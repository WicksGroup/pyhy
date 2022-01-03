"""A script to run benchmark Hyades times against parallel runs

Todo:
    - confirm this works at all. I think my inf files are broken, check B
"""
import os
import time


def run_hyades(inf):
    """A simple function to run Hyades in series for several inf files"""
    command = f'hyades {inf} nano '
    print('Starting', command)
    start = time.time()
    os.system(command)
    stop = time.time()
    print(f'Finished {command} in {stop - start:.4f} seconds')


if __name__ == '__main__':
    inf_files = sorted([f for f in os.listdir('./') if f.endswith('.inf')])
    start_time = time.time()
    for inf in inf_files:
        run_hyades(inf)
    end_time = time.time()
    print(f'Entire script took {end_time - start_time:.4f} seconds.')
