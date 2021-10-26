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


def scrolling_plot(run_name):
    """Compares the experimental and optimized velocities. Use the arrow keys and b to scroll through optimization

    Note:
        Use the arrow keys to move through the iterations in the optimizer. b jumps straight to the best optimization

    Todo:
        - I think I need to add the delay somewhere
        - make sure iterations stays between 0 and the max in the json file

    Args:
        run_name:

    Returns:

    """
    json_name = f'../data/{run_name}/{run_name}_optimization.json'
    with open(json_name) as f:
        jd = json.load(f)  # jd stands for json_data

    fig, ax = plt.subplots()
    ax.plot(jd['experimental']['time'], jd['experimental']['velocity'], label='Experiment')
    x = jd['iterations']['000']['time velocity']
    y = jd['iterations']['000']['velocity']
    line, = ax.plot(x, y, label='Simulation')

    iteration = 0
    ax.set_title(f'Optimization of {run_name}: {iteration} / {max([int(i) for i in jd["iterations"].keys()])}')
    ax.set(xlabel='Time (ns)', ylabel='Velocity (km/s)')
    ax.legend()

    def update(event):
        nonlocal iteration
        if event.key == 'left':
            iteration -= 1
        if event.key == 'right':
            iteration += 1
        if event.key == 'up':
            iteration += 10
        if event.key == 'down':
            iteration -= 10
        if event.key == 'b':
            iteration = int(jd['best']['number'])

        i = str(iteration).zfill(3)
        x = jd['iterations'][i]['time velocity']
        y = jd['iterations'][i]['velocity']
        line.set_data(x, y)
        ax.set_title(f'Optimization of {run_name}: {iteration} / {max([int(i) for i in jd["iterations"].keys()])}')
        fig.canvas.draw_idle()

    fig.canvas.mpl_connect('key_press_event', update)


if __name__ == '__main__':
    run_name = 's77742'
    scrolling_plot(run_name)
    plt.show()
