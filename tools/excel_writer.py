'''
Connor Krill December 5th, 2018
Functions for converting the .dat files output from hyades to a coherent excel spreadsheet
'''

import pandas as pd
import numpy as np
from hyades_output_reader import createOutput
import os


def formatForExcel(obj, label):
    '''Format a hyades_output_reader output as a pandas Dataframe for write_excel'''
    top = obj.time.reshape( (len(obj.time),1) ) # time comes in as 1D needs to be 2D with one dimension length of 1
    left_bottom = obj.X.reshape( (len(obj.X),1) )
    right  = np.concatenate((top.T, obj.output[0:len(obj.X), :]), axis=0)
    left   = np.concatenate( (np.full([1,1], np.nan), left_bottom), axis=0) # NaN appended to beginning of X
    result = np.concatenate( (left, right), axis=1) # put the left as a vertical vector on the side of the right
    df = pd.DataFrame(result)
    df.loc[0,0] = label
    
    return df


def writeExcel(excel_fname, data_path, variables):
    '''Write an excel spreadsheet with a page for each variable'''
    if not excel_fname.endswith('.xlsx'):
        excel_fname += '.xlsx'
    writer = pd.ExcelWriter( excel_fname )
    for var in variables:
        if var=='Pres':  label, units = 'Pressure', '(GPa)'
        elif var=='Rho': label, units = 'Density', '(g/cc)'
        elif var=='U':   label, units = 'Particle Velocity', '(km/s)'
        elif var=='Te':  label, units = 'Electron Temperature', '(K)'
        elif var=='Ti':  label, units = 'Ion Temperature', '(K)'
        elif var=='Tr':  label, units = 'Radiation Temperature', '(K)'
        hyades = createOutput(data_path, var)
        df = formatForExcel(hyades, f'{label} {units}')
        df.to_excel(writer, sheet_name=label, header=False, index=False)
    writer.save()
    writer.close()
    print(f'Saved: {excel_fname}')
