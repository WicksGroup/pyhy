"""Useful graphics to view a completed optimization"""
import os
import json
import configparser
import numpy as np
import matplotlib.pyplot as plt
from tools.hyades_reader import HyadesOutput
plt.style.use('ggplot')


def compare_velocities(run_name, show_drive=True):
    """A static graph comparing the experimental and optimized velocities

    Args:
        run_name (string): Name of the optimization to be plotted
        show_drive (bool, optional): Toggle to show the pressure input

    Returns:
        fig (matplotlib figure), ax (matplotlib axis)

    """
    # Load simulated and experimental data
    json_name = f'./data/{run_name}/{run_name}_optimization.json'
    with open(json_name) as f:
        jd = json.load(f)
    # Load if using shock velocity from config file
    config = configparser.ConfigParser()
    config_filename = os.path.join('.', 'data', run_name, f'{run_name}.cfg')
    config.read(config_filename)
    use_shock_velocity = config.getboolean('Setup', 'use_shock_velocity',
                                           fallback=False)

    fig, ax = plt.subplots()
    # Plot experimental data
    experimental_x = jd['experimental']['time']
    experimental_y = jd['experimental']['velocity']
    experimental_label = os.path.basename(jd['experimental']['file'])
    ax.plot(experimental_x, experimental_y, label=experimental_label, color='tab:orange')
    # Plot best iteration from optimized data
    best_iteration = jd['best']['number']
    delay = jd['iterations'][best_iteration]['delay']
    simulated_x = np.array(jd['best']['time velocity']) - delay  # jd['parameters']['delay']
    simulated_y = jd['best']['velocity']
    ax.plot(simulated_x, simulated_y, label=f'{run_name}_{jd["best"]["number"]}', color='tab:blue')

    # Load Hyades data for xray_probe time
    hyades_name = f'{run_name}_{jd["best"]["number"]}'
    hyades = HyadesOutput(os.path.join('./data', run_name, hyades_name), 'U')
    if hyades.xray_probe:
        old_ylim = ax.get_ylim()
        x = (hyades.xray_probe[0], hyades.xray_probe[0], hyades.xray_probe[1], hyades.xray_probe[1])
        y = (ax.get_ylim()[0], ax.get_ylim()[1], ax.get_ylim()[1], ax.get_ylim()[0])
        ax.fill(x, y, color='tab:gray', alpha=0.4, label='X-Ray Probe Time')
        ax.set_ylim(old_ylim)

    # Figure formatting
    ax.set_title('Result of optimization ' + run_name)
    if use_shock_velocity:
        y_label = 'Shock Velocity (km/s)'
    else:
        y_label = 'Particle Velocity (km/s)'
    ax.set(xlabel='Time (ns)', ylabel=y_label)
    ax.legend()

    if show_drive:  # Optionally plot the pressure drive on the same figure
        x = np.array(jd['best']['time pressure']) - delay  # jd['parameters']['delay']
        y = jd['best']['pressure']
        ax2 = ax.twinx()
        ax2.plot(x, y, linestyle='--', label='Pressure Drive', color='black')
        ax2.set_ylabel('Pressure (GPa)')
        ax2.legend(loc='lower right')
        ax2.grid(b=False, axis='y', which='both')
        return fig, (ax, ax2)

    return fig, ax


def iteration_velocities(run_name):
    """Compares the experimental and optimized velocities

    Note:
        Use the arrow keys to move through the iterations in the optimizer. b jumps straight to the best optimization.

    Args:
        run_name (string): Name of the optimization run to be plotted. Does not require path

    Returns:
        fig (matplotlib figure), ax (matplotlib axis)

    """

    # Load json data from optimization
    json_name = f'./data/{run_name}/{run_name}_optimization.json'
    with open(json_name) as f:
        jd = json.load(f)  # load json data from optimization
    # Load if using shock velocity from config file
    config = configparser.ConfigParser()
    config.read(os.path.join('.', 'data', 'run_name', f'{run_name}.cfg'))
    use_shock_velocity = config.get('Setup', 'use_shock_velocity',
                                    fallback=False)

    fig, ax = plt.subplots()
    # Plot experimental velocity
    x_experiment = jd['experimental']['time']
    y_experiment = jd['experimental']['velocity']
    ax.plot(x_experiment, y_experiment, color='tab:orange', label='Experiment', zorder=2)
    # Plot simulated velocity at iteration 000
    delay = jd['iterations']['000']['delay']
    x = np.array(jd['iterations']['000']['time velocity']) - delay  # jd['parameters']['delay']
    y = jd['iterations']['000']['velocity']
    line, = ax.plot(x, y, color='tab:blue', label='Simulation', zorder=3)
    # Add text for residual
    x_txt = (jd['parameters']['time of interest'][0] + jd['parameters']['time of interest'][1]) / 2
    txt = ax.text(x_txt, ax.get_ylim()[1] * 0.9,
                  f'Residual: {jd["iterations"]["000"]["residual"]:.2f}',
                  ha='center')
    # Fill window where residual was calculated
    old_ylim = ax.get_ylim()
    x = (jd['parameters']['time of interest'][0], jd['parameters']['time of interest'][0],
         jd['parameters']['time of interest'][1], jd['parameters']['time of interest'][1])
    y = (ax.get_ylim()[0], ax.get_ylim()[1],
         ax.get_ylim()[1], ax.get_ylim()[0])
    ax.fill(x, y, color='tab:gray', alpha=0.4, zorder=1, label='Residual Window')
    ax.set_ylim(old_ylim)
    # Formatting
    iteration = 0
    ax.set_title(f'Optimization Progress of {run_name}: {iteration} / {max([int(i) for i in jd["iterations"].keys()])}')
    if use_shock_velocity:
        y_label = 'Shock Velocity (km/s)'
    else:
        y_label = 'Particle Velocity (km/s)'
    ax.set(xlabel='Time (ns)', ylabel=y_label)
    ax.legend(loc='upper left')
    # Display instructions on screen
    instruction_txt = ax.text(ax.get_xlim()[0] + 0.5, ax.get_ylim()[1] * 0.5,
                              'Use the Left/Right arrow keys to move 1 iteration. '
                              '\nUse the Up/Down arrow keys to move 10 iterations.'
                              '\nPress b to jump to the best run in the optimization.'
                              '\nPress any key to remove these instructions.')

    def update(event):
        """Function to bind key presses to updating the figure

        Args:
            event (key_press_event): event passed from matplotlib when a key is pressed

        Returns:

        """
        if instruction_txt.get_text():  # Remove instructions if they're still on screen
            instruction_txt.set_text('')

        nonlocal iteration  # Define actions on key presses
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

        if iteration < 0:  # Put bounds on how high and low the iteration count can go
            iteration = 0
        if iteration > max([int(i) for i in jd['iterations'].keys()]):
            iteration = max([int(i) for i in jd['iterations'].keys()])
        # Update simulated velocity line
        i = str(iteration).zfill(3)
        x = np.array(jd['iterations'][i]['time velocity']) - jd['iterations'][i]['delay']
        y = jd['iterations'][i]['velocity']
        line.set_data(x, y)
        # Update formatting
        ax.set_title(f'Optimization Progress of {run_name}: {iteration} / {max([int(i) for i in jd["iterations"].keys()])}')
        upper_ylim = max(max(y), max(jd['experimental']['velocity'])) * 1.025
        ax.set(ylim=(ax.get_ylim()[0], upper_ylim))
        # Update text
        txt.set_text(f'Residual: {jd["iterations"][i]["residual"]:.2f}')
        txt.set_y(ax.get_ylim()[1] * 0.9)

        fig.canvas.draw_idle()

    fig.canvas.mpl_connect('key_press_event', update)

    return fig, ax


def best_histogram(run_name):
    """Plots a pressure histogram of the best run from an optimization

    Args:
        run_name (string): Name of the optimization run to be plotted

    Returns:
        fig (matplotlib figure), ax (matplotlib axis)

    """
    # Load optimization and Hyades data
    json_name = f'./data/{run_name}/{run_name}_optimization.json'
    with open(json_name) as f:
        jd = json.load(f)
    best_run = run_name + '_' + jd['best']['number']
    hyades_name = os.path.join('./data', run_name, best_run)
    hyades = HyadesOutput(hyades_name, 'Pres')
    x_start = hyades.layers[hyades.moi]['Mesh Start']
    x_stop = hyades.layers[hyades.moi]['Mesh Stop'] - 1
    if hyades.xray_probe:
        t_start = np.argmin(abs(hyades.time - hyades.xray_probe[0]))
        t_stop = np.argmin(abs(hyades.time - hyades.xray_probe[1]))
        pressure_slice = hyades.output[t_start:t_stop, x_start:x_stop]
    else:
        pressure_slice = hyades.output[:, x_start:x_stop]

    fig, ax = plt.subplots(figsize=(7, 5))
    # Plot histogram
    bins = np.linspace(pressure_slice.min(), pressure_slice.max(), num=20, endpoint=True)
    ax.hist(pressure_slice.reshape((-1,)), bins=bins,
            ec='white')
    # Add average as vertical line
    ax.axvline(np.mean(pressure_slice), color='black', label=f'Mean: {np.mean(pressure_slice):.2f} GPa')
    # Shade in the middle 50th percentile
    p25 = np.percentile(pressure_slice, 25)
    p75 = np.percentile(pressure_slice, 75)
    x = (p25, p25, p75, p75)
    y = (ax.get_ylim()[0], ax.get_ylim()[1], ax.get_ylim()[1], ax.get_ylim()[0])
    ax.fill(x, y,
            label='Middle 50%', color='tab:gray', alpha=0.4)
    # Format title and labels
    ax.set_title(f'Pressure Distribution of {hyades.layers[hyades.moi]["Name"]} in {run_name}_{jd["best"]["number"]}')
    ax.set(xlabel='Pressure (GPa)', ylabel='Counts')
    ax.legend(loc='upper left')
    # Add a footnote below and to the right side of the chart
    if hyades.xray_probe:
        xray_text = f'Pressures shown are in {hyades.layers[hyades.moi]["Name"]}' \
                    f' during X-Ray probe time {hyades.xray_probe[0]} - {hyades.xray_probe[1]} ns'
    else:
        xray_text = f'Pressures shown are in {hyades.layers[hyades.moi]["Name"]} over all times'
    ax.annotate(xray_text,
                xy=(1.0, -0.2),
                xycoords='axes fraction',
                ha='right',
                va="center",
                fontsize=10)
    fig.tight_layout()

    return fig, ax
