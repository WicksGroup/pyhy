'''
Connor Krill
July 11, 2019
Classes and Functions for hyades optimizer
'''

import os
import numpy as np
import scipy
import copy
import logging
import pandas as pd
from scipy import interpolate, optimize
import shutil
import matplotlib.pyplot as plt
import re
import json
from hyades_output_reader import createOutput
from hyades_runner import batchRunHyades, runHyadesPostProcess, runHyades
#from display_tabs import DisplayTabs


class hyadesOptimizer:
    '''
    Massive class that will be fed into the scipy optimizer to fit hyades data to experiment.
    This version does not match the temperature profile.
    See hyadesOptimizer.run(), the last function, for a summary of how this class works
    '''
    
    def __init__(self, run_name, t0, x0, use_shock_velocity=False, initial_tabs=None):
        
        self.run_name  = run_name
        self.pres_time = np.array(t0)
        self.pres      = np.array(x0)
        self.delay     = 0.0
        self.use_shock_velocity = use_shock_velocity
        
        self.exp_file = ''
        self.path     = f'../data/{self.run_name}/'
        self.inf_path = os.path.abspath('../data/inf/')
        
        self.iter_count = 0
        self.material_of_interest = None # Can be int or string
        self.shock_MOI = None
        self.post_variables = ('Pres', 'Te', 'Rho', 'U')
        self.residual = np.array(())
        self.exp_data = np.array(()) # updated before optimization is run
        self.exp_time = np.array(())
        
        inf_filename = os.path.join(self.path, f'{self.run_name}_setup.inf')
        with open(inf_filename) as fh:
            contents = fh.read()
        self.materials = re.findall('(?<=\[)(.*?)(?=\])', contents)
        
        
    def __initTabs__(self, initial_tabs=None):
        self.plot1 = DynamicUpdate("t-up Optim vs Real")

    def updateVariables(self, var_vec):
        '''
        Take apart the single vector from the optimizer into the component parts
        '''
        self.pres = var_vec
            
            
    def saveObj(self):
        '''
        Save only the input pressure, timing, and residual to a JSON
        '''
        json_name = os.path.join(self.path, f'{self.run_name}_optimization.json')
        
        # format the data from this run
        data = {'pres_time':list(self.pres_time),
                'pres':list(self.pres),
                'residual': self.residual,
                'delay': self.delay
                }
        
        # initialize json file if not in current directory, else load in json file
        if not os.path.basename(json_name) in os.listdir(self.path):
            json_data = {'iterations'       :{},
                         'experimental'     :None,
                         'best optimization':None,
                         'run name'         :self.run_name}
            json_data['best optimization'] = data
            json_data['best optimization']['name'] = str(self.iter_count).zfill(3)
            experimental = {'time': list(self.exp_time),
                            'velocity': list(self.exp_data),
                            'file': self.exp_file
                           }
            json_data['experimental'] = experimental
            
        else:
            with open(json_name) as f:
                json_data = json.load(f)
        # check if this run has a lower residual than the best residual
        if self.residual < json_data['best optimization']['residual']:
            json_data['best optimization'] = data
            json_data['best optimization']['name'] = str(self.iter_count).zfill(3)
        
        # write this data to the run
        json_data['iterations'][str(self.iter_count).zfill(3)] = data
        with open(json_name, "w") as write_file:
            json.dump(json_data, write_file)

        # remove unneccessary hyades folders
        directories = [f for f in os.listdir(self.path) if os.path.isdir(os.path.join(self.path, f))]
        for directory in directories:
            if ('000' in directory) or (json_data['best optimization']['name'] in directory) or (str(self.iter_count).zfill(3) in directory):
                continue # do nothing, we want to keep these folders
            else:
                delete_extensions = ('U.dat', 'Pres.dat', 'Te.dat', 'Rho.dat', 'Tr.dat', 'Ti.dat', 'sd1.dat',
                                     '.ppf', '.tmf', '.inf', '.otf')
                for file in os.listdir(os.path.join(self.path, directory)):
                    check_extension = [file.endswith(ext) for ext in delete_extensions]
                    if any(check_extension):
                        os.remove(os.path.join(self.path, directory, file))
                try:
                    os.rmdir(os.path.join(self.path, directory))
                except:
                    print(f'Failed to delete the directory {directory} - Check remaining contents')
                    print(os.listdir(os.path.join(self.path, directory)))
                
    
    
    def writeInf(self):
        '''
        Write an .inf file based on the current class parameters.
        PCHIP interpolation between optimizer variables and .inf file  
        ''' 
        pchip = interpolate.PchipInterpolator(self.pres_time, self.pres)
        xs = np.linspace(np.ceil(self.pres_time.min()), np.floor(self.pres_time.max()),
                         num=100)
        ys = pchip(xs)
        mask = np.where(ys < 0)
        ys[mask] = 0
        self.xs, self.ys = xs, ys
        pres_scale = 1.0e9
        pres_lines = [f'tv {t * 1e-9:.6e} {v * pres_scale:.6e}'
                      for t, v in zip(self.xs, self.ys)]
        
        # Read setup file
        setup_inf = f'{self.run_name}_setup.inf'
        with open(os.path.join(self.path, setup_inf)) as fh:
            contents = fh.read()
        new = copy.deepcopy( contents )
        
        assert 'TV_PRES' in new, f'Did not find "TV_PRES" in {new}'
        new = new.replace('TV_PRES', '\n'.join(pres_lines))
        
        # Write new file
        try:
            os.makedirs(self.inf_path+f'\{self.run_name}')
        except:
            print("path exists")
        out_fname = setup_inf.replace('setup', str(self.iter_count).zfill(3))
        with open(os.path.join(self.inf_path+f'\{self.run_name}', out_fname), 'w') as f:
            f.write(new)       
        
    
    def simulateInf(self):
        '''
        Run the hyades simulation on the .inf most recently written by this class
        '''
        inf_path = self.inf_path
        final_destination = self.path
        print(inf_path,final_destination)
        batchRunHyades(inf_path+f'\{self.run_name}', final_destination, copy_data_to_excel=False, debug=2)

    ###
#        # setup a logging file
#        filename   = 'hyop.log'
#        log_format = '%(asctime)s %(levelname)s:%(message)s'
#        datefmt    = '%Y-%m-%d %H:%M:%S'
#        logging.basicConfig(filename=filename,
#                            format=log_format, datefmt=datefmt, level=logging.DEBUG)
#        assert filename in os.listdir(os.getcwd()), f'{filename!r} not in current directory {os.getcwd()!r}'
#
#        old_dir = os.getcwd() # save the old directory in case I need it later
#        inf_files = []
#        for f in os.listdir(self.inf_path):
#            if ('setup' not in f) and (f.endswith('.inf')) and f.startswith(self.run_name):
#                inf_files.append(f[:-4])
#
#        for inf_name in inf_files:
#            t2complete = runHyades(self.inf_path, inf_name, self.path) # creates a new folder named "run_name"
#            logging.info(f'Completed HYADES run for {inf_name} in {round(t2complete,1)} seconds')
#            runHyadesPostProcess(os.path.join(inf_name, inf_name), self.post_variables)
#            logging.info(f'Completed post processing for {inf_name} variables: {", ".join(self.post_variables)}')
#
#            os.chdir(old_dir)
#            # move the folder and post processing to final_destination
#            print("MOVING", os.path.join(self.inf_path))
#            print("TO",  self.path)
#            shutil.move(os.path.join(self.inf_path, inf_name), self.path)

    
    def readExp(self, exp_file_name, time_of_interest, delay):
        '''
        Load the experimental data into the class for comparison
        Assign self.exp_file, self.exp_time, and self.exp_data
        This function should only be called once before the optimizer is run
        '''
        self.exp_file = f'../data/experimental/{exp_file_name}'
        df = pd.read_excel( self.exp_file )
        df.loc[df[df.columns[1]] < 0.1, df.columns[1]] = 0 # set velocities below 0.1 to 0
        velocity_time = df[df.columns[0]]
        velocity      = df[df.columns[1]]
        f_velocity    = scipy.interpolate.interp1d(velocity_time, velocity)
        self.exp_time = np.linspace(time_of_interest[0], time_of_interest[1], num=50)      
        self.exp_data = f_velocity(self.exp_time)
            
        # add delay to experimental time           
#        self.delay = delay
#        self.exp_time += self.delay

                         
    def calcResidual(self):
        '''
        Calculate the sum of squares resdiual between the experimental and simulated data
        '''
        hyades_file = f'{self.run_name}_{str(self.iter_count).zfill(3)}'
        hyades_path = os.path.join(self.path, hyades_file, hyades_file)
        hyades_U = createOutput(hyades_path, 'U') # outside the if/else so can be passed into myTabs
                         
        if self.material_of_interest is None:
            self.material_of_interset = hyades_U.material_of_interest
        if (self.shock_MOI is None) and ('shock_MOI' in vars(hyades_U)):
            self.shockMOI = hyades_U.shock_MOI
                        
        if self.use_shock_velocity:
            # adjust the shock velocity timing so the shock MOI lines up with experimental data
            # calculate residual on the overlap between the adjusted time and experimental data
            # ie calculate from (beginning of experimental time) to (end of exp_time or shock leaves shock MOI)
            shock = createOutput(hyades_path, 'Shock velocity')
            time_start = shock.material_properties[hyades_U.shock_MOI]['timeIn']
            time_stop  = shock.material_properties[hyades_U.shock_MOI]['timeOut']
            delay = self.exp_time.min() - time_start
            self.delay = delay
            adjusted_shock_time = shock.time + delay
            # interpolate from the beginning of exp_time
            # to the end of exp_time or the shock leaves the sample, whichever comes first
            f_Us = interpolate.interp1d(adjusted_shock_time, shock.Us)
            max_interp_time = min(self.exp_time.max(), time_stop)# + delay)
            interp_time = np.linspace(self.exp_time.min(), max_interp_time, num=50)
            interp_hyades = f_Us(interp_time)
            self.residual = sum( np.square(self.exp_data - interp_hyades) )
                         
            plot_time = adjusted_shock_time
            plot_velocity = shock.Us
        else:
            delay = self.delay
            if self.material_of_interest is None:
                self.material_of_interest = hyades_U.material_of_interest
            idx = hyades_U.material_properties[self.material_of_interest]['endMesh'] - 1
            x, y = hyades_U.time - self.delay, hyades_U.output[idx,:]
            print(x,y)
            f_hyades_U = scipy.interpolate.interp1d(x, y) # interpolation is just for residual calculation
            interp_hyades = f_hyades_U(self.exp_time)
            self.residual = sum( np.square(self.exp_data - interp_hyades) )
            plot_time = x
            plot_velocity = y
        print('Hyades time limits:', hyades_U.time.min(), hyades_U.time.max())
        #print('interpolated limits:', plot_time)
        #print('plot velocity:', plot_velocity)
        #self.myTabs.update_velocity_output(self.exp_time, self.exp_data,plot_time, plot_velocity, hyades_path, 0.0,use_shock_velocity=self.use_shock_velocity)
        self.plot1.on_running(plot_time,plot_velocity,self.exp_time,self.exp_data)
        self.plot1.figure.savefig(f'{self.run_name}_{self.iter_count}.png')
        
# def calcShockVelocity(self, hyades_path):
#        '''
#        Trying to translate the matlab ShockFrontFunction
#        '''
#        hyades_pres = createOutput(hyades_path, 'Pres')
#        hyades_Up   = createOutput(hyades_path, 'U')
#        hyades_rho  = createOutput(hyades_path, 'Rho')
#        start, stop   = 10, len(hyades_pres.time) # limits on the loop
#        threshold     = 10 # Value to cross to find the first value
#        offset_points = 10 # number of points to look backwards from
#        pressure          = np.zeros((stop-start))
#        density           = np.zeros((stop-start))
#        particle_velocity = np.zeros((stop-start))
#        time              = np.zeros((stop-start))
#        j = 0
#        for i in range(start, stop):
#            index = max(np.where(hyades_pres.output[:, i] > threshold)[0]) # last instance of the condition
#            pressure_slice = hyades_pres.output[index-offset_points:index+1, i]
#            pressure_index = np.argmax(pressure_slice) # index of the maximum wrt the length of the pressure slice
#            loc = pressure_index + index - offset_points
#
#            # update pressure, particle velocity, time, density
#            pressure[j]          = pressure_slice.max()
#            particle_velocity[j] = hyades_Up.output[loc, i]
#            time[j]              = hyades_rho.time[i]
#            density[j]           = hyades_rho.output[loc,0]
#            j += 1
#
#        shock_velocity = pressure / (density * particle_velocity)
#        return time, shock_velocity

                         
    def run(self, var_vec):
        '''
        The function handed to the scipy optimizer.
        Updates hyades temperature, pressure base on input
        Writes new .inf files
        Simulates new .inf files
        Calculates residual between experimental and hyades
        Pickles self into saved file
        Increases iter_count by 1
        '''           
        self.updateVariables(var_vec)
        self.writeInf()
        self.simulateInf()
        self.calcResidual()
        self.saveObj()
        
        #self.myTabs.update_tab_info(str(self.iter_count).zfill(3), self.residual, self.pres)
        #self.myTabs.update_pressure_input(self.pres_time, self.pres, self.xs, self.ys)
        #self.myTabs.update_residual(self.residual)
                         
        self.iter_count += 1
        if (self.residual < 30) and (len(self.pres_time)<=10):
            print('RESIDUAL < 30 and RESOLUTION <= 10')
            raise resolutionError('CONDITIONS MET - INCREASING RESOLUTION')
        elif (self.residual < 15) and (len(self.pres_time)<=20):
            print('RESIDUAL < 8 and RESOLUTION <= 20')
            raise resolutionError('CONDITIONS MET - INCREASING RESOLUTION')
                         
                         
        return self.residual
                         
class resolutionError(Exception):
    # catcher to increase resolution
    pass



import matplotlib.pyplot as plt
import random
plt.ion()
class DynamicUpdate():
    def __init__(self,name):
        #Set up plot
        self.figure, self.ax = plt.subplots()
        self.figure.suptitle(name)
        self.lines, = self.ax.plot([],[])
        self.line2, = self.ax.plot([],[])
        #Autoscale on unknown axis and known lims on the other
        self.ax.set_autoscaley_on(True)
        #self.ax.set_xlim(self.min_x, self.max_x)
        #Other stuff
        self.ax.grid()

    def on_running(self, xdata, ydata, xdata2=[],ydata2=[]):
        #Update data (with the new _and_ the old points)
        self.lines.set_xdata(xdata)
        self.lines.set_ydata(ydata)
        if xdata2!=[] and ydata2!=[]:
            self.line2.set_xdata(xdata2)
            self.line2.set_ydata(ydata2)
        #Need both of these in order to rescale
        self.ax.relim()
        self.ax.autoscale_view()
        #We need to draw *and* flush
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

        
                         
