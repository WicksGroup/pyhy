"""Animate a variable lineout moving through all times

Todo:
    - Would it be helpful to add the ambient density as a horizontal line for each layer?
"""
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from tools.hyades_reader import HyadesOutput
from graphics.static_graphics import add_layers
from graphics.static_graphics import show_ambient_density
plt.style.use('ggplot')


def lineout_animation(inf_name, var, show_layers=True):
    """Animate a single variable lineout as it changes over time

    Note:
        Click the screen to pause/play the animation

    Args:
        inf_name (string): Name of the Hyades run
        var (string): Abbreviated variable name
        show_layers (bool, optional): Toggle to show layer names and boundaries

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
        txt.set_text(f'Time: {hyades.time[i]:.2f} ns')
        return line,

    hyades = HyadesOutput(inf_name, var)

    fig, ax = plt.subplots()
    # Add Line
    line, = ax.plot(hyades.x, hyades.output[0, :], lw=2)
    txt = ax.text(hyades.x.max() * 0.02, hyades.output.max() * 0.94, 'Time: 0.00 ns', ha='left', fontsize='large')
    # Format title, axis
    ax.set_title(f'Animated Lineout of {hyades.run_name} {var}')
    ax.set(xlabel='Position (µm)', ylabel=f'{hyades.long_name} ({hyades.units})',
           ylim=(hyades.output.min(), hyades.output.max()))
    ax.grid(b=True, which='major', axis='both', lw=1)
    ax.grid(b=True, which='minor', axis='both', lw=0.5, alpha=0.5)
    ax.minorticks_on()

    if show_layers:
        ax = add_layers(hyades, ax)
    if var == 'Rho':
        ax = show_ambient_density(hyades, ax)
        ax.legend(loc='upper right')

    fig.canvas.mpl_connect('button_press_event', onclick)
    anim = animation.FuncAnimation(fig, animate, frames=len(hyades.time), interval=100, blit=False)

    return anim


if __name__ == '__main__':
    f = '../data/FeSi/CFe_shock100'
    var = 'Rho'
    lineout_animation(f, var)
    plt.show()
