import os
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from scipy.io import netcdf
from tools.hyades_reader import ShockVelocity, HyadesOutput
plt.style.use('ggplot')


def xt_diagram(filename, var, show_layers: bool = True, show_shock_front: bool = False):
    """Plot a colored XT diagram for a Hyades variable

    Args:
        filename (string): Name of the .cdf
        var (string): Abbreviated name of variable of interest - one of Pres, Rho, U, Te, Ti, Tr, R
        show_layers (bool, optional): Toggle to show layer interfaces and names
        show_shock_front (bool, optional): Toggle to show the position of the shock front

    Returns:
        fig (matplotlib figure), ax (matplotlib axis)
    """
    hyades = HyadesOutput(filename, var)

    fig, ax = plt.subplots()

    if var == 'U':
        pcm = ax.pcolormesh(hyades.x, hyades.time, hyades.output, vmin=0, cmap='viridis')
    else:
        pcm = ax.pcolormesh(hyades.x, hyades.time, hyades.output, cmap='viridis')

    fig.colorbar(pcm, label=f"{hyades.long_name} ({hyades.units})")

    ax.set_title(f'{hyades.run_name} XT Diagram')
    ax.set(xlabel='Lagrangian Position (µm)', ylabel='Time (ns)',
           xlim=(hyades.x.min(), hyades.x.max()))

    if hyades.xray_probe:
        ax.hlines(hyades.xray_probe, hyades.x.min() - 0.5, hyades.x.max() + 0.5,
                  color='white', linestyles='dotted', lw=1)
        txt_x = (hyades.x.max() - hyades.x.min()) * 0.98
        txt_y = hyades.xray_probe[0] + (hyades.xray_probe[1] - hyades.xray_probe[0]) * 0.1
        ax.text(txt_x, txt_y, 'X-Ray Probe',
                color='white', ha='right')

    if show_layers:
        for material in hyades.layers:
            x_start = hyades.layers[material]['X Start']
            x_stop = hyades.layers[material]['X Stop']
            if x_stop < hyades.x.max():
                ax.vlines(x_stop, hyades.time.min(), hyades.time.max(),
                          color='white', linestyles='solid', lw=1, alpha=0.7)
            text_x = x_start + ((x_stop - x_start) / 2)
            text_y = hyades.time.max() * 0.9
            label = f"{hyades.layers[material]['Name']}\n{hyades.layers[material]['EOS']}"
            ax.text(text_x, text_y, label,
                    color='white', ha='center')

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

    Todo:
        * Adjust the x scale and add a note during laser ablation to account for ablated material

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
    if isinstance(mode, list):  # Plot multiple shock velocities
        fig, ax = plt.subplots()
        for m in mode:
            shock = ShockVelocity(filename, m)
            ax.plot(shock.time, shock.Us, label=m)
        ax.legend()
        ax.set_title(f'Comparing Us of {os.path.basename(filename)}')
    elif mode.lower() == 'all':  # Plot Shock Velocity using Left, Right, and Average Particle Velocity
        fig, ax = plt.subplots()
        for m in ('left', 'right', 'average'):
            shock = ShockVelocity(filename, m)
            ax.plot(shock.time, shock.Us, label=m)
            ax.legend()
        ax.set_title(f'Comparison of L, R, Avg Us for {shock.run_name}')
    elif mode.lower() == 'difference':  # Plot the difference between the left and right indexed shock velocities
        L_shock = ShockVelocity(filename, 'left')
        R_shock = ShockVelocity(filename, 'right')
        assert (L_shock.time == R_shock.time).all(), 'Left and Right shock timings do not agree'
        fig, ax = plt.subplots()
        ax.plot(L_shock.time, L_shock.Us - R_shock.Us, label='Left - Right')
        ax.legend()
        ax.set_title(f'Comparing L and R Us for {L_shock.run_name}')
    else:
        shock = ShockVelocity(filename, mode=mode)
        fig, ax = plt.subplots()
        ax.plot(shock.time, shock.Us)
        ax.set_title(f'Shock Velocity ({mode}) of {shock.run_name}')
    ax.set(xlabel='Time (ns)', ylabel='Shock Velocity (km/s)')
    return fig, ax


def lineout(filename, var, times, show_layers: bool = True):
    """Plot the variable of interest at multiple times.

    Note:
        Hyades uses oddly sized time steps, so your time may not be in the data.
        This script plots the times closest to the input ones.
        The correct time is the one in the legend **not** the one you input.

    Args:
        filename (string): Name of the .cdf
        var (string): Abbreviated name of variable of interest - one of Pres, Rho, U, Te, Ti, Tr, R
        times (list): Floats of times to be plotted
        show_layers (bool, optional): Toggle to show the layer interfaces and names.

    Returns:
        fig (matplotlib figure), ax (matplotlib axis)

    """
    hyades = HyadesOutput(filename, var)
    colors = matplotlib.cm.viridis(np.linspace(0, 1, num=len(times)))
    fig, ax = plt.subplots()
    for t, c in zip(times, colors):
        i = np.argmin(abs(hyades.time - t))
        ax.plot(hyades.x, hyades.output[i, :], color=c, label=f'{hyades.time[i]:.2f} ns')
    ax.set_title(f'Lineouts of {hyades.run_name}')
    ax.set(xlabel='Lagrangian Position (µm)', ylabel=f'{hyades.long_name} ({hyades.units})')
    ax.legend()
    y_min, y_max = ax.get_ylim()
    if show_layers:
        for material in hyades.layers:
            x_start = hyades.layers[material]['X Start']
            x_stop = hyades.layers[material]['X Stop']
            if x_stop < hyades.x.max():
                ax.vlines(x_stop, y_min - 0.5, y_max + 0.5,
                          color='black', linestyles='solid', lw=1, alpha=0.7)
            text_x = x_start + ((x_stop - x_start) / 2)
            text_y = y_max * 0.9
            label = f"{hyades.layers[material]['Name']}\n{hyades.layers[material]['EOS']}"
            ax.text(text_x, text_y, label,
                    color='black', ha='center')
    ax.set_ylim(y_min, y_max)

    return fig, ax


if __name__ == '__main__':
    directory = '../data/'
    filename = 'diamond_decay'
    var = 'Pres'
    f = os.path.join(directory, filename, filename+'.cdf')
    # fig, ax = plot_shock_velocity(f, 'all')
    # ax.set_title('Three methods of calculating Shock Velocity')
    # fig, ax = lineout(f, var, [0, 10, 20, 30, 50, 100, 150, 250])
    # fig, ax = lineout(f, 'U', [])
    # fig, ax = XTDiagram(f, 'Rho')
    # fig, ax = XTDiagram(f, 'Pres')
    # fig, ax = XTDiagram(f, 'U')
    # hyades = hyadesOutput(f, 'Pres')
    # print(hyades.time.min(), hyades.time.max())
    # print(hyades.x.min(), hyades.x.max())
    # print(hyades.output.min(), hyades.output.max())

    shock_debug_plot = True
    if shock_debug_plot:
        hyades = HyadesOutput(f, 'Pres')
        shock = ShockVelocity(f, 'left')
        fig, ax = xt_diagram(f, 'Pres')
        x0 = hyades.x[shock.window_start]
        y0 = hyades.time[10:]
        x1 = hyades.x[shock.window_stop]
        y1 = hyades.time[10:]
        ax.plot(x0, y0,
                color='white', ls='dotted', lw=2, label='Shock Window')
        ax.plot(x1, y1,
                color='white', ls='dotted', lw=2)
        ax.plot(hyades.x[shock.shock_index], hyades.time[10:], 'red', label='Shock Front', lw=1)
        ax.legend()

    plt.show()
