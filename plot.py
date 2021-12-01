"""Command line interface to plot various Hyades figures.

Notes:
    See --help for usage.

"""
import os
import argparse
import matplotlib.pyplot as plt
from graphics import static_graphics


def is_float(string):
    """Returns True if a string can be converted to a float, otherwise False"""
    try:
        float(string)
        return True
    except ValueError:
        return False


description = '''A command line interface to plot common types of Hyades graphics.
                                 
This is a Python script to generate common plots from Hyades data.
It can create many different static graphics, such as XT Diagrams,
diagram of the target design, and/or a plot of the shock velocity.
Please note the shock velocity function is only designed for shock
simulations and may not yield useful results for ramp compression.

--save uses default names and overwrites files with the same name.

Examples:
    If you already ran a simulation named 'diamond_decay' then the
    following line would create XT Diagrams for Pressure, Density,
    and Particle Velocity, each in their own pop up window:
        $ python plot.py diamond_decay -XT Pres Rho U
        
    The following line plots the pressure over the whole sample at
    the times in the data closest to 1, 2, 3.4, 5 and 9 nanoseconds:
        $ python plot.py diamond_decay -l Pres 1 2 3.4 5 9
    
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
parser.add_argument('-XT', choices=['Pres', 'U', 'Rho', 'Rho0', 'Te', 'Tr', 'Ti'], nargs='+',
                    help='Plot each variable on an XT diagram.'
                         '\nMultiple selections are allowed and will be plotted on their own figure.')
parser.add_argument('-l', '--lineout', nargs='+',
                    help='Plot lineouts of a variable of interest at multiple times')
parser.add_argument('-t', '--target', action='store_true',
                    help='Toggle to plot the target design. Works best on targets with wide layers.')
parser.add_argument('-k', '--shock', nargs='*',
                    choices=['L', 'R', 'Avg', 'difference', 'Cubic', 'all'],
                    help='Toggle to plot the Shock Velocity.'
                         ' Optionally select how to index Particle Velocity in Shock calculation (default: Cubic).'
                         '\nMultiple selections are allowed and will be plotted on a single figure')
parser.add_argument('-c', '--coordinate', choices=('e', 'eulerian', 'l', 'lagrangian'),
                    help='Coordinate system to use on the x-axis of XT Diagrams and Lineouts. (Default: Lagrangian)'
                         'Only applies to lineouts and XT diagrams.')
parser.add_argument('--title', type=str, nargs='+',
                    help='Sets a custom title on *all* figures. Recommended use when only one plot is specified.')
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

if args.XT:
    '''XT Diagrams require a variable of interest. Multiple variables are plotted on separate figures.
    Example:
        $ python plot.py file_name -XT Pres U
        Would create one XT Diagram for the Pressure and one for the Particle Velocity, each in their own figure.
    '''
    for var in args.XT:
        fig, ax = static_graphics.xt_diagram(abs_path, var, coordinate_system=coordinate_system)
        if args.title:
            ax.set_title(' '.join(args.title))
        if args.save:
            out_fname = f'{base_out_filename} {var} XT.png'
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
        plt.savefig(out_fname, dpi=200)

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
