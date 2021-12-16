"""An attempt to run Hyades simulations in parallel. Does **not** neatly format the output like hyades_runner.py"""
import multiprocessing
import os


def run_parallel_hyades(inf_names):
    """Runs hyades simulations in parallel.

    Todo:
        * Test this on the lab iMac to explore effects of parallel simulations
    """

    def execute(file):
        """Function to run Hyades for the parallel command"""
        os.system(f'hyades {file}')

    num_processes = len(inf_names)
    process_pool = multiprocessing.Pool(processes=num_processes)
    process_pool.map(execute, inf_names)


if __name__ == '__main__':
    inf_dir = '../data/inf'
    inf_files = [os.path.join(inf_dir, f) for f in os.listdir(inf_dir) if f.endswith('.inf')]
    run_parallel_hyades(tuple(inf_files))
