"""Plot a histogram of a variable by selecting a rectangular region in an XT diagram"""
import matplotlib.pyplot as plt
import matplotlib.widgets as mwidgets
import numpy as np
from tools.hyades_reader import HyadesOutput
from graphics.static_graphics import add_layers
plt.style.use('ggplot')


def xt_diagram_with_histogram(filename, variable, compression_threshold=1):
    """Plots an XT Diagram with the ability to select a rectangular region for histograms

    Args:
        filename (string): Name of the data to be plotted
        variable (string): Abbreviated name of variable of interest
        compression_threshold (float): Toggleable minimum pressure to include in the histogram

    Returns:
        fig, axes

    """
    def update_histogram(compression_threshold=compression_threshold):
        """Updates histogram graphics, title, and statistics

        Args:
            compression_threshold (float): Toggleable minimum pressure to include in the histogram
        """

        nonlocal hyades
        nonlocal check_button
        checked = check_button.get_status()[0]
        if checked:
            pass  # If checked, use the default compression_threshold from the function definition
        else:
            compression_threshold = 0
        axes[1].cla()
        # Get the region selected on the xt diagram from the RectangleSelector
        x_min, x_max = min(rect.corners[0]), max(rect.corners[0])
        t_min, t_max = min(rect.corners[1]), max(rect.corners[1])
        x_min_index = np.argmin(abs(hyades.x[0, :] - x_min))
        x_max_index = np.argmin(abs(hyades.x[0, :] - x_max))
        closest_t_min, t_min_index = hyades.get_closest_time(t_min)
        closest_t_max, t_max_index = hyades.get_closest_time(t_max)

        selected_output = hyades.output[t_min_index:t_max_index, x_min_index:x_max_index]
        if compression_threshold > 0:  # ignores output below a compression_threshold pressure in GPa

            if hyades.data_dimensions[1] == 'NumMeshs':
                # FIXME: figure out how to make this work with particle velocity
                error_message = 'Due to indexing issues, this feature does not work for variables with NumMeshs dimensions.' \
                                '\nThis means it does not work for Particle Velocity (U) but should work for Particle Velocity (UCM).' \
                                '\nThis feature works for Pres, Rho, and Te/Ti/Tr.'
                raise ValueError(error_message)
            hyades_pressure = HyadesOutput(filename, 'Pres')
            selected_pressure = hyades_pressure.output[t_min_index:t_max_index, x_min_index:x_max_index]
            mask = selected_pressure >= compression_threshold
            selected_output = selected_output[mask]
        # Add histogram with custom bin sizes depending on the variable
        bin_sizes = {'Pres': 20, 'U': 0.25, 'UCM': 0.25, 'Rho': 0.25, 'Te': 250, 'Ti': 250, 'Tr': 250}
        if variable in bin_sizes:
            step = bin_sizes[variable]
        else:
            step = (selected_output.max() - selected_output.min()) / 30
        try:
            bins = np.arange(np.floor(selected_output.min()), np.ceil(selected_output.max()), step=step)
        except ValueError:
            print('Try clicking and drag on the XT diagram to select a region for the histogram.')
        else:
            axes[1].hist(selected_output.flatten(), bins=bins,
                         fc='tab:orange', ec=None)
            # Add vertical line at average
            axes[1].axvline(np.mean(selected_output), color='black', linestyle='solid',
                            label=f'Mean: {np.mean(selected_output):.2f} {hyades.units}')
            # Add shaded region indicating middle 50 % of histogram
            p25 = np.percentile(selected_output, 25)
            p75 = np.percentile(selected_output, 75)
            x = (p25, p25, p75, p75)
            y = (axes[1].get_ylim()[0], axes[1].get_ylim()[1], axes[1].get_ylim()[1], axes[1].get_ylim()[0])
            axes[1].fill(x, y, label='Middle 50%', color='tab:gray', alpha=0.4)
            # Format axis
            title = f'Histogram over {x_min:.1f}-{x_max:.1f} um and {closest_t_min:.1f}-{closest_t_max:.1f} ns'
            axes[1].set_title(title, fontsize='medium')
            axes[1].set(xlabel=f'{hyades.long_name} ({hyades.units})', ylabel='Counts')
            axes[1].legend(loc='upper left', fontsize='small')
            fig.canvas.draw()

    def on_region_selected(eclick, erelease):
        """Updates the histogram based on the region selected in the XT Diagram"""
        if eclick or erelease:
            update_histogram()
        return eclick, erelease

    def on_button_clicked(label):
        """Updates histogram to ignore uncompressed material if button is currently checked"""
        update_histogram()
        return label

    hyades = HyadesOutput(filename, variable)
    # Create figure with 2 axes
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(10, 5))
    plt.subplots_adjust(left=None, right=None, top=None, bottom=None, wspace=0.15)
    # Add xt diagram and its colorbar to first axis
    pcm = axes[0].pcolormesh(hyades.x[0, :], hyades.time, hyades.output)
    axes[0] = add_layers(hyades, axes[0], color='white')
    cb = plt.colorbar(pcm, ax=[axes[0]], location='right', pad=0.015)  # Add colorbar and label it
    cb.set_label(f'{hyades.long_name} ({hyades.units})', rotation=-90, labelpad=14)
    cb.ax.tick_params(labelsize='small')
    if hyades.xray_probe:  # Add horizontal lines on xt diagram for x-ray probe times
        axes[0].hlines(hyades.xray_probe, axes[0].get_xlim()[0], axes[0].get_xlim()[1],
                       color='white', linestyles='dotted', lw=1)
        txt_x = axes[0].get_xlim()[1] * 0.98
        txt_y = hyades.xray_probe[0] + (hyades.xray_probe[1] - hyades.xray_probe[0]) * 0.1
        axes[0].text(txt_x, txt_y, 'X-Ray Probe',
                     color='white', ha='right')
    # Format axis containing xt diagram
    axes[0].set_title(f'XT Diagram of {hyades.long_name}')
    axes[0].set(xlabel='Lagrangian Position (um)', ylabel='Time (ns)')

    axes[1].hist(hyades.output.flatten(),  # bins=bins,
                 facecolor='tab:orange', edgecolor=None)
    axes[1].set_title(f'Histogram of {hyades.long_name}')
    axes[1].yaxis.tick_right()
    axes[1].yaxis.set_label_position("right")

    # Add RectangleSelector to the XT diagram
    props = dict(facecolor='tab:orange', alpha=0.5)
    rect = mwidgets.RectangleSelector(axes[0], on_region_selected,
                                      interactive=True,
                                      minspanx=1,
                                      minspany=0.2,
                                      props=props)
    ax_checkbutton = plt.axes([0.73, 0.71, 0.13, 0.25], facecolor=(1, 1, 1, 0))  # facecolor transparency set to zero
    ax_checkbutton.set_frame_on(False)  # Remove the rectangular frame around the axis
    # Add CheckButtons on the histogram to material at pressures below 1 GPa
    check_button = mwidgets.CheckButtons(ax_checkbutton, [f'Ignore Pres < {compression_threshold} GPa'])
    check_button.on_clicked(on_button_clicked)
    # Format CheckButton font size and colors
    for t in check_button.labels:
        t.set(fontsize='small')
    for r in check_button.rectangles:
        r.set_facecolor('tab:orange')
        r.set_edgecolor('black')
        r.set_alpha(0.4)

    '''
    According to the matplotlib documentation, to keep the RectangleSelector and CheckButtons active,
    we must keep a reference to them. Adding them as attributes to the figure is my lazy way of creating references.
    Source: https://matplotlib.org/stable/api/widgets_api.html from Feb 2022
    '''
    axes[0].rectangle_selector = rect
    axes[1].check_button = check_button

    return fig, axes  # check_button


if __name__ == '__main__':
    filename = '../data/CLiF_shock'
    variable = 'U'
    fig, axes = xt_diagram_with_histogram(filename, variable, compression_threshold=1)
    plt.show()
