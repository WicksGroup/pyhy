"""Functions to run Hyades, convert the .otf to .cdf, and organize the output files into folders.

Todo:
    * Confirm this works with the inf_GUI.py
    * Confirm the logging is working
"""
import os
import time
import shutil
import logging
import subprocess

from tools.excel_writer import write_excel


def run_hyades(inf_name):
    """Runs a single Hyades simulation.

    Args:
        inf_name (string): Name of the .inf

    Returns:
        log_string (string): Status and details of Hyades simulation

    """
    t0 = time.time()
    command = ['hyades', inf_name]
    sp = subprocess.run(command)
    t1 = time.time()
    file_extensions = ('.otf', '.ppf', '.tmf')
    run_name = os.path.basename(os.path.splitext(inf_name)[0])
    found_all = all([run_name + ext in os.listdir(os.path.dirname(inf_name))
                     for ext in file_extensions])
    if found_all and sp.returncode == 0:
        log_string = f'Completed Hyades simulation of {os.path.basename(inf_name)} in {t1 - t0:.2f} seconds.'
    else:
        log_string = f'Failed to run Hyades simulation of {os.path.basename(inf_name)}.'

    return log_string


def otf2cdf(otf_name):
    """Runs the PPF2NCDF command to convert Hyades output (.otf) to a netcdf (.cdf) file

    Args:
        otf_name (string): Name of the .otf (should match name of .inf)

    Returns:
        log_string (string): status of the PPF2NCDF command

    """
    cmd = ['PPF2NCDF', os.path.splitext(otf_name)[0]]
    sp = subprocess.run(cmd)
    run_name = os.path.basename(os.path.splitext(otf_name)[0])
    found = run_name + '.cdf' in os.listdir(os.path.dirname(otf_name))
    if found and sp.returncode == 0:
        log_string = 'Completed PPF2NCDF.'
    else:
        log_string = 'Failed PPF2NCDF.'

    return log_string


def batch_run_hyades(inf_dir, out_dir, excel_variables=[]):
    """Runs Hyades simulations of many .inf files and packages each output into its own folder.

    Args:
        inf_dir (string): Name of the directory containing .inf files
        out_dir (string): Destination directory where all the data will end up
        excel_variables (list, optional): List of abbreviated variable names to copy to excel file

    Returns:
        None

    """
    inf_files = [f for f in os.listdir(inf_dir) if f.endswith('.inf')]
    if len(inf_files) == 0:  # if there are no inf files in the inf_directory
        raise ValueError(f'Did not find any .inf files in {inf_dir}')

    if inf_dir.startswith('./'):  # Hyades doe not work with ./ prepended on directories
        inf_dir = inf_dir[2:]

    # Set up a logging file
    filename = 'hyades.log'
    log_format = '%(asctime)s %(levelname)s:%(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    logging.basicConfig(filename=filename, format=log_format, datefmt=date_format, level=logging.DEBUG)

    for inf in sorted(inf_files):
        print(f'Starting Hyades {inf}')
        abs_path = os.path.join(inf_dir, inf)
        # Run Hyades
        log_note = run_hyades(abs_path)
        # Run PPF2NCDF to create .cdf file and add note to log
        log_note += otf2cdf(abs_path) + ' '

        # Optionally convert .cdf as a human-readable excel file
        if excel_variables:
            excel_filename = os.path.join(abs_path, os.path.splitext(inf)[0])
            write_excel(abs_path, excel_filename, excel_variables)
            log_note += f' Saved {", ".join(excel_variables)} to excel file.'
        logging.info(log_note)

        # Create new directory in out_dir
        basename = os.path.splitext(inf)[0]
        new_dir = os.path.join(out_dir, basename)
        os.mkdir(new_dir)
        # Move all files with the same name as the .inf to the new directory
        for f in os.listdir(inf_dir):
            if os.path.splitext(f)[0] == basename:
                source = os.path.join(inf_dir, f)
                destination = os.path.join(new_dir, f)
                shutil.move(source, destination)

    return log_note
