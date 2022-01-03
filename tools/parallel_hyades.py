"""An attempt to run Hyades simulations in parallel. Does **not** neatly format the output like hyades_runner.py


todo: check if this works i think inf B is broken"""
import multiprocessing
import os
import time


def run_hyades(inf):
    """A simple function to run Hyades in series for several inf files"""
    command = f'hyades {inf} >> {os.path.splitext(inf)[0]}_progress.txt'
    print('Starting', command)
    start = time.time()
    os.system(command)
    stop = time.time()
    print(f'Finished {command} in {stop - start:.4f} seconds')


if __name__ == '__main__':
    inf_files = sorted([f for f in os.listdir('./') if f.endswith('.inf')])
    num_processes = len(inf_files)
    start_time = time.time()
    process_pool = multiprocessing.Pool(processes=num_processes)
    process_pool.map(run_hyades, inf_files)
    process_pool.close()
    end_time = time.time()
    print(f'Entire script took {end_time - start_time:.4f} seconds.')


