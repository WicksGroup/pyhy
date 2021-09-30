"""Functions to run Hyades, convert the .otf to .cdf, and organize the output files into folders."""
import os
import subprocess
import shutil


def run_hyades(inf_name):
    """Runs a single Hyades simulation.

    Args:
        inf_name (string): Name of the .inf

    Returns:
        terminal output, terminal error message, terminal response code

    """
    cmd = f'hyades {inf_name}'
    sp = subprocess.Popen(cmd,
                          shell=True,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          universal_newlines=True)
    response_code = sp.wait()
    out, err = sp.communicate()

    return out, err, response_code


def otf2cdf(otf_name):
    """Runs the PPF2NCDF command to convert Hyades output (.otf) to a netcdf (.cdf) file

    Args:
        inf_name (string): Name of the .otf (should match name of .inf)

    Returns:
        terminal output, terminal error message, terminal response code

    """
    cmd = f'PP2NCDF {os.path.splitext(otf_name)[0]}'
    print(cmd)
    sp = subprocess.Popen(cmd,
                          shell=True,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          universal_newlines=True)
    response_code = sp.wait()
    out, err = sp.communicate()

    return out, err, response_code


def batch_run_hyades(inf_dir, out_dir):
    """Runs Hyades simulations of many .inf files and packages each output into its own folder.

    Args:
        inf_dir (string): Name of the directory containing .inf files
        out_dir (string): Destination directory where all the data will end up

    Returns:
        None

    """
    inf_files = [f for f in os.listdir(inf_dir) if f.endswith('.inf')]
    for inf in inf_files:
        print(f'Starting Hyades {inf}')
        abs_path = os.path.join(inf_dir, inf)

        # Run Hyades and post processor
        out, err, rc = run_hyades(abs_path)
        if err:
           raise Exception(f'Error from terminal while running "Hyades {abs_path}":\n{err}')
        out, err, rc = otf2cdf(abs_path)
        if err:
           raise Exception(f'Error from terminal while running "PPF2NCDF {abs_path}":\n{err}')

        # Create new directory in out_dir
        basename = os.path.splitext(inf)[0]
        new_dir = os.path.join(out_dir, basename)
        os.mkdir(new_dir)
        print(f'Made {new_dir}')

        # move all files with the same name as the .inf to the new directory
        for f in os.listdir(inf_dir):
            if os.path.splitext(f)[0] == basename:
                source = os.path.join(inf_dir, f)
                destination = os.path.join(new_dir, f)
                shutil.move(source, destination)
                print(f'moved {destination}')

    return None