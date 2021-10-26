"""The newest version of how to control the optimizer with a configuration file and configparser

Todo:
    - add an argparser to run from command line
    - implement shock velocity
    - implement restart from. I don't think this should make a new folder
"""
import os
import sys
sys.path.append('../')
import argparse
import configparser
import numpy as np
from scipy import interpolate, optimize
from optimizer.hyop_class import HyadesOptimizer, ResolutionError
from optimizer.hyop_functions import calculate_laser_pressure


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
    run_path = f'../data/{run_name}'

    config_filename = os.path.join(run_path, f'{run_name}.cfg')
    config = configparser.ConfigParser()
    config.read(config_filename)

    # Get Setup config and initialize HyadesOptimizer
    delay = config.get('Setup', 'delay',
                       fallback=0)
    use_shock_velocity = config.get('Setup', 'use_shock_velocity',
                                    fallback=False)
    hyop = HyadesOptimizer(run_name, config.get('Setup', 'time'), config.get('Setup', 'Pressure'),
                           delay=delay, use_shock_velocity=use_shock_velocity)
    # Get experimental config and load experimental data into hyop instance
    experimental_filename = config.get('Experimental', 'filename',
                                       fallback=run_name)
    if not experimental_filename:
        experimental_filename = run_name
    time_of_interest = config.get('Experimental', 'time_of_interest',
                                  fallback=None)
    hyop.read_experimental_data(experimental_filename, time_of_interest=time_of_interest)
    # Optionally use laser ablation pressure as first pressure guess
    laser_spot_diameter = config.get('Experimental', 'laser_spot_diameter',
                                     fallback=0)
    if laser_spot_diameter != 0:
        ablation_pressure, laser_log_message = calculate_laser_pressure(hyop, laser_spot_diameter)
        hyop.pres = ablation_pressure

    # Run a loop over each of the resolutions
    for resolution in (len(hyop.pres), 2*len(hyop.pres), 3*len(hyop.pres)):
        print('Current resolution: ', resolution)
        f = interpolate.interp1d(hyop.pres_time, hyop.pres)
        new_time = np.linspace(hyop.pres_time.min(), hyop.pres_time.max(), num=resolution)
        new_pres = f(new_time)
        hyop.pres_time = new_time
        hyop.pres = new_pres
        lb, ub = [0]*len(hyop.pres), [np.inf]*len(hyop.pres)
        bounds = optimize.Bounds(lb, ub, keep_feasible=True)
        try:
            sol = optimize.minimize(hyop.run, hyop.pres,
                                    method=config.get('Optimization', 'method'),
                                    jac=config.get('Optimization', 'jac'),
                                    tol=config.get('Optimization', 'tol'),
                                    bounds=bounds,
                                    options=config.get('Optimization', 'options'))
        except ResolutionError:
            print("INCREASING RESOLUTION")

    out_fname = os.path.join(hyop.path, f'{hyop.run_name}_solution.txt')
    with open(out_fname, 'w') as f:
        f.write(str(sol))

    return sol


description = '''A command line interface to run the optimizer'''
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

args = parser.parse_args()
# End parser
if args.filename:
    sol = run_optimizer(args.filename)
    print(sol)
