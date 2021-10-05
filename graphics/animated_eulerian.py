"""Animate and color a Hyades simulation moving through Eulerian space

Todo:
    * The line collection isn't the best way to do this. For Zone indexes I could add a patch collection instead
    * add initial material interface labels
    * add moving material interface labels
    * I don't trust this for Rho or Te based on animated lineout visualizations
"""
import os
import numpy as np
import matplotlib as mpl
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from tools.hyades_reader import HyadesOutput
from scipy.io import netcdf
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
    cdf_name = os.path.join(hyades.dir_name, hyades.run_name + '.cdf')
    cdf = netcdf.netcdf_file(cdf_name)
    eulerian_positions = cdf.variables['R'].data.copy() * 1e4
    cdf.close()

    if hyades.output.shape[1] == eulerian_positions.shape[1]:  # if hyades.output is using Mesh indexing
        pass
    elif hyades.output.shape[1] + 1 == eulerian_positions.shape[1]:  # if hyades.output is using Zone indexing
        # Pressure, Temperature, and Density all use zone indexing
        left_mesh = eulerian_positions[:, :-1]
        right_mesh = eulerian_positions[:, 1:]
        eulerian_positions = (left_mesh + right_mesh) / 2  # Zone positions are average of left and right Mesh positions

    # Initialize the figure
    fig, ax = plt.subplots()
    ax.set_title('Eulerian Position')
    x_min = eulerian_positions.min() - ((eulerian_positions.max() - eulerian_positions.min()) * 0.05)
    x_max = eulerian_positions.max() + ((eulerian_positions.max() - eulerian_positions.min()) * 0.05)
    ax.set(xlim=(x_min, x_max), ylim=(-0.2, 1.2))

    # Add the lines for free surface initial positions
    first_layer = list(hyades.layers.keys())[0]
    left_free_surface = hyades.layers[first_layer]['X Start']
    last_layer = list(hyades.layers.keys())[-1]
    right_free_surface = hyades.layers[last_layer]['X Stop']
    ax.vlines((left_free_surface, right_free_surface), -0.1, 1.1,
              linestyles='dashed', color='black', alpha=0.7)

    # Plot the sample at time 0
    line_coordinates = [np.array([[x, 0], [x, 1]]) for x in eulerian_positions[0, :]]
    colors = mpl.cm.plasma(hyades.output[0, :])
    line_collection = LineCollection(line_coordinates, colors=colors)
    ax.add_collection(line_collection)

    # Set up the color bar
    cmap = mpl.cm.plasma
    norm = mpl.colors.Normalize(vmin=hyades.output.min(), vmax=hyades.output.max())
    fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), label=f'{hyades.long_name} ({hyades.units})')

    def animate(i):
        """Is called by FuncAnimation to update all the graphics"""
        ax.clear()
        # Update the position and colors of the lines
        line_coordinates = [np.array([[x, 0], [x, 1]]) for x in eulerian_positions[i, :]]
        colors = mpl.cm.plasma(hyades.output[i, :])
        line_collection = LineCollection(line_coordinates, colors=colors)
        ax.add_collection(line_collection)
        # Update the text displaying the time
        text_str = f'Time: {hyades.time[i]:.2f} ns'
        ax.text(0, 1.1, text_str)
        # Update formatting, titles, grids
        ax.set_title(f'Eulerian Movie of {os.path.basename(inf_name)}')
        ax.set(xlabel='Eulerian Position (µm)',
               xlim=(x_min, x_max), ylim=(-0.2, 1.2))
        ax.set(yticklabels=[])
        ax.tick_params(left=False)
        ax.grid(b=False, which='both', axis='y')

        # Add initial position lines
        ax.vlines((left_free_surface, right_free_surface), -0.1, 1.1,
                  linestyles='dashed', color='black', alpha=0.7)
        fig.canvas.draw()

        return line_collection,

    anim = mpl.animation.FuncAnimation(fig, animate, frames=len(hyades.time), interval=10, blit=True)

    return anim


if __name__ == '__main__':
    f = '../data/diamond_decay/diamond_decay'
    color_var = 'Pres'
    anim = eulerian_animation(f, color_var)

    save = True
    if save:
        print('Saving...')
        anim.save('eulerian.mp4', fps=12)
        print('Saved.')
    plt.show()
