"""Functions for the HyadesOptimizer class.

use_laser_power and restart_from are both used during the setup of an optimization, not during.
plot_xray_pressure is a function to handle some of the graphics during an optimization.

"""
import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import interpolate
from optimizer.hyop_class import HyadesOptimizer
from tools.hyades_reader import HyadesOutput


def calculate_laser_pressure(hyop, laser_spot_diameter, debug=0):
    """Estimate the initial pressure for hyop using the laser power in the experimental file.

    Pressure is estimated using either the Diamond or CH (plastic) laser ablation pressure formula.
    If the first material in the Hyades .inf is Diamond, the Diamond formula is used.
    Otherwise the plastic formula is used.

    Args:
        hyop (HyadesOptimizer): Instance of the HyOp class to store calculated laser drive
        laser_spot_diameter (float): diameter of the laser spot size, in millimeters
        debug (int, optional): Flag used to display additional data and plots

    Returns:
        ablation_pressure (Numpy Array), laser_log_message (string)

    """
    df = pd.read_excel(hyop.exp_file)
    cols = df.columns
    time_column, velocity_column = cols[0], cols[1]
    laser_time_column, laser_power_column = cols[2], cols[3]
    laser_time = df[laser_time_column]
    laser_power = df[laser_power_column]
    laser_power.loc[laser_power < 0] = 0
    laser_spot_diameter = laser_spot_diameter / 1e4  # convert to centimeters
    spot_area = np.pi * (laser_spot_diameter / 2)**2  # pi * radius^2
    laser_intensity = laser_power / spot_area

    if hyop.materials[0] == 'Diamond':  # Use Diamond ablation pressure formula
        ablation_pressure = 42.0 * (laser_intensity ** 0.71)
        if debug >= 1:
            print('Using diamond ablation pressure formula')
    else:  # Use plastic ablation pressure formula
        ablation_pressure = 46.5 * (laser_intensity ** 0.80)
        if debug >= 1:
            print('Using CH ablation pressure formula')
    f_laser = interpolate.interp1d(laser_time, ablation_pressure)  # Interpolate ablation pressure onto time scale

    ablation_pressure = f_laser(hyop.pres_time)
    laser_log_message = f'Estimated initial pressure using data from {os.path.basename(hyop.exp_file)}'

    if debug >= 1:
        fig, ax1 = plt.subplots()
        ax2 = ax1.twinx()
        ax1.plot(hyop.pres_time, hyop.pres, 'r', label='Hyades Pressure')
        ax2.plot(laser_time, laser_power, 'b', label='Laser Power')
        ax2.grid()
        plt.title('Hyades Pressure and Laser Power')
        ax1.legend(loc=2)
        ax2.legend(loc=4)
        plt.show()

    return ablation_pressure, laser_log_message


def restart_from(restart_folder, time_for_pressure, debug=0):
    """Set the initial pressure in HyOp using a previous optimization run

    Args:
        restart_folder (string): Name of the previously run Hyades optimization
        time_for_pressure (list): Timing of the initial pressure. The pressure is pulled from the old optimization
        debug (int, optional): Flag to display extra data and plots

    Returns:
        HyOp (HyadesOptimizer), restart_log_message (string)

    """
    # Load previous optimization data from json
    json_name = f'../data/{restart_folder}/{restart_folder}_optimization.json'
    with open(json_name) as f:
        json_data = json.load(f)
    previous_pres = json_data['best']['pressure']
    previous_pres_time = json_data['best']['time pressure']
    f = interpolate.interp1d(previous_pres_time, previous_pres, 'Cubic')
    new_pressure = f(time_for_pressure)

    run_name = os.path.basename(restart_folder)
    last_iteration = max([int(n) for n in json_data['iterations'].keys()])
    hyop = HyadesOptimizer(run_name, time_for_pressure, new_pressure)
    hyop.iter_count = last_iteration + 1
    hyop.delay = json_data['parameters']['delay']

    restart_log_message = f'Starting this optimization from {restart_folder}. Starting at iteration {hyop.iter_count}.'

    if debug >= 1:  # Optional plot to compare old and new pressures
        plt.plot(previous_pres_time, previous_pres, 'o', label='Old')
        plt.plot(time_for_pressure, new_pressure, 'x', label='New')
        plt.setp(plt.gca(), title='New and Old Optimization Timing',
                 xlabel='Time (ns)', ylabel='Pressure (GPa)')
        plt.legend()
        plt.show()
    
    return hyop, restart_log_message


def plot_xray_pressure(path, show_average=True):
    """Plot the pressure as an XT Diagram and the average pressure in the material of interest

    Formatted for display_tabs.py.

    Args:
        path (string): Path to the Hyades cdf
        show_average (bool, optional): Toggle to show the average pressure in the material of interest

    Returns:
        fig (matplotlib figure): figure containing the graphics
        ax_array (tuple): Tuple of (ax0, ax1) the two axis on the figure

    """
    hyades = HyadesOutput(path, 'Pres')

    if show_average:
        # Plot pressure as t-X pcolormesh
        fig, (ax1, ax2) = plt.subplots(figsize=(10, 8), nrows=2, ncols=1, sharex=True)
        cmap = plt.cm.inferno  # hot, plasma, inferno
        im = ax1.pcolormesh(hyades.time, hyades.x, hyades.output, cmap=cmap)
        plt.subplots_adjust(hspace=0.1)
        # Colorbar
        cb = fig.colorbar(im, ax=(ax1, ax2), orientation="horizontal",
                          pad=0, aspect=10, shrink=0.2, anchor=(0.02, 7.75))
        cb.set_label('Pressure (GPa)', color='w')
        cbytick_hyades = plt.getp(cb.ax.axes, 'xticklabels')
        plt.setp(cbytick_hyades, color='w')
        # Add vertical lines for material interfaces, horizontal lines for x-ray times
        for mat in hyades.layers:
            distance = hyades.layers[mat]['X Start']
            y = (hyades.layers[mat]['X Start'] + hyades.layers[mat]['X Stop']) / 2
            ax1.axvline(distance, color='w', linestyle='dashed', linewidth=1)
            ax1.text(0.99 * ax2.get_xlim()[1], y, mat, fontsize=12, color='w', ha='right')
        for time in hyades.xray_probe:
            ax1.axhline(time, color='w', linestyle='dashed', linewidth=1)
        x = hyades.x.max() * 0.02
        y = (hyades.xray_probe[1] + hyades.xray_probe[0]) / 2
        ax1.text(x, y, 'X-Ray Window', color='w', ha='left')
        # Plot mean and standard deviation
        ix_dist = (hyades.layers[hyades.moi]['Mesh Start'],
                   hyades.layers[hyades.moi]['Mesh Stop'])
        mean = np.mean(hyades.output[ix_dist[0]:ix_dist[1], :], axis=0)
        std_dev = np.std(hyades.output[ix_dist[0]:ix_dist[1], :], axis=0) 
        ax2.plot(hyades.time, mean, label='Average')
        ax2.fill_between(hyades.time, mean+std_dev, mean-std_dev, alpha=0.25, label='Std Dev')
        for t in hyades.xray_probe_time:
            ax2.axvline(t, color='k', linestyle='dashed', linewidth=1)

        # Final figure formatting
        ax1.set_title(f'{os.path.basename(path)} Pressure History')
        sz = 12
        ax1.set_ylabel('Lagranian Position (um)', fontsize=sz)
        ax2.set_title(f'Average Pressure in {hyades.moi}', fontsize=12)
        ax2.set_xlabel('Time (ns)', fontsize=sz)
        ax2.set_ylabel('Mean Pressure (GPa)', fontsize=sz)
        ax2.set_xlim(0, hyades.time.max())
        ax2.tick_params(axis='x', labelsize=sz)
        ax1.tick_params(axis='y', labelsize=sz)
        ax2.tick_params(axis='both', labelsize=sz)
        ax2.legend(loc=2, fontsize='medium')

        return fig, (ax1, ax2)

    else:
        # Plot pressure as x-t pcolormesh
        fig, ax1 = plt.subplots(figsize=(10, 8))
        cmap = plt.cm.viridis  # hot, plasma, inferno
        im = ax1.pcolormesh(hyades.time, hyades.x, hyades.output, cmap=cmap)

        cb = fig.colorbar(im, ax=ax1)
        cb.set_label('Pressure (GPa)', color='w')
        cbytick_hyades = plt.getp(cb.ax.axes, 'xticklabels')
        plt.setp(cbytick_hyades, color='w')

        # Add vertical dashed lines for material interfaces
        for mat in hyades.layers:
            distance = hyades.layers[mat]['X Start']
            y = (hyades.layers[mat]['X Start'] + hyades.layers[mat]['X Stop']) / 2
            ax1.axvline(distance, color='w', linestyle='dashed', linewidth=1)
            ax1.text(0.99 * ax1.get_xlim()[1], y, mat, fontsize=12, color='w', ha='right')
        
        # Final figure formatting
        ax1.set_title(f'{os.path.basename(path)} Pressure History', fontsize=18)
        sz = 12
        ax1.set_ylabel('Lagrangian Position (um)', fontsize=sz)
        ax1.set_xlabel('Time (ns)', fontsize=sz)
        ax1.set_xlim(0, hyades.time.max())
        ax1.tick_params(axis='both', labelsize=sz)
        
        return fig, ax1
