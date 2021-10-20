"""Command line interface to run the Hyades Optimizer.

This script will likely be a huge, gnarly mess.

Things to control:
    - Run Name
    - Experimental File Name (if not specified, use run_name.xlsx  in /data/experimental
    - Time of interest (if not specified, use ceiling(min(experiment_time)) and floor(max(experimental_time))
    - Initial Pressure, not needed if using laser power
    - Initial Time
    - Use shock velocity (bool) default False
    - Use laser power (float) the input here will be the laser spot diameter (in millimeters I think)

Structure:

If run_name exists as a previously run optimization
    restart from that run

confirm there is a setup file, experimental file, and folder for this optimization
if the setup file is in the /data/inf folder
    create a new folder for the run
    move the setup to the folder we just created

if use laser power
    get initial pressure and time
else
    set initial pressure and time

start the optimization
"""
import argparse
import os

description = '''A command line interface to fit Hyades simulated Velocities to VISAR data.'''
epilog = '''
                      ___      _  _      
                     | _ \_  _| || |_  _ 
                     |  _/ || | __ | || |
                     |_|  \_, |_||_|\_, |
                          |__/      |__/ 
               Developed by the Wicks Lab at JHU
'''

parser = argparse.ArgumentParser(prog='optimize_hyades_CLI.py',
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 description=description,
                                 epilog=epilog
                                 )

parser.add_argument('setup', type=str,
                    help='Name of the setup file. Does not require "_setup.inf"')
parser.add_argument('-x', '--experiment',
                    help='Name of the experimental data file.\n'
                         'Assumed to be in ./data/experimental\n'
                         '(default: Name of the setup file)')
parser.add_argument('-p', '--Pressure', nargs='+',
                    help='Initial Pressure (GPa) drive.\n'
                         'Format A: List of Pressures EX: 0 10 30 50 80 100 110'
                         'Format B: constant num_points EX: 100 8'
                         'Format B sets the initial number of Pressure and Time points with num_points')
parser.add_argument('-t', '--time', nargs='+',
                    help='Initial timing (ns) of the Pressure drive.\n'
                         'Format A: List of times EX: 1 2 3 4.6 5.3 7.0 10\n'
                         'Format B: Start Stop EX: 0 20\n'
                         'Format B will have the same number of points as the pressure vector, endpoints included')
parser.add_argument('-r', '--residual', nargs='+',
                    help='Time window for residual calculation.\n'
                         'Format: "-t start stop" EX: "-t 3 16.4"\n'
                         '(default: min and max of experimental time)')
parser.add_argument('-l', '--laser', type=float,
                    help='Laser spot diameter (millimeter).')
parser.add_argument('-k', '--shock', action='store_true',
                    help='Toggle to use Shock Velocity instead of Particle Velocity.')

'''
minimal working example
python optimize_hyades_CLI.py s77742 --pressure 100 8 --time 0 20

really ugly big example
python optimize_hyades_CLI.py s77742 --pressure 0 10 20 30 40 50 60 70 --time 0 1 2 3 4 5 6 7 8 

'''

args = parser.parse_args()
