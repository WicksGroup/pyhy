import os
import re
import json
import copy
import scipy
import logging
import numpy as np
import pandas as pd
from scipy import interpolate
from tools.hyades_reader import HyadesOutput, ShockVelocity
from tools import hyades_runner


class HyadesOptimizer:
    """Class used to fit a Hyades simulated velocity to experimentally measured VISAR

    Massive class that will be fed into the SciPy optimization function to fit hyades data to experiment.

    Note:
        See HyadesOptimizer.run(), the last function, for a summary of how this class works

    """
    
    def __init__(self, run_name, t0, x0, delay=0, use_shock_velocity=False):
        """Constructor method to initialize Hyades parameters and simulation hyperparameters

        Args:
            run_name (string): Name of the folder and setup file for the optimization
            t0 (list): timing of the initial pressure
            x0 (list): initial guess of the pressure drive
            use_shock_velocity (bool, optional): Toggle to optimize shock velocity instead of particle velocity
        """
        self.run_name = run_name
        self.pres_time = np.array(t0)
        self.pres = np.array(x0)
        self.delay = delay
        self.use_shock_velocity = use_shock_velocity
        
        self.exp_file = ''
        self.path = f'./data/{self.run_name}/'
        self.inf_path = os.path.abspath('./data/inf/')
        
        self.iter_count = 0
        self.material_of_interest = None
        self.shock_moi = None
        self.residual = np.array(())
        self.exp_data = np.array(())  # Experimental variables must be updated once before optimization is run
        self.exp_time = np.array(())
        
        inf_filename = os.path.join(self.path, f'{self.run_name}_setup.inf')
        with open(inf_filename) as fh:
            contents = fh.read()
        pattern = '\[\w+!?\$?\]'
        self.materials = re.findall(pattern, contents)

    def read_experimental_data(self, exp_file_name, time_of_interest=None):
        """Load the experimental data into the class

        Assigns self.exp_file, self.exp_time, and self.exp_data

        Note:
            This function should only be called once before the optimizer is run
        Args:
            exp_file_name (string): Name of the excel sheet containing the experimental data
            time_of_interest (tuple): Tuple of (start_time, stop_time) where the residual is calculated.
                                      Defaults to using all times in the experimental data
        """

        if not exp_file_name.endswith('.xlsx'):
            exp_file_name += '.xlsx'
        self.exp_file = f'./data/experimental/{exp_file_name}'
        df = pd.read_excel(self.exp_file, sheet_name=0)
        df.loc[df[df.columns[1]] < 0.1, df.columns[1]] = 0  # set velocities below 0.1 to 0

        velocity_time = df[df.columns[0]]
        velocity = df[df.columns[1]]
        # Excel adds NaN rows to Velocity Time and Velocity if the other columns in the sheet are longer
        # This drops all rows from velocity and time if the first instance of NaN till the end of the file is NaN
        index_of_first_nan = min(np.where(velocity.isna())[0])
        if all(velocity_time[index_of_first_nan:].isna()):
            velocity_time = velocity_time[:index_of_first_nan]
            velocity = velocity[:index_of_first_nan]

        if any(velocity.isna()) or any(velocity_time.isna()):
            raise ValueError(f'Found NaN (Not-a-Number) in experimental velocity file {self.exp_file}')
        f_velocity = scipy.interpolate.interp1d(velocity_time, velocity)

        if (not time_of_interest) or (time_of_interest == 'None'):
            time_of_interest = (min(velocity_time), max(velocity_time))

        self.exp_time = np.linspace(time_of_interest[0], time_of_interest[1], num=50)
        self.exp_data = f_velocity(self.exp_time)

    def update_variables(self, var_vec):
        """Take apart the single vector from the optimizer into the component parts

        Note:
            If we ever optimize more than one variable at a time this will be useful.
        """
        self.pres = var_vec

    def write_inf(self):
        """Write an .inf file based on the current class parameters

        This function does *not* create an .inf from scratch. It looks for a file named {run_name}_setup.inf
        and replaces the keyword TV_PRES with the current pressure drive.
        The new file is named {run_name}_{iter_count}.inf
        Uses PCHIP interpolation to improve resolution on the Pressure drive
        """
        # Interpolate the Pressure drive onto a high resolution time
        pchip = interpolate.PchipInterpolator(self.pres_time, self.pres)
        xs = np.linspace(np.ceil(self.pres_time.min()), np.floor(self.pres_time.max()), num=100)
        ys = pchip(xs)
        mask = np.where(ys < 0)
        ys[mask] = 0
        self.xs = xs
        self.ys = ys
        pres_scale = 1.0e10
        pres_lines = [f'tv {t * 1e-9:.6e} {v * pres_scale:.6e}'
                      for t, v in zip(self.xs, self.ys)]
        
        # Read Setup .inf file
        setup_inf = f'{self.run_name}_setup.inf'
        with open(os.path.join(self.path, setup_inf)) as f:
            contents = f.read()
        new = copy.deepcopy(contents)
        
        assert 'TV_PRES' in new, f'Did not find "TV_PRES" in {new}'
        new = new.replace('TV_PRES', '\n'.join(pres_lines))

        out_fname = setup_inf.replace('setup', str(self.iter_count).zfill(3))
        with open(os.path.join(self.inf_path, out_fname), 'w') as f:
            f.write(new)       

    def simulate_inf(self):
        """Run the Hyades simulation of the last .inf written by this class"""

        hyades_runner.batch_run_hyades(self.inf_path, self.path, quiet=True)

        # Setup a logging file
        filename = './optimizer/hyop.log'
        log_format = '%(asctime)s %(levelname)s:%(message)s'
        datefmt = '%Y-%m-%d %H:%M:%S'
        logging.basicConfig(filename=filename, format=log_format, datefmt=datefmt, level=logging.DEBUG)
        log = f'Run Name: {self.run_name} Iteration: {str(self.iter_count).zfill(3)} Residual: {self.residual}'
        logging.info(log)

    def calculate_residual(self):
        """Calculates the sum of least squares residual between the most recent Hyades simulation and experiment"""
        hyades_file = f'{self.run_name}_{str(self.iter_count).zfill(3)}'
        hyades_path = os.path.join(self.path, hyades_file, hyades_file)
        hyades_U = HyadesOutput(hyades_path, 'U')
                         
        if self.material_of_interest is None:
            self.material_of_interest = hyades_U.moi
        if (self.shock_moi is None) and ('shock_moi' in vars(hyades_U)):
            self.shock_moi = hyades_U.shock_moi

        if self.use_shock_velocity:
            """
            This is broken and I know it Oct 13th 2021
            """
            # adjust the shock velocity timing so the shock MOI lines up with experimental data
            # calculate residual on the overlap between the adjusted time and experimental data
            # ie calculate from (beginning of experimental time) to (end of exp_time or shock leaves shock MOI)
            shock = ShockVelocity(hyades_path, 'Shock velocity')
            time_start = shock.material_properties[hyades_U.shock_MOI]['timeIn']
            time_stop = shock.material_properties[hyades_U.shock_MOI]['timeOut']
            delay = self.exp_time.min() - time_start
            self.delay = delay
            adjusted_shock_time = shock.time + delay
            # interpolate from the beginning of exp_time
            # to the end of exp_time or the shock leaves the sample, whichever comes first
            f_Us = interpolate.interp1d(adjusted_shock_time, shock.Us)
            max_interp_time = min(self.exp_time.max(), time_stop)
            interp_time = np.linspace(self.exp_time.min(), max_interp_time, num=50)
            interp_hyades = f_Us(interp_time)
            self.residual = sum(np.square(self.exp_data - interp_hyades))
        else:
            if self.material_of_interest is None:
                self.material_of_interest = hyades_U.moi
            idx = hyades_U.layers[self.material_of_interest]['Mesh Stop'] - 1
            x = hyades_U.time - self.delay
            y = hyades_U.output[:, idx]
            if any(np.isnan(y)):
                raise ValueError(f'Found NaN in HyadesOuput {hyades_path}')
            f_hyades_U = scipy.interpolate.interp1d(x, y)  # Interpolate Hyades data onto experimental time
            interp_hyades = f_hyades_U(self.exp_time)
            if any(np.isnan(interp_hyades)):
                raise ValueError(f'Found NaN in interpolated HyadesOutput {hyades_path}')
            self.residual = sum(np.square(self.exp_data - interp_hyades))

    def save_json(self):
        """Save the input pressure, timing, and residual to a JSON file"""
        json_name = os.path.join(self.path, f'{self.run_name}_optimization.json')

        hyades_file = f'{self.run_name}_{str(self.iter_count).zfill(3)}'
        hyades_path = os.path.join(self.path, hyades_file, hyades_file)
        hyades = HyadesOutput(hyades_path, 'U')
        i = hyades.layers[hyades.moi]['Mesh Stop'] - 1

        # Format the data from this iteration
        iteration_data = {'time pressure': list(self.pres_time),
                          'pressure': list(self.pres),
                          'time velocity': list(hyades.time),
                          'velocity': list(hyades.output[:, i]),
                          'residual': self.residual,
                          }
        # Initialize json file if it doesn't exist, else load in json file
        if not os.path.exists(json_name):
            parameters = {'delay': self.delay,
                          'time of interest': [self.exp_time.min(), self.exp_time.max()],
                          'moi': self.material_of_interest,
                          'shock moi': self.shock_moi,
                          'path': self.path
                          }
            experimental = {'time': list(self.exp_time),
                            'velocity': list(self.exp_data),
                            'file': self.exp_file
                            }

            json_data = {'run name': self.run_name,
                         'data path': self.path,
                         'best': iteration_data,
                         'experimental': experimental,
                         'iterations': {},
                         'parameters': parameters
                         }
            json_data['best']['number'] = str(self.iter_count).zfill(3)
        else:
            with open(json_name) as f:
                json_data = json.load(f)

        # Check if this run has a lower residual than the best residual
        if self.residual < json_data['best']['residual']:
            json_data['best'] = iteration_data
            json_data['best']['number'] = str(self.iter_count).zfill(3)

        # Write this data to the run
        json_data['iterations'][str(self.iter_count).zfill(3)] = iteration_data
        with open(json_name, "w") as write_file:
            json.dump(json_data, write_file)

        # Remove unnecessary hyades folders
        directories = [f for f in os.listdir(self.path) if os.path.isdir(os.path.join(self.path, f))]
        for directory in directories:
            if ('000' in directory) or (json_data['best']['number'] in directory) or (
                    str(self.iter_count).zfill(3) in directory):
                continue  # do nothing, we want to keep these folders
            else:
                delete_extensions = ('.cdf', '.ppf', '.tmf', '.inf', '.otf')
                for file in os.listdir(os.path.join(self.path, directory)):
                    check_extension = [file.endswith(ext) for ext in delete_extensions]
                    if any(check_extension):
                        os.remove(os.path.join(self.path, directory, file))
                try:
                    os.rmdir(os.path.join(self.path, directory))
                except:
                    print(f'Failed to delete the directory {directory} - Check remaining contents:')
                    print(os.listdir(os.path.join(self.path, directory)))

    def run(self, var_vec):
        """The function called by the SciPy optimization routine.

        Outline of this function:
            1. Updates Hyades Pressure drive based on var_vec
            2. Writes new .inf file
            3. Simulates new .inf file
            4. Calculates residual between simulation and experimental data
            5. Saves pressure drive, Hyades velocity, and residual to a json file
            6. Increases iteration count by 1

        Note:
            To speed up optimization routines that use numerical derivatives, this function will raise the exception
            ResolutionError if both the number of points on the pressure drive is small and the residual is small.
            The thrown ResolutionError is caught by optimize.py and used to restart the optimization routine
            with a higher resolution on the pressure drive. The conditions for the size of the resolution drive and
            residual can be adjusted, but throwing a first error at resolution < 50 and number of pressure points <= 10,
            then a second ResolutionError at resolution < 20 and number of pressure points <= 20 has qualitatively
            worked well for the L-BFGS-B method within scipy.optimize.minimize.

        Args:
            var_vec (numpy array): The pressure drive of the Hyades simulation

        Returns:
            residual (float): The sum of least squares residual between Hyades and experimental velocity
        """
        self.update_variables(var_vec)
        self.write_inf()
        self.simulate_inf()
        self.calculate_residual()
        self.save_json()

        pretty_pressure = ', '.join([f'{p:.2f}' for p in self.pres])
        print(f'Iteration: {str(self.iter_count).zfill(3)} Residual: {self.residual:.4f} Pressure: {pretty_pressure}')

        self.iter_count += 1
        if (self.residual < 50) and (len(self.pres_time) <= 10):
            print('RESIDUAL < 50 and RESOLUTION <= 10')
            raise ResolutionError('CONDITIONS MET - INCREASING RESOLUTION')
        elif (self.residual < 15) and (len(self.pres_time) <= 20):
            print('RESIDUAL < 20 and RESOLUTION <= 20')
            raise ResolutionError('CONDITIONS MET - INCREASING RESOLUTION')

        return self.residual


class ResolutionError(Exception):
    """Custom error used to stop the optimization and restart it at a higher resolution"""
    pass
