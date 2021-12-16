"""A script to run benchmark Hyades times against parallel runs"""
import os


def run_series_hyades(inf_names):
    """A simple function to run Hyades in series for several inf files

    Note:
        This was designed as a benchmark to compare to parallel hyades runs. Not intended to be useful.

    Args:
        inf_names:

    Returns:

    """
    for inf in inf_names:
        command = f'hyades {inf}'
        os.system(command)


if __name__ == '__main__':
    inf_dir = '../data/inf'
    inf_files = [os.path.join(inf_dir, f) for f in os.listdir(inf_dir) if f.endswith('.inf')]
    run_series_hyades(inf_files)