"""Command line interface to animate Hyades

Note:
    Save feature requires ffmpeg installed.


"""
import os
import argparse
import matplotlib.pyplot as plt
from graphics.animated_eulerian import eulerian_animation
from graphics.animated_histograms import histogram_animation
from graphics.animated_lineout import lineout_animation


description = '''A command line interface to make simple animations of Hyades runs.

Options to animate the Eulerian position of the run, distributions
of a variable (with inset lineout), or the lineout of any variable
on its own.

Using --save requires ffmpeg. Currently, there is no alternative.

Examples:
    If you already ran the simulation diamond_decay, the following
    line would animate the distribution of pressures in the sample
        $ python animated_hyades.py diamond_decay -l Pres
    
    The following line would make an Eulerian space animation, and
    color the animation using the Particle Velocity at each point.
    The extensions --save and --quiet are combined into -sq so the
    graphics would be saved and would not be displayed.
        $ python animated_hyades.py diamond_decay -e U -sq
'''
epilog = '''
                      ___      _  _      
                     | _ \_  _| || |_  _ 
                     |  _/ || | __ | || |
                     |_|  \_, |_||_|\_, |
                          |__/      |__/ 
               Developed by the Wicks Lab at JHU
'''

parser = argparse.ArgumentParser(prog='animate_hyades.py',
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 description=description,
                                 epilog=epilog
                                 )

parser.add_argument('filename', type=str,
                    help='Name of the Hyades run to be plotted. Does not require file extension.')
parser.add_argument('-e', '--eulerian',
                    help='Animate the sample moving through Eulerian space. Colors the sample with a variable.')
parser.add_argument('-g', '--histogram',
                    help='Animate the distribution of a variable over time.')
parser.add_argument('-l', '--lineout',
                    help='Animate a lineout of a variable over time.')

parser.add_argument('-s', '--save', nargs='?', const=12,
                    help='* Requires ffmpeg installed * '
                         'Saves all graphics at specified frames per second (default: 12 fps). '
                         'Saving long animations may take a couple minutes.')
parser.add_argument('-q', '--quiet', action='store_true',
                    help='Toggle to hide the graphics.'
                         ' Recommend use with --save for saving files without viewing.')

args = parser.parse_args()
# End parser

abs_path = os.path.join('./data/', os.path.splitext(args.filename)[0])
base_save_filename = os.path.join('./data', os.path.splitext(args.filename)[0], os.path.splitext(args.filename)[0])

if args.eulerian:
    animation = eulerian_animation(abs_path, args.eulerian)
    if args.save:
        save_filename = f'{base_save_filename} {args.eulerian} eulerian.mp4'
        print(f'Saving {save_filename}...')
        animation.save(save_filename, fps=args.save)
        print('Saved.')

if args.histogram:
    animation = histogram_animation(abs_path, args.histogram)
    if args.save:
        save_filename = f'{base_save_filename} {args.histogram} histogram.mp4'
        print(f'Saving {save_filename}...')
        animation.save(save_filename, fps=args.save)
        print('Saved.')

if args.lineout:
    animation = lineout_animation(abs_path, args.lineout)
    if args.save:
        save_filename = f'{base_save_filename} {args.lineout} lineout.mp4'
        print(f'Saving {save_filename}...')
        animation.save(save_filename, fps=args.save)
        print('Saved.')

if not args.quiet:
    plt.show()

if args.quiet and (not args.save):
    print('Selection did not display or save the graphics. See --help for more info.')

# Below is the best line of Python I've ever written
is_only_filename = not any([getattr(args, arg) for arg in vars(args) if not arg == 'filename'])
if is_only_filename:
    print('Whoops! No graphics were specified.'
          'Try adding one of the options to plot a figure. See --help for more info.')
