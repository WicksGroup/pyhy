'''
Connor Krill
July 11, 2019
Classes and Functions for hyades optimizer
'''

import os
import numpy as np
import scipy
import copy
import pandas as pd
from scipy import interpolate #, optimize
import shutil
import matplotlib.pyplot as plt
import re
import json
from hyades_output_reader import createOutput
#from hyades_runner import run_hyades, run_hyades_post
from hyop_class import hyadesOptimizer

from display_tabs import DisplayTabs



def useLaserPower(hyop, exp_file_name, laser_spot_diameter, debug=0):
    '''
    Estimate the initial pressure for hyop using the laser power in the experimental file
    '''
    df = pd.read_excel(exp_file_name)
    cols = df.columns
    time_column, velocity_column = cols[0], cols[1]
    laser_time_column, laser_power_column = cols[2], cols[3]
    laser_time = df[laser_time_column]
    laser_power = df[laser_power_column]
    laser_power.loc[laser_power < 0] = 0
    laser_spot_diameter = laser_spot_diameter / 1e4          # convert to centimeters
    spot_area = np.pi * (laser_spot_diameter / 2)**2         # pi * r^2
    laser_intensity = laser_power / spot_area
    if (hyop.materials[0]=='Diamond'):
        ablation_pressure = 42.0 * (laser_intensity ** 0.71) # diamond ablation pressure formula
        if debug==1:
            print('Using diamond ablation pressure formula')
    else:
        ablation_pressure = 46.5 * (laser_intensity ** 0.80) # CH ablation pressure formula. Ray said use this as default
        if debug==1:
            print('Using CH ablation pressure formula')
    f_laser = interpolate.interp1d(laser_time, ablation_pressure) # Interpolate ablation pressure onto time scale
    
    ###
    hyop.pres = f_laser(hyop.pres_time)
    laser_log_message = f'Estimated initial pressure using data from {os.path.basename(exp_file_name)!r}'
    ###
    if debug==1:
        fig, ax1 = plt.subplots()
        ax2 = ax1.twinx()
        ax1.plot(hyop.pres_time, hyop.pres,'r', label='Hyades Pressure')
        ax2.plot(laser_time, laser_power,'b', label='Laser Power')
        ax2.grid()
        plt.title('Hyades Pressure and Laser Power')
        ax1.legend(loc=2)
        ax2.legend(loc=4)
        plt.show()
    return hyop, laser_log_message



def restartFrom(restart_folder, time_for_pressure, debug=0):
    '''
    Set the intial pressure in hyop using a previous optimization run
    '''    
    last_char = restart_folder[-1]
    if last_char.isdigit():
        new_folder = f'{restart_folder[:-1]}{int(last_char) + 1}' # add one to the last digit
    else:
        new_folder = restart_folder + '2'
    if debug==1:
        print(f'NEW FOLDER: {new_folder}')
    
    if not os.path.isdir(f'../data/{new_folder}'):
        os.mkdir(f'../data/{new_folder}')
    
    for f in os.listdir(f'../data/{restart_folder}'):
        if f.endswith('.inf'):
            old_inf = f
            break
    if not 'old_inf' in locals():
        raise Exception(f'Did not find .inf in {restart_folder}')
    src = f'../data/{restart_folder}/{old_inf}'
    dest = f'../data/{new_folder}/{new_folder}_setup.inf'
    if debug==1:
        print(f'SOURCE, DESTINATION: {src}, {dest}')
    shutil.copy2(src, dest)    
    
    #OVERHAUL WITH JSON
    json_name = f'../data/{restart_folder}/{restart_folder}_optimization.json'
    with open(json_name) as f:
        json_data = json.load(f)
    
    previous_pres = json_data['best optimization']['pres']
    previous_pres_time = json_data['best optimization']['pres_time']

    f = interpolate.interp1d(previous_pres_time, previous_pres)
    new_pres = f(time_for_pressure)

    ###
    run_name = new_folder
    initial_pressure = new_pres
    hyop = hyadesOptimizer(run_name, time_for_pressure, initial_pressure)
    restart_log_message = f'Starting this optimization from {restart_folder}'
    ###

    plt.plot(previous_pres_time, previous_pres, 'o', label='old')
    plt.plot(time_for_pressure, new_pres,       '+', label='new')
    plt.setp(plt.gca(), title='New and Old Optimization Timing',
            xlabel='Time (ns)', ylabel='Pressure (GPa)')
    plt.legend()
    plt.show()
    
    return hyop, restart_log_message


def plotXrayPressure(path, direct_path=False, show_average=True):
    '''
    Create a two axis figure, the first axis is a pcolor X-t image of the pressure
    the second is the average pressure in the material_of_pressure over time
    '''
    if direct_path:
        hyades = createOutput(path, 'Pres')
    else:
        json_file = os.path.join(path, f'{os.path.basename(os.path.normpath(path))}_optimization.json')
        with open(json_file) as f:
            json_data = json.load(f)

        hyades_file = [f for f in os.listdir(path) if (json_data['best optimization']['name'] in f)
                                                   and os.path.isdir(os.path.join(path,f))]
        hyades_file = hyades_file[0]
        hyades = createOutput(os.path.join(path, hyades_file, hyades_file), 'Pres')
        
    if show_average:
        # Plot pressure as t-X pcolormesh
        fig, (ax1, ax2) = plt.subplots(figsize=(10,8), nrows=2, ncols=1, sharex=True)
        cmap = plt.cm.viridis #hot # plasma, inferno
        im = ax1.pcolormesh(hyades.time, hyades.X, hyades.output[:len(hyades.X),:], cmap=cmap)
        plt.subplots_adjust(hspace=0.1)

        # colorbar
        cb = fig.colorbar(im, ax=(ax1, ax2), orientation="horizontal",
                          pad=0, aspect=10, shrink=0.2, anchor=(0.02, 7.75))
        cb.set_label('Pressure (GPa)', color='w')
        cbytick_hyades = plt.getp(cb.ax.axes, 'xticklabels')
        plt.setp(cbytick_hyades, color='w')

        # hoizontal dashed lines for materials
        for mat in hyades.material_properties:
            distance = hyades.material_properties[mat]['startX']
            y = (hyades.material_properties[mat]['startX'] + hyades.material_properties[mat]['endX']) / 2
            ax1.axhline(distance, color='w', linestyle='dashed', linewidth=1)
            ax1.text(0.99 * ax2.get_xlim()[1], y, mat, fontsize=12, color='w', ha='right')

        for time in hyades.xray_probe_time:
            ax1.axvline(time, color='w', linestyle='dashed', linewidth=1)

        x = (hyades.xray_probe_time[1] + hyades.xray_probe_time[0]) / 2
        y = ax1.get_ylim()[1] * 0.85
        ax1.text(x, y, 'X-Ray\nWindow', color='w', ha='center')

        # Plot mean and standard deviation
        ix_dist = (hyades.material_properties[hyades.material_of_interest]['startMesh'],
                   hyades.material_properties[hyades.material_of_interest]['endMesh'])

        mean    = np.mean(hyades.output[ix_dist[0]:ix_dist[1], :], axis=0)
        std_dev = np.std(hyades.output[ix_dist[0]:ix_dist[1], :], axis=0) 
        ax2.plot(hyades.time, mean, label='Average')
        ax2.fill_between(hyades.time, mean+std_dev, mean-std_dev, alpha=0.25, label='Std Dev')
        for t in hyades.xray_probe_time:
            ax2.axvline(t, color='k', linestyle='dashed', linewidth=1)

        # final figure formatting
        ax1.set_title(f'{os.path.basename(path)} Pressure History')
        sz = 12
        ax1.set_ylabel('Lagranian Position (um)', fontsize=sz)
        ax2.set_title(f'Average Pressure in {hyades.material_of_interest}', fontsize=12)
        ax2.set_xlabel('Time (ns)', fontsize=sz)
        ax2.set_ylabel('Mean Pressure (GPa)', fontsize=sz)
        ax2.set_xlim(0, hyades.time.max())
        ax2.tick_params(axis='x', labelsize=sz)
        ax1.tick_params(axis='y', labelsize=sz)
        ax2.tick_params(axis='both', labelsize=sz)
        ax2.legend(loc=2, fontsize='medium')
        return fig, (ax1, ax2)
    else:
        # Plot pressure as t-X pcolormesh
        fig, ax1 = plt.subplots(figsize=(10,8))
        cmap = plt.cm.viridis #hot # plasma, inferno
        im = ax1.pcolormesh(hyades.time, hyades.X, hyades.output[:len(hyades.X),:], cmap=cmap)

        # colorbar
        cb = fig.colorbar(im, ax=ax1, )#orientation="horizontal",
                          #pad=0, aspect=10, shrink=0.2,)# anchor=(0.02, 7.75))
        cb.set_label('Pressure (GPa)', color='w')
        cbytick_hyades = plt.getp(cb.ax.axes, 'xticklabels')
        plt.setp(cbytick_hyades, color='w')

        # hoizontal dashed lines for materials
        for mat in hyades.material_properties:
            distance = hyades.material_properties[mat]['startX']
            y = (hyades.material_properties[mat]['startX'] + hyades.material_properties[mat]['endX']) / 2
            ax1.axhline(distance, color='w', linestyle='dashed', linewidth=1)
            ax1.text(0.99 * ax1.get_xlim()[1], y, mat, fontsize=12, color='w', ha='right')
        
        # final figure formatting
        ax1.set_title(f'{os.path.basename(path)} Pressure History',fontsize=18)
        sz = 12
        ax1.set_ylabel('Lagranian Position (um)', fontsize=sz)
        ax1.set_xlabel('Time (ns)', fontsize=sz)
        ax1.set_xlim(0, hyades.time.max())
        ax1.tick_params(axis='both', labelsize=sz)
        
        return fig, ax1
