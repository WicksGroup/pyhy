"""Command line interface to run multiple Hyades simulations.

Example:
    The following line would run all the .inf files in the `./data/inf` folder::

    $ python run_hyades.py

"""
import os
import argparse
from tools.hyades_runner import batch_run_hyades


description = '''Command line interface to run multiple Hyades simulations.

Runs a Hyades simulation for each .inf in the --inf_dir folder, runs PPF2NCDF
to make the .cdf output file for every simulation, moves all files from a run
to a folder named after the .inf.

Example:
    The following line would run all .inf files in the directory ./data/inf
    $ python run_hyades.py
'''
epilog = '''
                      ___      _  _      
                     | _ \_  _| || |_  _ 
                     |  _/ || | __ | || |
                     |_|  \_, |_||_|\_, |
                          |__/      |__/ 
               Developed by the Wicks Lab at JHU
'''

parser = argparse.ArgumentParser(prog='run_hyades.py',
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 description=description,
                                 epilog=epilog
                                 )

parser.add_argument('-in', '--inf_dir', type=str, default='./data/inf/',
                    help='Name of the directory containing the .inf files. (default: %(default)s)')
parser.add_argument('-out', '--out_dir', type=str, default='./data/',
                    help='Folder where data will end up. (default: %(default)s)')
parser.add_argument('-r', '--run', action='store_true', default=False,
                    help='Toggle to disable inf filename preview and run Hyades without confirmation. (default: False)')
args = parser.parse_args()

# inf_dir = args.inf_dir or './data/inf'
# out_dir = args.out_dir or './data/'

if args.run:  # Input request to run Hyades without confirmation
    batch_run_hyades(args.inf_dir, args.out_dir)
else:  # Print all .inf names and ask for confirmation
    inf_files = [f for f in os.listdir(args.inf_dir) if f.endswith('.inf')]
    print(f'Found {len(inf_files)} .inf files in {args.inf_dir!r}: {", ".join(inf_files)}.')
    answer = input(f'Start all {len(inf_files)} Hyades simulations? [y/n]: ')
    if answer == 'y':
        batch_run_hyades(args.inf_dir, args.out_dir)
    else:
        print('Did not run any Hyades simulations.')
