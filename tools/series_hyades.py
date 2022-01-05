"""A script to run benchmark Hyades times against parallel runs

"""
import os
import time


def run_hyades(inf):
    """A simple function to run Hyades in series for several inf files"""
    command = f'hyades {inf}'
    with open('series_log.txt', 'a') as f:
        f.write(f'Starting {command}\n')
    start = time.time()
    os.system(command)
    stop = time.time()
    with open('series_log.txt', 'a') as f:
        f.write(f'Finished {command} in {stop - start:.4f} seconds\n')


if __name__ == '__main__':
    path = '../data/inf'
    inf_files = sorted([f for f in os.listdir(path) if f.endswith('.inf')])
    with open('series_log.txt', 'w') as f:
        f.write(f'Logging for series_hyades.py\n')
        f.write(f'Running {len(inf_files)} Hyades simulations in series.\n')
        f.write(f'inf files are: {", ".join(inf_files)}\n')
    start_time = time.time()
    for inf in inf_files:
        run_hyades(os.path.join(path, inf))
    end_time = time.time()
    with open('series_log.txt', 'a') as f:
        f.write(f'Entire script took {end_time - start_time:.4f} seconds.')
