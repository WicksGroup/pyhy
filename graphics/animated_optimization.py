import os
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from tools.hyades_reader import HyadesOutput
plt.style.use('fivethirtyeight')


def velocity_residual_animation(run_name, save_movie=False):
    """

    Args:
        run_name:

    Returns:

    """

    json_name = f'../data/{run_name}/{run_name}_optimization.json'
    with open(json_name) as f:
        jd = json.load(f)  # load json data from optimization

    lines = []

    fig, (ax1, ax2) = plt.subplots(ncols=1, nrows=2)
    # Plot experimental velocity
    x_experiment = jd['experimental']['time']
    y_experiment = jd['experimental']['velocity']
    ax1.plot(x_experiment, y_experiment, color='tab:orange', label='Experiment', zorder=1)
    # Plot simulated velocity at iteration 000
    x = np.array(jd['iterations']['000']['time velocity'])
    y = np.array(jd['iterations']['000']['velocity'])
    mask = x < 15
    line, = ax1.plot(x[mask], y[mask], color='tab:blue', label='Simulation', zorder=2)
    lines.append(line)
    # Format velocity plot
    ax1.set(xlim=(0, 15), ylim=(-1, 10),
            xlabel='Time (ns)', ylabel='Velocity (km/s)')
    ax1.set_title(f'Optimization Progress 000/{max([int(i) for i in jd["iterations"].keys()])}')
    ax1.legend(loc='upper left', fontsize='small')
    # Plot the first residual
    residuals = [jd['iterations'][str(i).zfill(3)]['residual'] for i in range(len(jd['iterations']) - 1)]
    line, = ax2.semilogy([0], residuals[0], color='tab:green')
    lines.append(line)
    ax2.set(xlim=(0, len(jd['iterations'])), ylim=(1, 5 * max(residuals)),
            xlabel='Iteration Number', ylabel='Residual')
    ax2.set_yticks([1, 10, 100, 1000])

    def update(i):
        """Called to change the line data during the animation"""
        nonlocal lines
        time = np.array(jd['iterations'][str(i).zfill(3)]['time velocity'])
        velocity = np.array(jd['iterations'][str(i).zfill(3)]['velocity'])
        mask = time < 15
        lines[0].set_data(time[mask], velocity[mask])
        if max(velocity[mask]) < 5:
            ax1.set(ylim=(-1, 5))

        lines[1].set_data(range(i), residuals[:i])

        ax1.set_title(f'Optimization Progress {str(i).zfill(3)}/{max([int(j) for j in jd["iterations"].keys()])}')
        return lines

    fig.tight_layout()
    anim = animation.FuncAnimation(fig, update,
                                   frames=len(jd['iterations']), interval=30,
                                   repeat=False, blit=False)
    if save_movie:
        print('Saving... (This m')
        Writer = animation.writers['ffmpeg']
        writer = Writer(fps=20, metadata=dict(artist='Me'), bitrate=1800)
        anim.save(f'../data/{run_name}/{run_name} optimization progress.mp4', dpi=200, writer=writer)
        print(f'Saved {run_name} optimization progress.mp4')

    plt.show()


if __name__ == '__main__':
    run_name = 's77731_211104'
    velocity_residual_animation(run_name, save_movie=True)
