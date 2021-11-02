"""The newest version of how to control the optimizer with a configuration file and configparser

Todo:
    - implement shock velocity
    - implement restart from. I don't think this should make a new folder
"""
import os
import sys
sys.path.append('../')
import argparse
import configparser
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate, optimize
from optimizer.hyop_class import HyadesOptimizer, ResolutionError
from optimizer.hyop_functions import calculate_laser_pressure
from graphics import optimizer_graphics


def run_optimizer(run_name):
    """Starts an optimization to fit Hyades simulated Velocity to experimental VISAR.

    This function is mostly formatting the variables specified in the .cfg to work with the Hyades Optimizer class.
    It also controls the resolution of the optimization using a for loop.

    Note:
        Assumes the Hyades Setup file, configuration file, and experimental data have already been formatted.
        The setup file must be named 'run_name_setup.inf', the configuration file must be named 'run_name.cfg',
        The experimental data name is specified in the configuration file, but is typically to be run_name.xlsx.
        The bounds of the optimization solution are always set to  >= 0.

    Args:
        run_name (string):

    Returns:
        sol (scipy.optimize.OptimizeResult): The solution to the optimization

    """
    run_path = f'./data/{run_name}'

    config_filename = os.path.join(run_path, f'{run_name}.cfg')
    config = configparser.ConfigParser()
    if not os.path.exists(config_filename):
        error_string = f'Could not find {run_name}.cfg in {run_path}.' \
                       f'\nContents of {run_path} are :{os.listdir(run_path)}'
        raise Exception(error_string)
    config.read(config_filename)

    # Get Setup config and initialize HyadesOptimizer
    delay = config.getfloat('Setup', 'delay',
                            fallback=0)
    use_shock_velocity = config.getboolean('Setup', 'use_shock_velocity',
                                           fallback=False)
    time = [float(i) for i in config.get('Setup', 'time').split(',')]
    pressure = [float(i) for i in config.get('Setup', 'pressure').split(',')]
    if len(time) == 3 and len(pressure) != 3:  # If time is in the format: start, stop, num
        time = [i for i in np.linspace(time[0], time[1], num=int(time[2]), endpoint=True)]
    hyop = HyadesOptimizer(run_name, time, pressure,
                           delay=delay, use_shock_velocity=use_shock_velocity)
    # Get experimental config and load experimental data into hyop instance
    experimental_filename = config.get('Experimental', 'filename',
                                       fallback=run_name)
    if experimental_filename == 'None':
        experimental_filename = run_name
    time_of_interest = config.get('Experimental', 'time_of_interest',
                                  fallback=None)
    if time_of_interest:
        time_of_interest = [float(i) for i in time_of_interest.split(',')]
    hyop.read_experimental_data(experimental_filename, time_of_interest=time_of_interest)
    # Optionally use laser ablation pressure as first pressure guess
    laser_spot_diameter = config.getfloat('Experimental', 'laser_spot_diameter',
                                          fallback=0)
    if laser_spot_diameter != 0:
        ablation_pressure, laser_log_message = calculate_laser_pressure(hyop, laser_spot_diameter)
        hyop.pres = ablation_pressure

    # Run a loop over each of the resolutions
    for resolution in (len(hyop.pres), 2*len(hyop.pres), 4*len(hyop.pres)):
        print('Current resolution: ', resolution)
        f = interpolate.interp1d(hyop.pres_time, hyop.pres)
        new_time = np.linspace(hyop.pres_time.min(), hyop.pres_time.max(), num=resolution)
        new_pres = f(new_time)
        hyop.pres_time = new_time
        hyop.pres = new_pres
        lb, ub = [0]*len(hyop.pres), [np.inf]*len(hyop.pres)
        bounds = optimize.Bounds(lb, ub, keep_feasible=True)
        jac = config.get('Optimization', 'jac',
                         fallback=None)
        if jac == 'None':
            jac = None
        try:
            sol = optimize.minimize(hyop.run, hyop.pres,
                                    method=config.get('Optimization', 'method'),
                                    jac=jac,
                                    tol=config.getfloat('Optimization', 'tol'),
                                    bounds=bounds,
                                    options={'disp': config.getboolean('Optimization', 'disp'),
                                             'maxfun': config.getint('Optimization', 'maxfun'),
                                             'eps': config.getfloat('Optimization', 'eps')
                                             }
                                    )
        except ResolutionError:
            print("INCREASING RESOLUTION")

    out_fname = os.path.join(hyop.path, f'{hyop.run_name}_solution.txt')
    with open(out_fname, 'w') as f:
        f.write(str(sol))

    return sol


description = '''A command line interface to run the optimizer and plot the output.'''
epilog = '''
                      ___      _  _      
                     | _ \_  _| || |_  _ 
                     |  _/ || | __ | || |
                     |_|  \_, |_||_|\_, |
                          |__/      |__/ 
               Developed by the Wicks Lab at JHU
'''

parser = argparse.ArgumentParser(prog='optimize_hyades.py',
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 description=description,
                                 epilog=epilog
                                 )
parser.add_argument('filename', type=str,
                    help='Name of the Hyades run to be optimized.')
parser.add_argument('-r', '--run', action='store_true',
                    help='Run the optimizer. Assumes experimental data, filename_setup.inf, '
                         'and filename.cfg are set up in the folder pyhy/data/filename.')
parser.add_argument('-b', '--best', action='store_true',
                    help='Plot the best velocity from a completed optimization, '
                         'experimental velocity, and pressure drive all on a single figure.')
parser.add_argument('-g', '--histogram', action='store_true',
                    help='Plot a pressure histogram of the best run from a completed optimization.')
parser.add_argument('-v', '--velocity', action='store_true',
                    help='Plot a comparison of the optimized and experimental velocities.')
args = parser.parse_args()
# End parser

if args.run:
    sol = run_optimizer(args.filename)

if args.best:
    fig, ax = optimizer_graphics.compare_velocities(args.filename)

if args.histogram:
    fig, ax = optimizer_graphics.best_histogram(args.filename)

if args.velocity:
    fig, ax = optimizer_graphics.iteration_velocities(args.filename)

plt.show()
