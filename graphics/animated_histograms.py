"""Animate a histogram showing the distribution of a variable over time"""
import numpy as np
import matplotlib.animation
import matplotlib.pyplot as plt
from tools.hyades_reader import HyadesOutput
plt.style.use('ggplot')


def histogram_animation(inf_name, var):
    """Animate the distribution of a variable over time

    Note:
        Click the screen to pause/play the animation

    Args:
        inf_name (string): Name of the Hyades run
        var (string): Abbreviated variable name

    Returns:
        anim (matplotlib animation)
    """
    anim_running = True

    hyades = HyadesOutput(inf_name, var)
    my_bins = np.linspace(hyades.output.min(), hyades.output.max(), num=50, endpoint=True)

    fig, ax = plt.subplots()
    counts, bins, bars = ax.hist(hyades.output[0, :], bins=my_bins)
    ax.set_title('s77742 Pressure Histogram')
    axin1 = ax.inset_axes([0.7, 0.65, 0.25, 0.25], zorder=5)
    line, = axin1.plot(hyades.x, hyades.output[0, :])
    x_text = hyades.output.min() + ((hyades.output.max() - hyades.output.min()) * 0.05)
    y_text = max(counts) * 0.9
    txt = ax.text(x_text, y_text, f'Time {hyades.time[0]:.2f} ns')

    def onclick(event):
        nonlocal anim_running
        if anim_running:
            anim.event_source.stop()
            anim_running = False
        else:
            anim.event_source.start()
            anim_running = True

    def update(i):
        """Called by FuncAnimate to update all the graphics"""
        ax.clear()
        counts, bins, bars = ax.hist(hyades.output[i, :], bins=my_bins,
                                     ec='white', fc='red')
        ax.set_title(f'Animated Histogram of {hyades.run_name}')
        ax.set(xlabel=f'{hyades.long_name} ({hyades.units})', ylabel='Counts')
        if max(counts) > 100:
            ax.set(ylim=(0, max(counts) * 1.05))
        else:
            ax.set(ylim=(0, 100))

        ax.text(x_text, ax.get_ylim()[1] * 0.9, f'Time {hyades.time[i]:.2f} ns', fontsize='large')
        ax_in = ax.inset_axes([0.7, 0.65, 0.25, 0.25])
        ax_in.plot(hyades.x, hyades.output[i, :])
        ax_in.set_title(f'Pressure at {hyades.time[i]:.2f} ns', fontsize='small')
        ax_in.set_xlabel('Position (µm)', fontsize='small')
        ax_in.set_ylabel('Pressure (GPa)', fontsize='small')
        ax_in.set(ylim=(0, hyades.output.max()))

    fig.canvas.mpl_connect('button_press_event', onclick)
    anim = matplotlib.animation.FuncAnimation(fig, update,
                                              frames=len(hyades.time), interval=10, repeat=True)

    return anim


if __name__ == '__main__':
    # Below is the variable to set the path to ffmpeg
    plt.rcParams['animation.ffmpeg_path'] = 'C:/Users/cjkri/ffmpeg/bin/ffmpeg.exe'
    f = '../data/FeSi/s77742_sep23_A'
    histogram_animation(f, 'Pres')

    save = False
    if save:
        writer = matplotlib.animation.FFMpegWriter(fps=8)
        print('Saving...')
        matplotlib.animation.save(filename='s77742 Pressure Histogram.mp4', writer=writer, dpi=200)
        print('Saved.')
    plt.show()


