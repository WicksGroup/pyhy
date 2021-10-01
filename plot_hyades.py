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

Todo:
    * handle case in lineout where the user forgets to put in a variable
    * see if June wants the 2 separate y-axis plots so show two different variables at the same time
    * add custom title option
    * add a useful help message for lineout

"""
import os
import argparse
import matplotlib.pyplot as plt
from graphics import hyades_graphics_static


parser = argparse.ArgumentParser(prog='plot_hyades.py',
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 description='''A command line interface to plot common types of Hyades graphics.
                                 
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
''',
epilog='''\
                      ___      _  _      
                     | _ \_  _| || |_  _ 
                     |  _/ || | __ | || |
                     |_|  \_, |_||_|\_, |
                          |__/      |__/ 
Developed by the Wicks' Lab at JHU.                                                   
'''
                                 )


parser.add_argument('filename', type=str,
                    help='Name of the Hyades run to be plotted. Does not require file extension.')
parser.add_argument('-XT', choices=['Pres', 'U', 'Rho', 'Te', 'Tr', 'Ti'], nargs='+',
                    help='Plot each variable on an XT diagram')
parser.add_argument('-lo', '--lineout', nargs='+',
                    help='Line description')
parser.add_argument('-target', action='store_true',
                    help='Toggle to plot the target design. Works best on targets with wide layers.')
parser.add_argument('-shock', choices=['L', 'R', 'Avg', 'difference', 'all'], nargs='+',
                    help='Toggle to plot the Shock Velocity.'
                         ' Must select how to index the Particle Velocity with L, R, Avg (Average), All, Difference (L - R).')

parser.add_argument('-s', '--save', action='store_true',
                    help='Toggle to save all graphics after they are closed.')
parser.add_argument('-q', '--quiet', action='store_true',
                    help='Toggle to hide the graphics.'
                         ' Recommend use with --save for saving files without viewing')

args = parser.parse_args()

abs_path = './data/' + args.filename
if args.XT:
    for var in args.XT:
        fig, ax = hyades_graphics_static.xt_diagram(abs_path, var)
        if args.save:
            out_fname = f'{os.path.basename(args.filename)} {var} XT.png'
            plt.savefig(out_fname, dpi=200)

if args.lineout:
    var = args.lineout[0]
    times = [float(t) for t in args.lineout[1:]]
    fig, ax = hyades_graphics_static.lineout(abs_path, var, times)
    if args.save:
        out_fname = f'{os.path.basename(args.filename)} {var} lineout.png'
        plt.savefig(out_fname, dpi=200)

if args.target:
    fig, x = hyades_graphics_static.visualize_target(abs_path)
    if args.save:
        out_fname = f'{os.path.basename(args.filename)} Target Design.png'
        plt.savefig(out_fname, dpi=200)

if args.shock:
    if len(args.shock) == 1:
        args.shock = args.shock[0]
    fig, ax = hyades_graphics_static.plot_shock_velocity(abs_path, args.shock)
    if args.save:
        out_fname = f'{os.path.basename(args.filename)} {args.shock} Us.png'
        plt.savefig(out_fname, dpi=200)

if not args.quiet:
    plt.show()

if args.quiet and (not args.save):
    print('Selection did not display or save the graphics.')

# Below is the best line of Python I've ever written
is_only_filename = not any([getattr(args, arg) for arg in vars(args) if not arg == 'filename'])
if is_only_filename:
    print('Whoops! No graphics were specified.'
          'Try adding one of the options to plot a figure. See --help for more info.')
