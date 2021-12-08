"""Convert netcdf (.cdf) files to more friendly excel format

Todo:
    * Figure out why excel throws an error when I first try to open these notebooks
      error does not break the excel notebook, just throws a pop up that doesn't appear to change any data
"""
import pandas as pd
import numpy as np
from tools.hyades_reader import HyadesOutput


def format_for_excel(hyades, label, coordinate_system='Lagrangian'):
    """Format a HyadesOutput as a pandas DataFrame for write_excel

    Format of the excel sheet is the following:
    Name (Units) |     x0    |     x1    | ... |    xM
        time0    | var(0, 0) | var(0, 1) | ... | var(0, M)
        time1    | var(1, 0) | var(1, 1) | ... | var(1, M)
        ...      |    ...    |    ...    | ... |    ...
        timeN    | var(N, 0) | var(N, 1) | ... | var(N, M)

    Note:
        All x coordinates are in microns.
        All times are in nanoseconds.

    Args:
        hyades (HyadesOutput): An instance of the HyadesOutput class
        label (string): Description of variable and units to put in excel file
        coordinate_system (string, optional): Coordinate system to use along top row of DataFrame

    Returns:
        df (pandas.DataFrame): HyadesOutput.output matrix with time on the left column and x on the top row

    """
    if coordinate_system.lower() == 'lagrangian':
        top = hyades.x[0, :].reshape((1, len(hyades.x[0, :])))
    elif coordinate_system.lower() == 'eulerian':
        top = np.array([range(len(hyades.x[0, :]))])
    right_matrix = np.concatenate((top, hyades.output), axis=0)
    time = np.insert(hyades.time, 0, np.NaN)
    time = time.reshape((len(time), 1))
    result = np.concatenate((time, right_matrix), axis=1)
    df = pd.DataFrame(result)
    df.iloc[0, 0] = label
    
    return df


def write_excel(cdf_path, excel_fname, variables, coordinate_system='Lagrangian'):
    """Write an excel spreadsheet with a page for each variable.

    Args:
        cdf_path (string): Path to the .cdf
        excel_fname (string): name of the excel file to write to
        variables (list): List of abbreviated variable names to include in excel file
        coordinate_system:
    Return:
        excel_fname (string): Name of the written excel file
    """
    coordinate_system = coordinate_system.lower()
    if not (coordinate_system == 'lagrangian' or coordinate_system == 'eulerian'):
        raise ValueError(f'Unrecognized coordinate system: {coordinate_system!r}. Options are Lagrangian or Eulerian')

    if not excel_fname.endswith('.xlsx'):
        excel_fname += '.xlsx'

    writer = pd.ExcelWriter(excel_fname, mode='w')
    for var in variables:
        if var == 'R':
            label, units = 'Eulerian Coordinates', '(um)'
        elif var == 'Pres':
            label, units = 'Pressure', '(GPa)'
        elif var == 'Rho':
            label, units = 'Density', '(g/cc)'
        elif var == 'U':
            label, units = 'Particle Velocity', '(km/s)'
        elif var == 'Te':
            label, units = 'Electron Temperature', '(K)'
        elif var == 'Ti':
            label, units = 'Ion Temperature', '(K)'
        elif var == 'Tr':
            label, units = 'Radiation Temperature', '(K)'
        hyades = HyadesOutput(cdf_path, var)
        df = format_for_excel(hyades, f'{label} {units}', coordinate_system=coordinate_system)
        df.to_excel(writer, sheet_name=label, header=False, index=False)

    # Add a sheet to the excel file specifying the data format
    if coordinate_system == 'lagrangian':
        format_dict = {'Variable Name (Units)': ['Time (ns) 0', 'Time 1', '...', 'Time N'],
                       'Lagrangian Position 0 (um)': ['Var (0, 0)', 'Var (1, 0)', '...', 'Var (N, 0)'],
                       'x 1': ['Var (0, 1)', 'Var (1, 1)', '...', 'Var (N, 1)'],
                       '...': ['...', '...', '...', '...'],
                       'x M': ['Var (0, M)', 'Var (1, M)', '...', 'Var (N, M)']}
    elif coordinate_system == 'eulerian':
        format_dict = {'Variable Name (Units)': ['Time (ns) 0', 'Time 1', '...', 'Time N'],
                       '0)': ['Var (0, 0)', 'Var (1, 0)', '...', 'Var (N, 0)'],
                       '1': ['Var (0, 1)', 'Var (1, 1)', '...', 'Var (N, 1)'],
                       '...': ['...', '...', '...', '...'],
                       'M': ['Var (0, M)', 'Var (1, M)', '...', 'Var (N, M)']}
    df_format = pd.DataFrame.from_dict(format_dict, dtype=str)
    df_format.to_excel(writer, sheet_name='Data Format', header=True, index=False)

    writer.save()
    writer.close()
    print(f'Saved: {excel_fname}')

    return excel_fname