"""Command line interface to plot various Hyades figures.

Notes:
    See --help for usage.
    
Examples:
    If you already ran a Hyades simulation named `diamond_decay`, the following would generate XT Diagrams for 
    the Pressure, Density, and Particle Velocity, each in their own pop up window::

    $ python plot_hyades.py diamond_decay -XT Pres Rho U
    
    To save graphics without displaying them, combine the `--save` and `--quiet` commands. The following would
    plot the target design and save the figure without displaying it::

    $ python plot_hyades.py diamond_decay -target -sq

    The following line plots the pressure over the whole sample at
    the times in the data closet to 1, 2, 3, 5, and 9 nanoseconds::

    $ python plot_hyades.py diamond_decay -lo Pres 1 2 3 5 9

Todo:
    * Add the dueling axis option to the lineouts

"""
import os
import argparse
import matplotlib.pyplot as plt
from graphics import static_graphics


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
        $ python plot_hyades.py diamond_decay -XT Pres Rho U
    
    To save graphics without displaying them, combine the `--save`
    and `--quiet` commands. The following would create a figure of
    the target design and save the figure without displaying it:
        $ python plot_hyades.py diamond_decay -target -sq
    
    The following line plots the pressure over the whole sample at
    the times in the data closet to 1, 2, 3, 5, and 9 nanoseconds:
        $ python plot_hyades.py diamond_decay -lo Pres 1 2 3 5 9
'''
epilog = '''
                      ___      _  _      
                     | _ \_  _| || |_  _ 
                     |  _/ || | __ | || |
                     |_|  \_, |_||_|\_, |
                          |__/      |__/ 
               Developed by the Wicks Lab at JHU
'''

parser = argparse.ArgumentParser(prog='plot_hyades.py',
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 description=description,
                                 epilog=epilog
                                 )

parser.add_argument('filename', type=str,
                    help='Name of the Hyades run to be plotted. Does not require file extension.')
parser.add_argument('-XT', choices=['Pres', 'U', 'Rho', 'Te', 'Tr', 'Ti'], nargs='+',
                    help='Plot each variable on an XT diagram')
parser.add_argument('-l', '--lineout', nargs='+',
                    help='Plot lineouts of a single variable of interest at multiple times')
parser.add_argument('-t', '--target', action='store_true',
                    help='Toggle to plot the target design. Works best on targets with wide layers.')
parser.add_argument('-k', '--shock', choices=['L', 'R', 'Avg', 'difference', 'all'], nargs='+',
                    help='Toggle to plot the Shock Velocity.'
                         ' Must select how to index the Particle Velocity with L, R, Avg (Average), All, Difference (L - R).')

parser.add_argument('-t', '--title', type=str, nargs='+',
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

if args.XT:
    for var in args.XT:
        fig, ax = static_graphics.xt_diagram(abs_path, var)
        if args.title:
            ax.set_title(' '.join(args.title))
        if args.save:
            out_fname = f'{base_out_filename} {var} XT.png'
            plt.savefig(out_fname, dpi=200)

if args.lineout:
    var = args.lineout[0]
    if var not in ('Pres', 'Rho', 'U', 'Te', 'Ti', 'Tr'):
        error_string = 'Variable of interest required for lineout plots.\n' \
                       'Example: --lineout Pres 1 2 3\n' \
                       'Options for variable are {Pres, Rho, U, Te, Ti, Tr}'
        raise ValueError(error_string)
    times = [float(t) for t in args.lineout[1:]]
    fig, ax = static_graphics.lineout(abs_path, var, times)
    if args.title:
        ax.set_title(' '.join(args.title))
    if args.save:
        out_fname = f'{base_out_filename} {var} lineout.png'
        plt.savefig(out_fname, dpi=200)

if args.target:
    fig, ax = static_graphics.visualize_target(abs_path)
    if args.title:
        ax.set_title(' '.join(args.title))
    if args.save:
        out_fname = f'{base_out_filename} Target Design.png'
        plt.savefig(out_fname, dpi=200)

if args.shock:
    if len(args.shock) == 1:
        args.shock = args.shock[0]
    fig, ax = static_graphics.plot_shock_velocity(abs_path, args.shock)
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
