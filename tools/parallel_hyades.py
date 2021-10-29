"""An attempt to run Hyades simulations in parallel. Does **not** neatly format the output like hyades_runner.py"""
import multiprocessing
import os


def run_parallel_hyades(inf_files):
    """Runs hyades simulations in parallel.

    Todo:
        * Test this on the lab iMac to explore effects of parallel simulations

    Note:
        THIS SCRIPT HAS NOT BEEN THOROUGHLY TESTED. UNSURE OF EFFECTS OF PARALLEL SIMULATIONS.
        We are not sure this script actually saves any time. Further testing is needed.
    """

    assert(len(inf_files)) < 5, 'Due to a lack of testing, the number of parallel simulations is limited to 4 or fewer.'

    def execute(file):
        """Function to run Hyades for the parallel command"""
        os.system(f'hyades {file}')

    print(f'There are {len(inf_files)} inf files: {", ".join(inf_files)}.')
    answer = input(f'Attempt to run all {len(inf_files)} in parallel? [y/n]')
    if answer == 'y':
        parallel_runs = tuple([os.path.join(inf_dir, f) for f in inf_files])
        num_processes = len(parallel_runs)
        process_pool = multiprocessing.Pool(processes=num_processes)
        process_pool.map(execute, parallel_runs)
    else:
        print('Not running any Hyades simulations.')


if __name__ == '__main__':
    inf_dir = '../data/inf'
    inf_files = [os.path.join(inf_dir, f) for f in os.listdir(inf_dir) if f.endswith('.inf')]
    run_parallel_hyades(inf_files)
