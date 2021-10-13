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
# from display_tabs import DisplayTabs


class HyadesOptimizer:
    """Class used to fit a Hyades simulation to experimental data

    Todo:
        * The shock velocity class needs to know the time in and out of materials
        * set up the logging
        * Reformat the json saving to include more parameters and the velocity
        * update the documenation on all the functions

    Massive class that will be fed into the SciPy optimization function to fit hyades data to experiment.
    This version does not match the temperature profile.

    Note:
        See HyadesOptimizer.run(), the last function, for a summary of how this class works

    """
    
    def __init__(self, run_name, t0, x0, use_shock_velocity=False, initial_tabs=None):
        """Constructor method to initialize Hyades parameters and simulation hyperparameters

        Args:
            run_name:
            t0:
            x0:
            use_shock_velocity:
            initial_tabs:
        """
        self.run_name = run_name
        self.pres_time = np.array(t0)
        self.pres = np.array(x0)
        self.delay = 0.0
        self.use_shock_velocity = use_shock_velocity
        
        self.exp_file = ''
        self.path = f'../data/{self.run_name}/'
        self.inf_path = os.path.abspath('../data/inf/')
        
        self.iter_count = 0
        self.material_of_interest = None
        self.shock_MOI = None
        self.residual = np.array(())
        self.exp_data = np.array(())  # updated before optimization is run
        self.exp_time = np.array(())
        
        inf_filename = os.path.join(self.path, f'{self.run_name}_setup.inf')
        print(f'Contents of {self.path}  are {os.listdir(self.path)}')
        with open(inf_filename) as fh:
            contents = fh.read()
        pattern = '\[\w+!?\$?\]'
        self.materials = re.findall(pattern, contents)

    # def __initTabs__(self, initial_tabs=None):
    #     self.plot1 = DynamicUpdate("t-up Optim vs Real")

    def read_experimental_data(self, exp_file_name, time_of_interest, delay):
        """Load the experimental data into the class

        Assigns self.exp_file, self.exp_time, and self.exp_data

        Note:
            This function should only be called once before the optimizer is run
        Args:
            exp_file_name (string): Name of the excel sheet containing the experimental data
            time_of_interest (tuple): Tuple of (start_time, stop_time) where the residual is calculated
            delay (float): A time delay, in nanoseconds, to shift the experimental data so it lines up with Hyades
        """
        if not exp_file_name.endswith('.xlsx'):
            exp_file_name += '.xlsx'
        self.exp_file = f'../data/experimental/{exp_file_name}'
        df = pd.read_excel(self.exp_file)
        df.loc[df[df.columns[1]] < 0.1, df.columns[1]] = 0  # set velocities below 0.1 to 0
        velocity_time = df[df.columns[0]]
        velocity = df[df.columns[1]]
        f_velocity = scipy.interpolate.interp1d(velocity_time, velocity)
        self.exp_time = np.linspace(time_of_interest[0], time_of_interest[1], num=50)
        self.exp_data = f_velocity(self.exp_time)

        # Add delay to experimental time
        # self.delay = delay
        # self.exp_time += self.delay

    def update_variables(self, var_vec):
        """Take apart the single vector from the optimizer into the component parts

        If we ever optimize more than one variable at a time this will be useful.
        """
        self.pres = var_vec

    def write_inf(self):
        """Write an .inf file based on the current class parameters

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
        
        # Write new .inf file for this iteration
        # try:
        #     os.makedirs(self.inf_path + f'/{self.run_name}')
        # except:
        #     print(f'A folder for {self.run_name} already exists.')
        out_fname = setup_inf.replace('setup', str(self.iter_count).zfill(3))
        with open(os.path.join(self.inf_path, out_fname), 'w') as f:
            f.write(new)       

    def simulate_inf(self):
        """Run the Hyades simulation of the last .inf written by this class"""

        hyades_runner.batch_run_hyades(self.inf_path, self.path, quiet=True)

        # Setup a logging file
        # filename = 'hyop.log'
        # log_format = '%(asctime)s %(levelname)s:%(message)s'
        # datefmt = '%Y-%m-%d %H:%M:%S'
        # logging.basicConfig(filename=filename,
        #                     format=log_format, datefmt=datefmt, level=logging.DEBUG)
        # assert filename in os.listdir(os.getcwd()), f'{filename!r} not in current directory {os.getcwd()!r}'
        # logging.info(f'Run Name: {self.run_name} Iteration: {str(self.iter_count).zfill(3)} Residual: {self.residual:.4f}')

    def calculate_residual(self):
        """Calculates the sum of least squares residual between the most recent Hyades simulation and experiment"""
        hyades_file = f'{self.run_name}_{str(self.iter_count).zfill(3)}'
        hyades_path = os.path.join(self.path, hyades_file, hyades_file)
        hyades_U = HyadesOutput(hyades_path, 'U')  # outside the if/else so can be passed into myTabs
                         
        if self.material_of_interest is None:
            self.material_of_interest = hyades_U.moi
        if (self.shock_MOI is None) and ('shock_MOI' in vars(hyades_U)):
            self.shockMOI = hyades_U.shock_moi
                        
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
            max_interp_time = min(self.exp_time.max(), time_stop)# + delay)
            interp_time = np.linspace(self.exp_time.min(), max_interp_time, num=50)
            interp_hyades = f_Us(interp_time)
            self.residual = sum(np.square(self.exp_data - interp_hyades))
                         
            plot_time = adjusted_shock_time
            plot_velocity = shock.Us
        else:
            if self.material_of_interest is None:
                self.material_of_interest = hyades_U.moi
            idx = hyades_U.layers[self.material_of_interest]['Mesh Stop'] - 1
            x = hyades_U.time - self.delay
            y = hyades_U.output[:, idx]
            # print(x, y)
            f_hyades_U = scipy.interpolate.interp1d(x, y)  # Interpolate Hyades data onto experimental time
            interp_hyades = f_hyades_U(self.exp_time)
            self.residual = sum(np.square(self.exp_data - interp_hyades))
            plot_time = x
            plot_velocity = y
        # print('Hyades time limits:', hyades_U.time.min(), hyades_U.time.max())
        # self.myTabs.update_velocity_output(self.exp_time, self.exp_data,
        #                                    plot_time, plot_velocity,
        #                                    hyades_path, 0.0,
        #                                    use_shock_velocity=self.use_shock_velocity)
        # self.plot1.on_running(plot_time, plot_velocity, self.exp_time, self.exp_data)
        # self.plot1.figure.savefig(f'{self.run_name}_{self.iter_count}.png')

    def save_json(self):
        """Save the input pressure, timing, and residual to a JSON file"""
        json_name = os.path.join(self.path, f'{self.run_name}_optimization.json')
        # format the data from this run
        data = {'pres_time': list(self.pres_time),
                'pres': list(self.pres),
                'residual': self.residual,
                'delay': self.delay
                }
        # Initialize json file if not in current directory, else load in json file
        if not os.path.basename(json_name) in os.listdir(self.path):
            json_data = {'iterations': {},
                         'experimental': None,
                         'best optimization': data,
                         'run name': self.run_name}
            json_data['best optimization']['name'] = str(self.iter_count).zfill(3)
            experimental = {'time': list(self.exp_time),
                            'velocity': list(self.exp_data),
                            'file': self.exp_file
                            }
            json_data['experimental'] = experimental
        else:
            with open(json_name) as f:
                json_data = json.load(f)
        # Check if this run has a lower residual than the best residual
        if self.residual < json_data['best optimization']['residual']:
            json_data['best optimization'] = data
            json_data['best optimization']['name'] = str(self.iter_count).zfill(3)

        # Write this data to the run
        json_data['iterations'][str(self.iter_count).zfill(3)] = data
        with open(json_name, "w") as write_file:
            json.dump(json_data, write_file)

        # Remove unnecessary hyades folders
        directories = [f for f in os.listdir(self.path) if os.path.isdir(os.path.join(self.path, f))]
        for directory in directories:
            if ('000' in directory) or (json_data['best optimization']['name'] in directory) or (
                    str(self.iter_count).zfill(3) in directory):
                continue  # do nothing, we want to keep these folders
            else:
                delete_extensions = ('U.dat', 'Pres.dat', 'Te.dat', 'Rho.dat', 'Tr.dat', 'Ti.dat', 'sd1.dat',
                                     '.cdf', '.ppf', '.tmf', '.inf', '.otf')
                for file in os.listdir(os.path.join(self.path, directory)):
                    check_extension = [file.endswith(ext) for ext in delete_extensions]
                    if any(check_extension):
                        os.remove(os.path.join(self.path, directory, file))
                try:
                    os.rmdir(os.path.join(self.path, directory))
                except:
                    print(f'Failed to delete the directory {directory} - Check remaining contents')
                    print(os.listdir(os.path.join(self.path, directory)))

    def run(self, var_vec):
        """The function called by the SciPy optimization routine.

        1. Updates Hyades Pressure drive based on var_vec
        2. Writes new .inf file
        3. Simulates new .inf file
        4. Calculates residual between simulation and experimental data
        5. Saves Pressure drive and residual to a json file
        6. Increases iteration count by 1

        Args:
            var_vec (numpy array): The pressure drive of the Hyades simulation

        Returns:

        """
        self.update_variables(var_vec)
        self.write_inf()
        self.simulate_inf()
        self.calculate_residual()
        self.save_json()

        print(f'Iteration: {str(self.iter_count).zfill(3)} Residual: {self.residual:.4f} Pressure: {self.pres}')

        # self.myTabs.update_tab_info(str(self.iter_count).zfill(3), self.residual, self.pres)
        # self.myTabs.update_pressure_input(self.pres_time, self.pres, self.xs, self.ys)
        # self.myTabs.update_residual(self.residual)
                         
        self.iter_count += 1
        if (self.residual < 30) and (len(self.pres_time) <= 10):
            print('RESIDUAL < 30 and RESOLUTION <= 10')
            raise ResolutionError('CONDITIONS MET - INCREASING RESOLUTION')
        elif (self.residual < 15) and (len(self.pres_time) <= 20):
            print('RESIDUAL < 15 and RESOLUTION <= 20')
            raise ResolutionError('CONDITIONS MET - INCREASING RESOLUTION')

        return self.residual


class ResolutionError(Exception):
    """Custom error used to stop the optimization and restart it at a higher resolution"""
    pass



# import matplotlib.pyplot as plt
# import random
# plt.ion()
# class DynamicUpdate():
#     def __init__(self, name):
#         #Set up plot
#         self.figure, self.ax = plt.subplots()
#         self.figure.suptitle(name)
#         self.lines, = self.ax.plot([], [])
#         self.line2, = self.ax.plot([], [])
#         # Autoscale on unknown axis and known lims on the other
#         self.ax.set_autoscaley_on(True)
#         # self.ax.set_xlim(self.min_x, self.max_x)
#         # Other stuff
#         self.ax.grid()
#
#     def on_running(self, xdata, ydata, xdata2=[], ydata2=[]):
#         # Update data (with the new _and_ the old points)
#         self.lines.set_xdata(xdata)
#         self.lines.set_ydata(ydata)
#         if xdata2 != [] and ydata2 != []:
#             self.line2.set_xdata(xdata2)
#             self.line2.set_ydata(ydata2)
#         # Need both of these in order to rescale
#         self.ax.relim()
#         self.ax.autoscale_view()
#         # We need to draw *and* flush
#         self.figure.canvas.draw()
#         self.figure.canvas.flush_events()
