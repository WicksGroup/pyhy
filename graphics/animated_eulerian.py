"""Animate and color a Hyades simulation moving through Eulerian space"""
import os
import numpy as np
import matplotlib as mpl
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from scipy.io import netcdf
from tools.hyades_reader import HyadesOutput
from graphics.static_graphics import add_layers
plt.style.use('ggplot')


def eulerian_animation(inf_name, color_var):
    """Animates the sample as it moves through Eulerian space.

    Args:
        inf_name (string): Name of the .inf to be plotted
        color_var (string): Abbreviated variable name, used to color the sample

    Returns:
        anim (matplotlib animation)

    """
    hyades = HyadesOutput(inf_name, color_var)

    # Initialize the figure
    fig, ax = plt.subplots()
    ax.set_title('Eulerian Position')
    x_min = hyades.x.min() - ((hyades.x.max() - hyades.x.min()) * 0.05)
    if x_min < 0:
        x_min = -10
    x_max = min(hyades.x[0, :].max() * 4, hyades.x.max() * 1.25)  # accounts for runs where material moves very far
    ax.set(xlim=(x_min, x_max), ylim=(-0.2, 1.2))

    # Add the lines for free surface initial positions
    first_layer = list(hyades.layers.keys())[0]
    left_free_surface = hyades.layers[first_layer]['X Start']
    last_layer = list(hyades.layers.keys())[-1]
    right_free_surface = hyades.layers[last_layer]['X Stop']
    ax.vlines((left_free_surface, right_free_surface), -0.1, 1.1,
              linestyles='dashed', color='black', alpha=0.7)

    # Plot the sample at time 0
    line_coordinates = [np.array([[x, 0], [x, 1]]) for x in hyades.x[0, :]]
    colors = mpl.cm.plasma(hyades.output[0, :])
    line_collection = LineCollection(line_coordinates, colors=colors)
    ax.add_collection(line_collection)

    # Set up the color bar
    cmap = mpl.cm.plasma
    norm = mpl.colors.Normalize(vmin=hyades.output.min(), vmax=hyades.output.max())
    fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), label=f'{hyades.long_name} ({hyades.units})', ax=ax)

    def animate(i):
        """Is called by FuncAnimation to update all the graphics"""
        ax.clear()
        # Update the position and colors of the lines
        line_coordinates = [np.array([[x, 0], [x, 1]]) for x in hyades.x[i, :]]
        nonlocal norm
        colors = mpl.cm.plasma(norm(hyades.output[i, :]))
        line_collection = LineCollection(line_coordinates, colors=colors)
        ax.add_collection(line_collection)
        # Update the text displaying the time
        text_str = f'Time: {hyades.time[i]:.2f} ns'
        ax.text(0, 1.1, text_str,
                bbox=dict(facecolor='white', edgecolor='None'))
        # Update formatting, titles, grids
        ax.set_title(f'Eulerian Movie of {os.path.basename(inf_name)}')
        ax.set(xlabel='Eulerian Position (µm)',
               xlim=(x_min, x_max), ylim=(-0.2, 1.2))
        ax.set(yticklabels=[])
        ax.tick_params(left=False)
        ax.grid(b=False, which='both', axis='y')

        if len(hyades.layers) > 1:  # If there are more than one layers in the simulation
            # Add initial positions of the layer interfaces
            for mat in hyades.layers:
                j = hyades.layers[mat]['Mesh Start'] - 1
                layer_position = hyades.x[0, j]
                init_layer = ax.axvline(x=layer_position, linestyle='dashed', color='tab:green', alpha=0.7)
            # Add moving positions of the layer interfaces
            for mat in hyades.layers:
                j = hyades.layers[mat]['Mesh Start'] - 1
                layer_position = hyades.x[i, j]
                move_layer = ax.axvline(x=layer_position, linestyle='solid', color='black', alpha=0.7)
                # Add moving layer labels
                eulerian_x_start = hyades.x[i, j]
                '''
                Always subtract one from mesh_stop to account for Python 0-indexing
                Subtract another on from mesh_stop if the data is in Zone Indices to account for Zone to Mesh conversion
                '''
                mesh_stop = hyades.layers[mat]['Mesh Stop']
                mesh_stop = mesh_stop - 2 if hyades.data_dimensions[1] == 'NumZones' else mesh_stop - 1
                eulerian_x_stop = hyades.x[i, mesh_stop]
                text_x = eulerian_x_start + ((eulerian_x_stop - eulerian_x_start) / 2)
                ax.text(text_x, 1.05, hyades.layers[mat]['Name'],
                        color='black', ha='center')

        # Add lines for the initial position of the free surfaces
        init_free = ax.axvline(x=left_free_surface, linestyle='dashed', color='black', alpha=0.7)
        ax.axvline(x=right_free_surface, linestyle='dashed', color='black', alpha=0.7)
        if len(hyades.layers) > 1:  # If there is more than one material we need a legend with material interfaces
            labels = ['Initial Layer Interface', 'Moving Layer Interface', 'Initial Free Surface']
            ax.legend([init_layer, move_layer, init_free], labels,
                      fontsize='x-small', loc='lower right')
        else:
            ax.legend([init_free], ['Initial Free Surface'],
                      fontsize='x-small', loc='lower right')

        fig.canvas.draw()
        return line_collection,

    anim = mpl.animation.FuncAnimation(fig, animate, frames=len(hyades.time), interval=10, blit=True)

    return anim
