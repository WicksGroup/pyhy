"""Script to launch the optimization
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate, optimize
from optimizer.hyop_class import HyadesOptimizer
from optimizer.hyop_class import ResolutionError

# from display_tabs import DisplayTabs
plt.style.use('ggplot')


def hyopfunction(exp_file_name, time_of_interest, run_name):
    """

    Args:note
        exp_file_name:
        time_of_interest:
        run_name:
    """
    # Setup
    restart_from_this_run = ''  # Optional name of the run to restart from
    use_shock_velocity = False  # bool, Toggle to use Shock Velocity instead of Particle Velocity
    use_laser_power = 0         # Float, 0 means do not use laser drive, otherwise pull Laser Power from experiment
    delay = 0                   # Time (ns) to subtract from Hyades to align drives

    initial_pressure = (0, 100, 100, 100, 100, 100, 100, 100)
    initial_time = (0, 20)
    # End setup

    if len(initial_time) == 2:
        time_for_pressure = np.linspace(initial_time[0], initial_time[1], num=len(initial_pressure), endpoint=True)
    else:
        time_for_pressure = initial_time

    hyop = HyadesOptimizer(run_name, time_for_pressure, initial_pressure,
                           delay=delay, use_shock_velocity=use_shock_velocity)

    hyop.read_experimental_data(exp_file_name, time_of_interest=None)

    # if restart_from_this_run:
    #     hyop, restart_log_message = restart_from(restart_from_this_run, time_for_pressure)
    #     laser_log_message = ''
    # elif use_laser_power:
    #     hyop = HyadesOptimizer(run_name, time_for_pressure, initial_pressure)
    #     # hyop, laser_log_message = use_laser_power(hyop, '../data/experimental/s22262_Us.xlsx',laser_spot_diameter, debug=1)
    #     restart_log_message = ''
    # else:
    #     hyop = HyadesOptimizer(run_name, time_for_pressure, initial_pressure)
    #     laser_log_message, restart_log_message = '', ''
    #     print('Starting from scratch')
        
    print(f'Calculating the residual during {time_of_interest} ns, using a delay of {delay} ns on Hyades data.')
    hyop.read_experimental_data(exp_file_name, time_of_interest)
    hyop.delay = delay

    # Set optimization parameters
    optimization_algorithm = 'L-BFGS-B' 
    jac = None
    tol = 1
    options = {'disp': False, 'maxiter': 1000, 'eps': 10.0}  # eps is step size during jacobian approximation
    # Set up logging file
    # filename = 'hyop.log'
    # log_format = '%(asctime)s %(levelname)s:%(message)s'
    # datefmt = '%Y-%m-%d %H:%M:%S'
    # logging.basicConfig(filename=filename, format=log_format, datefmt=datefmt, level=logging.DEBUG)
    # log_message = f'Started optimization {hyop.run_name} '
    # log_message += f'method: {optimization_algorithm}, jac: {jac}, tol:{tol}, bounds: ({lb}, {ub}), options: {options}'
    # logging.info(log_message)
    #if laser_log_message:   logging.info(laser_log_message)
    #if restart_log_message: logging.info(restart_log_message)

    for resolution in (len(hyop.pres), 2*len(hyop.pres), 4*len(hyop.pres)):
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


experimental_filename = sys.argv[1]
time_of_interest = (float(sys.argv[2]), float(sys.argv[3]))
run_name = sys.argv[4]
hyopfunction(experimental_filename, time_of_interest, run_name)
