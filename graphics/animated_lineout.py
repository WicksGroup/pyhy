"""Animate a lineout moving through all times

Todo:
    * add save feature
"""
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from tools.hyades_reader import HyadesOutput
plt.style.use('ggplot')


def animiated_lineout(inf_name, var):
    """Animate a single variable lineout as it changes over time

    Args:
        inf_name:
        var:

    Returns:

    """
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
        """Is called by FuncAnimate to update all the graphics"""
        line.set_ydata(hyades.output[i, :])
        txt.set_text(f'Time {hyades.time[i]:.2f} ns')
        return line,

    hyades = HyadesOutput(inf_name, var)

    fig, ax = plt.subplots()
    ax.set_title(f'Animated Lineout of {hyades.run_name}')
    ax.set(xlabel='Position (µm)', ylabel=f'{hyades.long_name} ({hyades.units})',
           ylim=(hyades.output.min(), hyades.output.max()))
    line, = ax.plot(hyades.x, hyades.output[0, :], lw=2)
    txt = ax.text(hyades.x.max() * 0.98, hyades.output.max() * 0.94, 'Time 0.00 ns', ha='right')
    fig.canvas.mpl_connect('button_press_event', onclick)
    anim = animation.FuncAnimation(fig, animate, frames=len(hyades.time), interval=70, blit=False)


if __name__ == '__main__':
    f = '../data/diamond_decay'
    var = 'Te'
    animiated_lineout(f, var)
    plt.show()
