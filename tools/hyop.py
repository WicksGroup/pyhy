import os
import sys
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import interpolate, optimize
from hyades_runner import runHyades, runHyadesPostProcess
from tools.hyop_class import HyadesOptimizer
from tools.hyop_class import ResolutionError
from tools.hyop_functions import useLaserPower, restartFrom, plotXrayPressure
#from display_tabs import DisplayTabs
plt.style.use('ggplot')


def hyopfunction(exp_file_name, time_of_interest, run_name):
    """

    Args:
        exp_file_name:
        time_of_interest:
        run_name:
    """
    delay = 5  # nanoseconds, does not matter for shock velocity

    use_shock_velocity = False  # True or False
    use_laser_power = False  # True or False
    laser_spot_diameter = 1100  # microns, only matters if use_laser_power=True

    number_of_points = 8  # generally use a small number to start, the optimizer will automatically increase this
    # initial_pressure only matters if NOT using laser power and NOT restarting
    initial_pressure = [0, 100, 100, 100, 100, 100, 100, 100]
    time_for_pressure = np.linspace(0, 20, num=number_of_points, endpoint=True)

    restart_from_this_run = ''  # leave blank if no restart
    assert number_of_points == len(initial_pressure), f'There must be {number_of_points} entries in initial_pressure'
    assert number_of_points == len(time_for_pressure), f'There must be {number_of_points} entries in time_for_pressure'

    if restart_from_this_run:
        hyop, restart_log_message = restartFrom(restart_from_this_run, time_for_pressure)
        laser_log_message = ''
    elif use_laser_power:
        hyop = HyadesOptimizer(run_name, time_for_pressure, initial_pressure)
    # hyop, laser_log_message = useLaserPower(hyop, '../data/experimental/s22262_Us.xlsx',laser_spot_diameter, debug=1)
        restart_log_message = ''
    else:
        hyop = HyadesOptimizer(run_name, time_for_pressure, initial_pressure)
        laser_log_message, restart_log_message = '', ''
        print('starting from scratch')
        
    if use_shock_velocity:
        print('Residual will be calculating using shock velocity')
        hyop.use_shock_velocity = use_shock_velocity
        
    print(time_of_interest, delay)
    hyop.read_experimental_data(exp_file_name, time_of_interest, delay)
    hyop.delay = delay
    # Set optimization parameters
    optimization_algorithm = 'L-BFGS-B' 
    jac = None
    tol = 0.0001
    lb, ub = [0]*len(hyop.pres), [np.inf]*len(hyop.pres)
    bounds = optimize.Bounds(lb, ub, keep_feasible=True),
    options = {'disp': False, 'maxiter': 100000, 'eps': 10.0}  # eps is step size during jacobian approximation
    # Set up logging file
    filename = 'hyop.log'
    log_format = '%(asctime)s %(levelname)s:%(message)s'
    datefmt = '%Y-%m-%d %H:%M:%S'
    logging.basicConfig(filename=filename, format=log_format, datefmt=datefmt, level=logging.DEBUG)
    log_message = f'Started optimization {hyop.run_name} '
    log_message += f'method: {optimization_algorithm}, jac: {jac}, tol:{tol}, bounds: ({lb}, {ub}), options: {options}'
    logging.info(log_message)
    #if laser_log_message:   logging.info(laser_log_message)
    #if restart_log_message: logging.info(restart_log_message)

    ### Resolutions
    # hyop.__initTabs__()

    for resolution in (len(hyop.pres), 2*len(hyop.pres), 4*len(hyop.pres)):
        print('Current resolution', resolution)
        f = interpolate.interp1d(hyop.pres_time, hyop.pres)
        new_time = np.linspace(hyop.pres_time.min(), hyop.pres_time.max(), num=resolution)
        new_pres = f(new_time)
        hyop.pres_time = new_time
        hyop.pres = new_pres
        initial_pressure = new_pres
        lb, ub = [0]*len(hyop.pres), [np.inf]*len(hyop.pres)
        bounds = optimize.Bounds(lb, ub, keep_feasible=True),
        try:
            sol = optimize.minimize(hyop.run, initial_pressure,
                                    method=optimization_algorithm,
                                    jac=jac, tol=tol,
                                    bounds=bounds,
                                    options=options)
        except ResolutionError:
            print("Increasing resolution from", resolution)
            
    print(sol)
    out_fname = os.path.join(hyop.path, f'{hyop.run_name}_solution.txt')
    with open(out_fname, 'w') as f:
        f.write(str(sol))


print(sys.argv)
experimental_filename = sys.argv[1]
time_of_interest = (float(sys.argv[2]), float(sys.argv[3]))
run_name = sys.argv[4]
hyopfunction(experimental_filename, time_of_interest, run_name)
