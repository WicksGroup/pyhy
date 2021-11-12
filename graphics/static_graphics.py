"""Useful plots of Hyades inputs and outputs

Todo:
    - add option to plot in eulerian coordinates
"""
import sys
sys.path.append('../')
import os
import matplotlib
import matplotlib.pyplot as plt
plt.style.use('ggplot')
plt.rcParams['toolbar'] = 'toolmanager'
from matplotlib.backend_tools import ToolBase
import datetime
import numpy as np
import pandas as pd
from scipy.io import netcdf
from tools.hyades_reader import ShockVelocity, HyadesOutput


class SaveTools(ToolBase):
    """Matplotlib Tool to save the data on screen to a .csv"""
    default_keymap = 'd'
    description = 'Save data to a .csv'

    def __init__(self, *args, data_dictionary, header, filename, **kwargs):
        """Constructor method to initialize the tool

        Args:
            data_dictionary:
            header:
            filename:
        """
        self.data_dictionary = data_dictionary
        prefix = f'Data created using plot_shock_velocity in pyhy/graphics/static_graphics.py ' \
                 f'on {datetime.date.today().strftime("%Y-%m-%d")}\n'
        self.header = prefix + header
        if not self.header.endswith('\n'):
            self.header += '\n'
        self.filename = filename
        super().__init__(*args, **kwargs)

    def trigger(self, *args, **kwargs):
        """Function for the matplotlib button to save data on screen to csv

        Note:
            pandas.DataFrame can only initialize if every column is the same length.
            Since the velocity can be a different length than the other variables,
             the try except blocks attempts to sneak past the pandas.DataFrame limitation
             by continually appending data, which can handle varying lengths.
        """
        out_filename = self.get_filename()
        try:
            df = pd.DataFrame(self.data_dictionary)
        except ValueError as e:
            keys = list(self.data_dictionary.keys())
            first_key = keys[0]
            df = pd.DataFrame({first_key: list(self.data_dictionary[first_key])})
            print(first_key, type(self.data_dictionary[first_key]))
            for k in keys[1:]:
                print(k, len(self.data_dictionary[k]), self.data_dictionary[k][:10])
                additional_df = pd.DataFrame({k: list(self.data_dictionary[k])})
                df = pd.concat([df, additional_df], axis=1)

        with open(out_filename, 'w', newline='\n') as f:
            f.write(self.header)
            df.to_csv(f, index=False, float_format='%.4f')
        print('Saved ', out_filename)

    def get_filename(self):
        """Creates a new filename with a numerical extension to prevent writing over old data

        Returns:
            new_filename (string): The original filename with the lowest unused numerical extension
        """
        filename_with_extension = os.path.basename(self.filename)
        directory = os.path.dirname(self.filename)
        if filename_with_extension not in os.listdir(directory):
            return self.filename
        else:
            base_name, extension = os.path.splitext(filename_with_extension)
            i = 2
            while f'{base_name}_{i}{extension}' in os.listdir(directory):
                i += 1
            new_filename_with_extension = f'{base_name}_{i}{extension}'
            return os.path.join(directory, new_filename_with_extension)


def xt_diagram(filename, var, x_mode='Lagrangian', show_layers: bool = True, show_shock_front: bool = False):
    """Plot a colored XT diagram for a Hyades variable

    ToDo:
        - add the SavePlot tool to the toolbar. I can use my excel writer!
    Args:
        filename (string): Name of the .cdf
        var (string): Abbreviated name of variable of interest - one of Pres, Rho, U, Te, Ti, Tr, R
        x_mode (string):
        show_layers (bool, optional): Toggle to show layer interfaces and names
        show_shock_front (bool, optional): Toggle to show the position of the shock front

    Returns:
        fig (matplotlib figure), ax (matplotlib axis)
    """
    hyades = HyadesOutput(filename, var)

    fig, ax = plt.subplots()

    if x_mode.lower() == 'eulerian':
        eulerian = HyadesOutput(filename, 'R')
        x_label = 'Eulerian Position (µm)'
        if len(hyades.x) == eulerian.output.shape[1]:  # hyades.output uses mesh coordinates
            eulerian_mesh_coordinates = eulerian.output
            pcm = ax.pcolormesh(eulerian_mesh_coordinates, hyades.time, hyades.output, cmap='viridis')
        elif len(hyades.x) == eulerian.output.shape[1] - 1:  # hyades.output uses Zone coordinates
            eulerian_zone_coordinates = (eulerian.output[:, :-1] + eulerian.output[:, 1:]) / 2
            pcm = ax.pcolormesh(eulerian_zone_coordinates, hyades.time, hyades.output, cmap='viridis')
        else:
            raise ValueError(f'Unrecognized dimension of {filename} {var} output: {hyades.output.shape}')
    elif x_mode.lower() == 'lagrangian':
        x_label = 'Lagrangian Position (µm)'
        pcm = ax.pcolormesh(hyades.x, hyades.time, hyades.output, cmap='viridis')
    else:
        raise ValueError(f'Unrecognized x_mode: {x_mode}. Options are Lagrangian or Eulerian')
    # During laser ablation the early material is ejected to the left at high speed making the scale whack
    # if var == 'U':
    #     pcm = ax.pcolormesh(hyades.x, hyades.time, hyades.output, vmin=0, cmap='viridis')
    # else:
    #     pcm = ax.pcolormesh(hyades.x, hyades.time, hyades.output, cmap='viridis')

    fig.colorbar(pcm, label=f"{hyades.long_name} ({hyades.units})")
    ax.set_title(f'{hyades.run_name} XT Diagram')
    ax.set(xlabel=x_label, ylabel='Time (ns)')

    if hyades.xray_probe:
        ax.hlines(hyades.xray_probe, hyades.x.min() - 0.5, hyades.x.max() + 0.5,
                  color='white', linestyles='dotted', lw=1)
        txt_x = (hyades.x.max() - hyades.x.min()) * 0.98
        txt_y = hyades.xray_probe[0] + (hyades.xray_probe[1] - hyades.xray_probe[0]) * 0.1
        ax.text(txt_x, txt_y, 'X-Ray Probe',
                color='white', ha='right')

    if show_layers:
        ax = add_layers(hyades, ax, color='white')

    if show_shock_front:
        shock = ShockVelocity(filename, 'left')
        x_shock = hyades.x[shock.shock_index]
        y_shock = hyades.time[10:]
        ax.plot(x_shock, y_shock,
                label='Shock Front', color='white',
                linestyle='dotted', lw=2)

    def format_coord(x, y):
        xarr = hyades.x
        yarr = hyades.time
        if ((x > xarr.min()) & (x <= xarr.max()) &
                (y > yarr.min()) & (y <= yarr.max())):
            col = np.searchsorted(xarr, x) - 1
            row = np.searchsorted(yarr, y) - 1
            z = hyades.output[row, col]
            return f'Position {x:1.2f} µm, Time {y:1.2f} ns, z={z:1.2f}'
        else:
            return f'x={x:1.2f}, y={y:1.2f}'
    ax.format_coord = format_coord

    return fig, ax


def visualize_target(filename):
    """Draw and label the simulation layers to scale.

    Note:
        Very thin layers tend to create messy, unreadable graphics.

    Args:
        filename (string): Name of the .inf

    Returns:
        fig (matplotlib figure), ax (matplotlib axis)

    """
    hyades = HyadesOutput(filename, 'U')
    fig, ax = plt.subplots()
    colors = ('coral', 'steelblue', 'firebrick', 'orchid', 'seagreen', 'chocolate')
    for material, c in zip(hyades.layers, colors):

        x = hyades.layers[material]['X Start']
        width = hyades.layers[material]['X Stop'] - hyades.layers[material]['X Start']
        y = 0
        height = 1
        label = f"{hyades.layers[material]['Name']}\n{hyades.layers[material]['EOS']}"
        ax.text(x + width / 2, 1.1, label, ha='center')
        ax.text(x + width / 2, -0.1, f'{width:.2f} µm', ha='center')
        ax.add_patch(matplotlib.patches.Rectangle((x, y), width, height,
                                                  facecolor=c,
                                                  edgecolor=None))
    upper_x = hyades.x.max() * 1.05
    lower_x = hyades.x.max() * -0.05
    ax.set(xlabel='Lagrangian Position (µm)', xlim=(lower_x, upper_x), ylim=(-0.3, 1.3))
    ax.set_title(f'Target Visualization of {hyades.run_name}')
    plt.tick_params(axis='y', which='both', left=False, right=False, labelleft=False)
    plt.grid(b=False, axis='y', which='both')

    return fig, ax


def eulerian_position(filename):
    """Plot the Eulerian position all zones over time.

    Note:
        In laser simulations the ablated material travels very far, throwing off the x scale.

    Args:
        filename (string): Name of the .cdf

    Returns:
        fig (matplotlib figure), ax (matplotlib axis)

    """
    hyades = HyadesOutput(filename, 'R')
    times = [i for i in range(int(hyades.time.max()))]

    # get region numbers from the cdf to color code each material in the eulerian plot
    cdf_name = os.path.join(hyades.dir_name, hyades.run_name+'.cdf')
    cdf = netcdf.netcdf_file(cdf_name, 'r')
    region_numbers = cdf.variables['RegNums'].data.copy()
    region_numbers = region_numbers[1:-1]  # region numbers has a zero padded on either end
    cdf.close()

    colors = plt.cm.tab10(np.linspace(0, 1, num=10))
    fig, ax = plt.subplots()
    for t in times:
        i = np.argmin(abs(hyades.time - t))
        mesh_coordinates = hyades.output[i, :]
        zone_coordinates = (mesh_coordinates[1:] + mesh_coordinates[:-1]) / 2
        # print('Time: ', t, 'Hyades min/max: ', hyades.output.min(), hyades.output.max())
        # print('Time: ', t, 'Mesh min/max: ', mesh_coordinates.min(), mesh_coordinates.max())
        # print('Time: ', t, 'Zone min/max: ', zone_coordinates.min(), zone_coordinates.max())
        for layer_num in np.unique(region_numbers):
            # print(t, layer_num)
            mask, = np.where(region_numbers == layer_num)
            # print(mask)
            layer_zone_coordinates = zone_coordinates[mask]
            # print(layer_zone_coordinates)
            y = [hyades.time[i] for j in range(len(layer_zone_coordinates))]
            ax.plot(layer_zone_coordinates, y, marker='o', color=colors[layer_num-1], markersize=1)

    ax.set_title(f'Eulerian Position of {hyades.run_name}')
    ax.set(xlabel=f'Eulerian Position ({hyades.units})', ylabel='Time (ns)')
    # customize legend so the markers are visible, otherwise they are hard to see due to markersize=1
    labels = [hyades.layers[material]['Name'] for material in hyades.layers]
    handles = [matplotlib.patches.Patch(color=c, label=l) for c, l in zip(colors, labels)]
    ax.legend(handles=handles)

    return fig, ax


def plot_shock_velocity(filename, mode):
    """Plot the Shock Velocity.

    Note:
        Mode can be used to compare effects of particle velocity indexing.

    Args:
        filename (string): Name of the .cdf
        mode (string): Type of indexing to use on particle velocity - one of Left, Right, All, Difference, or a list

    Returns:
        fig (matplotlib figure), ax (matplotlib axis)

    """
    save_dictionary = {}  # Dictionary to hold x, y data that can be written to .csv
    if isinstance(mode, list):  # Plot multiple shock velocities
        save_dictionary['Time (ns)'] = ShockVelocity(filename, 'Cubic').time
        fig, ax = plt.subplots()
        for m in mode:
            shock = ShockVelocity(filename, m)
            ax.plot(shock.time, shock.Us, label=m)
            save_dictionary[f'{m} Us (km/s)'] = shock.Us
        ax.legend()
        ax.set_title(f'Comparing Us of {os.path.basename(filename)}')
        comment = f'Comparing the {", ".join(mode)}-indexed Shock Velocities of {shock.run_name}'
    elif mode.lower() == 'all':  # Plot Shock Velocity using Left, Right, and Average Particle Velocity
        save_dictionary['Time (ns)'] = ShockVelocity(filename, 'Cubic').time
        fig, ax = plt.subplots()
        for m in ('left', 'right', 'average', 'cubic'):
            shock = ShockVelocity(filename, m)
            ax.plot(shock.time, shock.Us, label=m)
            save_dictionary[f'{m} Us (km/s)'] = shock.Us
            ax.legend()
        ax.set_title(f'Comparison of L, R, Avg, Cubic Us for {shock.run_name}')
        comment = ax.get_title()
    elif mode.lower() == 'difference':  # Plot the difference between the left and right indexed shock velocities
        L_shock = ShockVelocity(filename, 'left')
        R_shock = ShockVelocity(filename, 'right')
        assert (L_shock.time == R_shock.time).all(), 'Left and Right shock timings do not agree'
        fig, ax = plt.subplots()
        ax.plot(L_shock.time, L_shock.Us - R_shock.Us, label='Left - Right')
        save_dictionary['Time (ns)'] = L_shock.time
        save_dictionary['L - R Us (km/s)'] = L_shock.Us - R_shock.Us
        ax.legend()
        ax.set_title(f'Comparing L and R Us for {L_shock.run_name}')
        comment = f'A comparison of the Left and Right indexed shock velocities of {L_shock.run_name}'
    else:
        shock = ShockVelocity(filename, mode=mode)
        fig, ax = plt.subplots()
        ax.plot(shock.time, shock.Us)
        save_dictionary['Time (ns)'] = shock.time
        save_dictionary[f'{mode} Us (km/s)'] = shock.Us
        ax.set_title(f'Shock Velocity ({mode}) of {shock.run_name}')
        comment = f'{mode}-indexed Shock Velocity of {shock.run_name}'
    ax.set(xlabel='Time (ns)', ylabel='Shock Velocity (km/s)')

    run_name = ShockVelocity(filename, 'Cubic').run_name
    out_fname = os.path.join('data', run_name, f'{run_name}_Us.csv')
    fig.canvas.manager.toolmanager.add_tool('Save Data', SaveTools,
                                            data_dictionary=save_dictionary,
                                            header=comment,
                                            filename=out_fname)
    fig.canvas.manager.toolbar.add_tool('Save Data', 'foo')

    return fig, ax


def lineout(filename, var, times, show_layers: bool = True):
    """Plot the variable of interest at multiple times.

    Note:
        Hyades uses oddly sized time steps, so your time may not be in the data.
        This script plots the times closest to the input ones.
        The correct time is the one in the legend *not* the one you input.

    Args:
        filename (string): Name of the .cdf
        var (list): Abbreviated name of variable of interest - any of Pres, Rho, U, Te, Ti, Tr
        times (list): Floats of times to be plotted
        show_layers (bool, optional): Toggle to show the layer interfaces and names.

    Returns:
        fig (matplotlib figure), ax (matplotlib axis)

    """
    save_dictionary = {}
    colors = matplotlib.cm.copper(np.linspace(0, 1, num=len(times)))
    if len(var) == 1:  # One variable plots on a single axis
        var = var[0]
        hyades = HyadesOutput(filename, var)
        save_dictionary['Lagrangian Position (um)'] = hyades.x
        fig, ax = plt.subplots()
        for t, c in zip(times, colors):  # Plot a line for each time
            i = np.argmin(abs(hyades.time - t))
            ax.plot(hyades.x, hyades.output[i, :],
                    color=c, label=f'{hyades.time[i]:.2f} ns')
            save_dictionary[f'{hyades.time[i]:.2f} ns'] = hyades.output[i, :]
        if show_layers:  # Add material names and interfaces
            ax = add_layers(hyades, ax)
        if var == 'Rho':  # If plotting density, add horizontal lines for each layer ambient density
            ax = show_ambient_density(hyades, ax)
        # Format title, labels, axis, materials
        ax.set_title(f'{hyades.long_name} of {hyades.run_name}')
        ax.set(xlabel='Lagrangian Position (µm)', ylabel=f'{hyades.long_name} ({hyades.units})')
        ax.grid(b=True, which='major', axis='both', lw=1)
        ax.grid(b=True, which='minor', axis='both', lw=0.5, alpha=0.5)
        ax.minorticks_on()
        ax.legend()
        out_filename = f'{hyades.run_name} {var}.csv'
        comment = f'{hyades.long_name} of {hyades.run_name} at various times. ' \
                  f'Lagrangian Positions are in microns. {hyades.long_name} are in {hyades.units}'
    else:  # Multiple variables plot on stacked axes
        comment = 'Lagrangian Positions are in microns. '
        fig, ax_arr = plt.subplots(nrows=len(var), ncols=1, sharex=True)
        for v, ax in zip(var, ax_arr):  # Each variable gets its own axis
            hyades = HyadesOutput(filename, v)
            save_dictionary[f'{hyades.long_name} Position (um)'] = hyades.x
            comment += f'{hyades.long_name} are in {hyades.units}. '
            for t, c in zip(times, colors):  # Plot a line for each time
                i = np.argmin(abs(hyades.time - t))
                ax.plot(hyades.x, hyades.output[i, :],
                        color=c, label=f'{hyades.time[i]:.2f} ns')
                save_dictionary[f'{hyades.long_name} {hyades.time[i]:.2f} ns'] = hyades.output[i, :]
            if show_layers:  # Add material names and interfaces
                ax = add_layers(hyades, ax)
            # Format axis labels for its respective variable
            ax.set_ylabel(f'{hyades.long_name} ({hyades.units})', fontsize='small')
            ax.legend(fontsize='x-small', loc='lower right')
        fig.suptitle(f'Lineouts of {hyades.run_name}')
        ax_arr[-1].set_xlabel('Lagrangian Position (µm)')  # Add x label to the bottom axis
        out_filename = f'{hyades.run_name}_{"_".join(var)}.csv'

    fig.canvas.manager.toolmanager.add_tool('Save Data', SaveTools,
                                            data_dictionary=save_dictionary,
                                            header=comment,
                                            filename=os.path.join('data', hyades.run_name, out_filename))
    fig.canvas.manager.toolbar.add_tool('Save Data', 'foo')

    return fig, ax


def add_layers(hyades, ax, color='black'):
    """Add the layer names and interfaces to an axis

    Todo:
        - can I make this work for eulerian coordinates???

    Args:
        hyades (HyadesOutput): Used for the layer information
        ax (matplotlib axis): axis to add the layers to
        color (string, optional): Color used for text and lines. Try to pick one contrasting your plot
    """
    y_min = ax.get_ylim()[0]
    y_max = ax.get_ylim()[1]
    for material in hyades.layers:
        x_start = hyades.layers[material]['X Start']
        x_stop = hyades.layers[material]['X Stop']
        if x_stop < hyades.x.max():
            ax.vlines(x_stop, y_min, y_max,
                      color=color, linestyles='solid', lw=1, alpha=0.7)
        text_x = x_start + ((x_stop - x_start) / 2)
        text_y = y_max * 0.8
        label = hyades.layers[material]['Name']
        ax.text(text_x, text_y, label,
                color=color, ha='center')
    ax.set_ylim(y_min, y_max)

    return ax


def show_ambient_density(hyades, ax):
    """Add horizontal lines for each layer's ambient density

    Args:
        hyades (HyadesOutput): instance of hyades output used to plot
        ax: matplotlib axis to add the labels to

    Returns:
        ax (matplotlib axis)

    """
    cdf_name = os.path.join(hyades.dir_name, hyades.run_name + '.cdf')
    cdf = netcdf.netcdf_file(cdf_name, 'r')
    region_numbers = cdf.variables['RegNums'].data.copy()
    region_numbers = region_numbers[1:-1]  # RegNums has a zero padded on either end
    cdf.close()
    show_label = True
    for layer_num in np.unique(region_numbers):
        mask, = np.where(region_numbers == layer_num)
        layer_coordinates = hyades.x[mask]
        layer_ambient_density = hyades.output[0, mask]  # Density at time zero for a single layer
        if show_label:  # Cheap way to only label the Ambient Density line once
            ax.plot(layer_coordinates, layer_ambient_density,
                    linestyle='dotted', color='black', label='Ambient\nDensity', zorder=20)
        else:
            ax.plot(layer_coordinates, layer_ambient_density,
                    linestyle='dotted', color='black', zorder=20)
        show_label = False

    return ax


if __name__ == '__main__':
    f = '../data/diamond_decay'

    # fig, ax = lineout(f, ['R'], [1, 2, 3, 4, 5, 6])
    fig, ax = xt_diagram(f, 'Pres')
    fig, ax = xt_diagram(f, 'Pres', x_mode='Eulerian')
    plt.show()


    # hyades = HyadesOutput(f, 'Pres')
    # print(hyades.moi, hyades.shock_moi)
    # fig, ax = xt_diagram(f, 'Pres')
    shock_debug_plot = False
    if shock_debug_plot:
        hyades = HyadesOutput(f, 'Pres')
        shock = ShockVelocity(f, 'Cubic')
        print(shock.time.shape, shock.Us.shape)
        fig, ax = xt_diagram(f, 'Pres')
        x0 = hyades.x[shock.window_start]
        y0 = shock.time
        x1 = hyades.x[shock.window_stop]
        y1 = shock.time
        ax.plot(x0, y0,
                color='white', ls='dotted', lw=2, label='Shock Window')
        ax.plot(x1, y1,
                color='white', ls='dotted', lw=2)
        ax.plot(hyades.x[shock.shock_index], shock.time, 'red', label='Shock Front', lw=1)
        ax.legend()

    plt.show()
