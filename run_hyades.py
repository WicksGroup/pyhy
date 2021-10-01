"""Command line interface to run Hyades.

Example:
    The following line would run all the .inf files in the `./data/inf` folder::

    $ python run_hyades.py

Todo:
    * Implement a feature to check if Hyades is available on the machine. I think
    https://stackoverflow.com/questions/11210104/check-if-a-program-exists-from-a-python-script
    has an answer

"""
import argparse
from tools.batchRunner import batch_run_hyades

parser = argparse.ArgumentParser(prog='run_hyades.py',
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 description='A command line interface to run Hyades.',
                                 epilog='''\
                      ___      _  _      
                     | _ \_  _| || |_  _ 
                     |  _/ || | __ | || |
                     |_|  \_, |_||_|\_, |
                          |__/      |__/ 
Developed by the Wicks' Lab at JHU.                                                   
'''
                                 )

parser.add_argument('-in', '--inf_dir', type=str, default='./data/inf/',
                    help='Name of the directory containing the .inf files. (default: %(default)s)')
parser.add_argument('-out', '--out_dir', type=str, default='./data/',
                    help='Folder where data will end up. (default: %(default)s)')

args = parser.parse_args()

inf_dir = args.inf_dir or './data/inf'
out_dir = args.out_dir or './data/'

batch_run_hyades(inf_dir, out_dir)

'''
try:
    subprocess.call(["wget", "your", "parameters", "here"])
except FileNotFoundError:
    # handle file not found error.

import shutil
program = 'Python'
location = shutil.which(program)
if location:
    print('You have ' + program)
else:
print('Sorry, could not find ' + program)
'''