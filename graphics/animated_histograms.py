import matplotlib.pyplot as plt
import matplotlib.animation
import numpy as np
from tools.hyades_output import HyadesOutput
plt.style.use('ggplot')
plt.rcParams['animation.ffmpeg_path'] = 'C:/Users/cjkri/ffmpeg/bin/ffmpeg.exe'

f = '../pyhy/data/FeSi/s77742_sep23_A'
hyades = HyadesOutput(f, 'Pres')
bins = np.linspace(hyades.output.min(), hyades.output.max(), num=50, endpoint=True)

fig, ax = plt.subplots()
histogram = ax.hist(hyades.output[0, :], bins=bins)
ax.set_title('s77742 Pressure Histogram')
axin1 = ax.inset_axes([0.7, 0.7, 0.25, 0.25], zorder=5)
line, = axin1.plot(hyades.x, hyades.output[0, :])

def animate(i):
    ax.clear()
    ax.hist(hyades.output[i, :], bins=bins,
            ec='white', fc='red')
    ax.set_title(f'Pressure Histogram at {hyades.time[i]:.1f} ns [{i}/{len(hyades.time)}]')
    ax.set(xlabel='Pressure (GPa)', ylabel='Counts',
           ylim=(0, 100))

    axin1 = ax.inset_axes([0.7, 0.7, 0.25, 0.25])
    axin1.plot(hyades.x, hyades.output[i, :])
    axin1.set_title(f'Pressure at {hyades.time[i]:.1f} ns', fontsize='small')
    axin1.set_xlabel('Position (µm)', fontsize='small')
    axin1.set_ylabel('Pressure (GPa)', fontsize='small')
    axin1.set(ylim=(0, hyades.output.max()))


ani = matplotlib.animation.FuncAnimation(fig, animate, frames=len(hyades.time), interval=10, repeat=True)
writer = matplotlib.animation.FFMpegWriter(fps=8)
ani.save(filename='s77742 Pressure Histogram.mp4', writer=writer, dpi=200)
print('Done')
# plt.show()

