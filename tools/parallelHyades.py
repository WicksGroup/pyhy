import multiprocessing
import os

# This block of code enables us to call the script from command line.                                                                                
def execute(file):
    os.system(f'hyades {file}')

# Creating the tuple of all the processes
all_files = ('data/inf/s77742_shock100.inf', 'data/inf/s77742_shock200.inf', 'data/inf/s77742_shock300.inf')
process_pool = multiprocessing.Pool(processes=3)
process_pool.map(execute, all_files)
