"""Animate a variable lineout moving through all times"""
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from tools.hyades_reader import HyadesOutput
from graphics.static_graphics import add_layers
from graphics.static_graphics import show_ambient_density
plt.style.use('ggplot')


def lineout_animation(inf_name, var, coordinate_system='Lagrangian', show_layers=True):
    """Animate a single variable lineout as it changes over time

    Note:
        Click the screen to pause/play the animation

    Args:
        inf_name (string): Name of the Hyades run
        var (string): Abbreviated variable name
        coordinate_system (string, optional): Coordinate System to use on the x-axis
        show_layers (bool, optional): Toggle to show layer names and boundaries

    Returns:

    """
    coordinate_system = coordinate_system.lower()
    if not (coordinate_system == 'lagrangian' or coordinate_system == 'eulerian'):
        raise ValueError(f'Unrecognized coordinate system: {coordinate_system!r}. Options are Lagrangian or Eulerian')
    anim_running = True

    def onclick(event):
        """Controls pause/play stay when screen is clicked"""
        nonlocal anim_running
        if anim_running:
            anim.event_source.stop()
            anim_running = False
        else:
            anim.event_source.start()
            anim_running = True

    def animate(i):
        """Function called by matplotlib.animation.FuncAnimation to update all graphics"""
        nonlocal coordinate_system
        line.set_ydata(hyades.output[i, :])
        if coordinate_system == 'lagrangian':
            pass  # Do not update x data in Lagrangian Coordinates
        else:
            line.set_xdata(hyades.x[i, :])  # Update x data in Eulerian Coordinates
            if show_layers:  # Update layer interfaces in Eulerian coordinates
                for j, layer in enumerate(list(hyades.layers.keys())):
                    mesh_start = hyades.layers[layer]['Mesh Start'] - 1  # Subtract 1 for Python 0-indexing
                    mesh_stop = hyades.layers[layer]['Mesh Stop'] - 1
                    if hyades.data_dimensions[1] == 'NumZones':  # Subtract an addition 1 for Zone to Mesh conversion
                        mesh_stop -= 1
                    eulerian_x_start = hyades.x[i, mesh_start]
                    eulerian_x_stop = hyades.x[i, mesh_stop]
                    text_x = eulerian_x_start + ((eulerian_x_stop - eulerian_x_start) / 2)
                    layer_labels[j].set_x(text_x)
                    # print(layer, eulerian_x_start, text_x)
                    if j > 0:
                        layer_lines[j-1].set_xdata(eulerian_x_start)
        txt.set_text(f'Time: {hyades.time[i]:.2f} ns')
        return line,

    hyades = HyadesOutput(inf_name, var)

    fig, ax = plt.subplots()
    # Add Line
    line, = ax.plot(hyades.x[0, :], hyades.output[0, :], lw=2)
    txt = ax.text(hyades.x.max() * 0.02, hyades.output.max() * 0.94, 'Time: 0.00 ns', ha='left', fontsize='large')
    # Format title, axis
    ax.set_title(f'Animated Lineout of {hyades.run_name} {var}')
    if coordinate_system == 'lagrangian':
        x_label = 'Lagrangian Position (µm)'
    else:
        x_label = 'Eulerian Position (µm)'
    ax.set(xlabel=x_label, ylabel=f'{hyades.long_name} ({hyades.units})',
           ylim=(hyades.output.min(), hyades.output.max() * 1.05))
    if coordinate_system == 'eulerian':
        ax.set_xlim(ax.get_xlim()[0], hyades.x.max())
    ax.grid(b=True, which='major', axis='both', lw=1)
    ax.grid(b=True, which='minor', axis='both', lw=0.5, alpha=0.5)
    ax.minorticks_on()

    if show_layers:
        '''Even with coordinate_system="Eulerian" the add_layers function is not intended for this type of plot.
           The layer interfaces and labels for Eulerian animated lineouts are handled in the animate function.
        '''
        if coordinate_system == 'lagrangian':
            ax = add_layers(hyades, ax, coordinate_system=coordinate_system)
        elif coordinate_system == 'eulerian':
            layer_lines = []
            layer_labels = []
            for layer in hyades.layers:
                mesh_start = hyades.layers[layer]['Mesh Start'] - 1  # Subtract 1 for Python 0-indexing
                mesh_stop = hyades.layers[layer]['Mesh Stop'] - 1
                if hyades.data_dimensions[1] == 'NumZones':  # Subtract an addition 1 for Zone to Mesh conversion
                    mesh_stop -= 1
                eulerian_x_start = hyades.x[0, mesh_start]
                eulerian_x_stop = hyades.x[0, mesh_stop]
                if layer != 'layer1':  # Do not draw a line for the first layer, which is the left-hand free surface
                    layer_line = ax.axvline(x=eulerian_x_start, color='black', linestyle='solid')
                    layer_lines.append(layer_line)
                text_x = eulerian_x_start + ((eulerian_x_stop - eulerian_x_start) / 2)
                layer_label = ax.text(text_x, hyades.output.max() * 0.8, hyades.layers[layer]['Name'],
                                      ha='center')
                layer_labels.append(layer_label)

    if var == 'Rho':
        ax = show_ambient_density(hyades, ax)
        ax.legend(loc='upper right')

    fig.canvas.mpl_connect('button_press_event', onclick)
    anim = animation.FuncAnimation(fig, animate, frames=len(hyades.time), interval=20, blit=False)

    return anim
