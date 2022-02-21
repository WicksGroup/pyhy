"""Command line interface to plot various Hyades figures.

Notes:
    See --help for usage.

"""
import os
import argparse
import matplotlib.pyplot as plt
from graphics import static_graphics
from graphics.xt_histogram import xt_diagram_with_histogram


def is_float(string):
    """Returns True if a string can be converted to a float, otherwise False"""
    try:
        float(string)
        return True
    except ValueError:
        return False


def save_figure(filename, dpi=200):
    """Ask user if okay to overwrite file before saving

    Args:
        filename (string): name of the file to be saved
        dpi (float): dpi parameter passed to matplotlib.pyplot.savefig

    Returns:
        saved (bool): Whether the file was saved
    """
    if os.path.exists(filename):
        response0 = input(f'{filename} already exists.\nDo you want to write over the existing file? [y/n] ')
        if response0 == 'y':
            print('Overwriting old figure and saving new one.')
            plt.savefig(filename, dpi=dpi)
            return True
        else:
            print('Did not save new figure.')
            return False
    else:
        plt.savefig(filename, dpi=dpi)
        return True


description = '''A command line interface to plot common types of Hyades graphics.
                                 
This is a Python script to generate common plots from Hyades data.
It can create many different static graphics, such as XT Diagrams,
diagram of the target design, and/or a plot of the shock velocity.
Please note the shock velocity function is only designed for shock
simulations and may not yield useful results for ramp compression.

Examples:
    If you already ran a simulation named 'diamond_decay' then the
    following line would create XT Diagrams for Pressure, Density,
    and Particle Velocity, each in their own pop up window:
        $ python plot.py diamond_decay -xt Pres Rho U
    To plot an XT diagram of the pressure with a histogram, use:
        $ python plot.py diamond_decay -xth Pres
        
    The following line plots the pressure over the whole sample at
    the times in the data closest to 1, 2, 3.4, 5 and 9 nanoseconds:
        $ python plot.py diamond_decay --lineout Pres 1 2 3.4 5 9
    
    To save graphics without displaying them, combine the `--save`
    and `--quiet` commands. The following would create a figure of
    the target design and save the figure without displaying it:
        $ python plot.py diamond_decay --target -sq

'''
epilog = '''
                      ___      _  _      
                     | _ \_  _| || |_  _ 
                     |  _/ || | __ | || |
                     |_|  \_, |_||_|\_, |
                          |__/      |__/ 
               Developed by the Wicks Lab at JHU
'''

parser = argparse.ArgumentParser(prog='plot.py',
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 description=description,
                                 epilog=epilog
                                 )

parser.add_argument('filename', type=str,
                    help='Name of the Hyades run to be plotted. Assumed to be in pyhy/data '
                         'and does not require file extension.')
parser.add_argument('-xt', choices=['Pres', 'Rho', 'Rho0', 'Sd1', 'Te',  'Ti', 'Tr', 'U', 'UCM'], nargs='+',
                    help='Plot each variable on an XT diagram.'
                         '\nMultiple selections are allowed and each will be plotted on their own figure.')
parser.add_argument('-xth', '--xt_histogram', nargs='+',
                    help='Plot an XT diagram with accompanying histogram.'
                         '\nClick and drag the XT diagram to create a histogram.'
                         '\nAdd a number to the command to set the minimum pressure threshold.')
parser.add_argument('-l', '--lineout', nargs='+',
                    help='Plot lineouts of a variable of interest at multiple times')
parser.add_argument('-t', '--target', action='store_true',
                    help='Toggle to plot the target design. Works best on targets with wide layers.')
parser.add_argument('-k', '--shock', nargs='*',
                    choices=['L', 'R', 'Avg', 'difference', 'Cubic', 'all'],
                    help='Toggle to plot the Shock Velocity.'
                         ' Optionally select how to index Particle Velocity in Shock calculation (default: Cubic).'
                         ' Multiple selections are allowed and will be plotted on a single figure.')
parser.add_argument('-c', '--coordinate', choices=('e', 'eulerian', 'l', 'lagrangian'),
                    help='Coordinate system for the x-axis of XT diagrams and lineouts. (Default: Lagrangian)')
parser.add_argument('--title', type=str, nargs='+',
                    help='Sets a custom title on *all* figures. Recommended when only one plot is specified.')
parser.add_argument('-s', '--save', action='store_true',
                    help='Toggle to save all graphics after they are closed.')
parser.add_argument('-q', '--quiet', action='store_true',
                    help='Toggle to hide the graphics.'
                         ' Recommend use with --save for saving files without viewing.')

args = parser.parse_args()
# End parser

abs_path = './data/' + os.path.splitext(args.filename)[0]
base_out_filename = os.path.join('./data/', os.path.splitext(args.filename)[0], os.path.splitext(args.filename)[0])

coordinate_system = args.coordinate or 'Lagrangian'
if coordinate_system == 'e':
    coordinate_system = 'Eulerian'
elif coordinate_system == 'l':
    coordinate_system = 'Lagrangian'

if args.xt:
    '''XT Diagrams require a variable of interest. Multiple variables are plotted on separate figures.
    Example:
        $ python plot.py file_name -xt Pres U
        Would create one XT Diagram for the Pressure and one for the Particle Velocity, each in their own figure.
    '''
    for var in args.xt:
        fig, ax = static_graphics.xt_diagram(abs_path, var, coordinate_system=coordinate_system)
        if args.title:
            ax.set_title(' '.join(args.title))
        if args.save:
            out_fname = f'{base_out_filename} {var} {coordinate_system} XT.png'
            save_figure(out_fname)
            # plt.savefig(out_fname, dpi=200)

if args.xt_histogram:
    '''XT diagram with histograms work very similarly to regular XT diagrams.
    Example:
        $ python plot.py file_name -xth Pres
        You can customize the minimum pressure threshold by adding a number to the command.
        The following line would set the minimum pressure on the histogram to 17 GPa
        $ python plot.py file_name -xth Pres 17
    '''
    if len(args.xt_histogram) == 1:  # Only input was variable
        fig, axes = xt_diagram_with_histogram(abs_path, args.xt_histogram[0])
    elif len(args.xt_histogram) == 2:  # Inputs are variable, compression_threshold
        variable, compression_threshold = args.xt_histogram
        compression_threshold = float(compression_threshold)
        if is_float(compression_threshold):
            fig, axes = xt_diagram_with_histogram(abs_path, variable, compression_threshold=compression_threshold)
    else:
        raise ValueError('--xt_histogram only accepts one or two inputs. See --help for details.')
    if args.title:
        ax.set_title(' '.join(args.title))
    if args.save:
        out_fname = f'{base_out_filename} {var} XT histogram.png'
        plt.savefig(out_fname, dpi=200)

if args.lineout:
    '''
    Lineouts require a list of variables and a list of times to plot the data at.
    Multiple variables create axis stacked on top of each other, sharing the x-axis on a single figure.
    Example:
        $ python plot.py file_name --lineout Pres Rho 1 2 3 4 10
        Would plot Pressure and Density lineouts of the data from file_name at times 1, 2, 3, 4, and 10 nanoseconds.
    '''
    variables = []
    times = []
    for v in args.lineout:  # Go through all inputs to get variables and times
        if is_float(v):  # Times are floats
            times.append(float(v))
        else:  # Variables are string abbreviations of Hyades variables
            if v not in ('Pres', 'Rho', 'Rho0', 'U', 'Te', 'Ti', 'Tr'):
                error_string = 'Variable of interest required for lineout plots.\n' \
                               'Example: --lineout Pres 1 2 3\n' \
                               'Options for variable are {Pres, Rho, Rho0, U, Te, Ti, Tr}'
                raise ValueError(error_string)
            variables.append(v)
    fig, ax = static_graphics.lineout(abs_path, variables, times, coordinate_system=coordinate_system)
    if args.title:
        ax.set_title(' '.join(args.title))
    if args.save:
        out_fname = f'{base_out_filename} {" ".join(variables)} lineout.png'
        save_figure(out_fname)
        # plt.savefig(out_fname, dpi=200)

if args.target:
    '''Target diagrams only use the required filename'''
    fig, ax = static_graphics.visualize_target(abs_path)
    if args.title:
        ax.set_title(' '.join(args.title))
    if args.save:
        out_fname = f'{base_out_filename} Target Design.png'
        plt.savefig(out_fname, dpi=200)

if args.shock or (isinstance(args.shock, list) and len(args.shock) == 0):
    if isinstance(args.shock, list) and len(args.shock) == 0:
        interpolation_mode = 'Cubic'
    else:
        interpolation_mode = args.shock
    '''Shock Velocity plots require the filename and an interpolation mode'''
    if len(args.shock) == 1:
        args.shock = args.shock[0]
    fig, ax = static_graphics.plot_shock_velocity(abs_path, interpolation_mode)
    if args.title:
        ax.set_title(' '.join(args.title))
    if args.save:
        out_fname = f'{base_out_filename} {args.shock} Us.png'
        plt.savefig(out_fname, dpi=200)

if not args.quiet:
    plt.show()

if args.quiet and (not args.save):
    print('Selection did not display or save the graphics. See --help for more info.')

# Below is the best line of Python I've ever written
is_only_filename = not any([getattr(args, arg) for arg in vars(args) if not arg == 'filename'])
if is_only_filename:
    print('Whoops! No graphics were specified.'
          'Try adding one of the options to plot a figure. See --help for more info.')
