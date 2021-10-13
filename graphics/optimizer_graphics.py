"""Useful graphics to view a completed optimization"""
import os
import json
import numpy as np
import matplotlib.pyplot as plt
from tools.hyades_reader import HyadesOutput
from graphics.static_graphics import xt_diagram
plt.style.use('ggplot')


def compare_velocities(run_name, show_drive=True):
    """A static graph comparing the experimental and optimized velocities

    Args:
        run_name:
        show_drive:

    Returns:

    """
    json_name = f'../data/{run_name}/{run_name}_optimization.json'
    with open(json_name) as f:
        jd = json.load(f)  # jd stands for json_data

    experimental_x = jd['experimental']['time']
    experimental_y = jd['experimental']['velocity']

    best_run = run_name + '_' + jd['best optimization']['name']
    hyades_name = os.path.join('../data', run_name, best_run)
    hyades = HyadesOutput(hyades_name, 'U')
    i = hyades.layers[hyades.moi]['Mesh Stop'] - 1
    print('MOI INDEX', i, hyades.x[i])

    fig, ax = plt.subplots()
    experimental_label = os.path.basename(jd['experimental']['file'])
    ax.plot(experimental_x, experimental_y, label=experimental_label, color='orange')
    simulated_x = hyades.time - jd['best optimization']['delay']
    simulated_y = hyades.output[:, i]
    ax.plot(simulated_x, simulated_y, label=best_run, color='blue')

    ax.set_title('Result of optimization ' + run_name)
    ax.set(xlabel='Time (ns)', ylabel='Particle Velocity (km/s)')
    ax.legend()

    if show_drive:
        x = np.array(jd['best optimization']['pres_time']) - jd['best optimization']['delay']
        y = jd['best optimization']['pres']
        ax2 = ax.twinx()
        ax2.plot(x, y, linestyle='--', label='Pressure Drive', color='black')

        ax2.set_ylabel('Pressure (GPa)')
        ax2.legend(loc='lower right')
        ax2.grid(b=False, axis='y', which='both')

    return fig, ax


if __name__ == '__main__':
    # run = 's77742'
    # fig, ax = compare_velocities(run)
    # plt.show()

    import matplotlib.pyplot as plt
    import numpy as np


    def type_plot():
        n = 20

        def update(event):
            nonlocal n
            if event.key == 'left':
                n -= 1
            if event.key == 'right':
                n += 1
            if event.key == 'up':
                n += 10
            if event.key == 'down':
                n -= 10
            print(n)
            x = [i for i in range(n)]
            y = np.random.random((n,))
            ax.cla()
            ax.plot(x, y)
            ax.set_title(n)
            fig.canvas.draw_idle()

            return line

        fig, ax = plt.subplots()
        line, = ax.plot([i for i in range(n)], np.random.random((n, )))

        fig.canvas.mpl_connect('key_press_event', update)

    type_plot()
    plt.show()
