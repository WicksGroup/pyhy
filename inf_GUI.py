"""A GUI used to create the .inf files for Hyades simulations.

The GUI does **not** require a local installation of Hyades to write a .inf.
The `Run Hyades` button **does** require a local installation of Hyades to work.

Example:
    Start the GUI with the following line::

    $ python inf_GUI.py

Todo:
    * implement the new cdf reader
"""
import os
import pathlib
import matplotlib
import pandas as pd
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import *
from tools.inf_GUI_helper import Layer, InfWriter, LayerTab
from tools import hyades_runner


import numpy as np
os.chdir(pathlib.Path(__file__).parent.absolute())
matplotlib.use("TkAgg")


class InputGUI:
    """Create a GUI to format Hyades .inf files.

    Takes in many different parameters, including simulation variables, Pressure / Temperature / Laser drives, and
    material properties then formats it all into a .inf for Hyades. Also has options to run Hyades and the optimizer.

    Note:
        Using a thermal model requires you have the Hyades formatted thermal conductivity table in the same directory
        as the .inf. Specifying the thermal model requires the filename in the .inf, so you will have to manually edit
        the .inf with the local filename.

        Specifying a constant thermal conductivity does not require any external tables.

        This GUI does not provide control over all possible Hyades inputs. See the Hyades Users' Guide for complete
        documentation.

        The `Write Inf` button will overwrite files with the same name without warning.
        Always double check your filenames.

    """
    def __init__(self, root):
        """Create GUI variables and format the entire thing. This generates the GUI window."""
        self.tabs = []
        self.n_layers = IntVar()
        self.time_max = DoubleVar()
        self.time_step = DoubleVar()
        self.pres_fname = StringVar()
        self.temp_fname = StringVar()
        self.laser_fname = StringVar()
        self.laser_wavelength = DoubleVar()
        self.laser_spot_diameter = DoubleVar()
        self.out_dir = StringVar()
        self.out_fname = StringVar()
        self.is_xray_probe = IntVar()  # binary 0/1 for False/True
        self.xray_probe_start = DoubleVar()
        self.xray_probe_stop = DoubleVar()
        self.source_multiplier = DoubleVar()
        self.time_of_interestS = DoubleVar(root)
        self.time_of_interestE = DoubleVar(root)
        self.exp_file_name = StringVar(root)
        self.save_excel = IntVar()
        self.save_excel.set(0)

        # set up the window and root of all the widgets
        root.title('Hyades Input File GUI')
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        # parent most widgets will use
        self.parent = ttk.Frame(root, padding=' 3 3 12 12').grid(column=0, row=0, sticky='NW')

        row = 1
        # Add titles
        Label(self.parent, text='Hyades Input File GUI',
              font=('Arial', 16),).grid(column=1, row=row, columnspan=4, pady=(5, 0))
        row += 1
        ttk.Label(self.parent, text='* are required',).grid(column=1, row=row, columnspan=4, pady=(0, 5))
        row += 1

        def simulate():
            """Function to run all .inf files in a directory for Run Hyades button"""
            inf_path = 'data/inf/'
            final_destination = '../data/'
            if self.save_excel.get() == 1:
                copy_data_to_excel = True
            else:
                copy_data_to_excel = False

            title = 'Hyades Input File GUI'
            files = [f for f in os.listdir(inf_path) if f.endswith('.inf')]
            message = f'Do you want to start {len(files)} Hyades Simulations?'
            message += f'\nInput files in {inf_path}: {", ".join(files)}'
            if len(files) == 0:
                messagebox.showerror(title, f'Found no .inf files in {inf_path}')
            elif messagebox.askyesno(title, message):
                hyades_runner.batchRunHyades(inf_path, final_destination, copy_data_to_excel)

        # time_max and time_step entries
        ttk.Label(self.parent, text='*Simulation Time (ns)').grid(row=row, column=1, sticky='NW')
        ttk.Entry(self.parent, textvariable=self.time_max, width=7).grid(row=row, column=2, sticky='NW')
        # Run hyades button
        ttk.Button(self.parent, text='Run Hyades', command=simulate).grid(row=row, column=3, sticky='NW')

        # Entry for visar for optimizer
        ttk.Label(self.parent, text='Visar Data Filename').grid(row=row, column=4, sticky='NW')
        ttk.Entry(self.parent, textvariable=self.exp_file_name, width=15).grid(row=row, column=5, sticky='NW')
        row += 1

        # Post Processor time step
        ttk.Label(self.parent, text='*Time Step (ns)').grid(row=row, column=1, sticky='NW')
        ttk.Entry(self.parent, textvariable=self.time_step, width=7).grid(row=row, column=2, sticky='NW')
        # Write the .inf button
        ttk.Button(self.parent, text='Write inf', command=self.write_out_props).grid(row=row, column=3, sticky='NW')
        # Time of interest
        ttk.Label(self.parent, text='Time of Interest Start (ns)').grid(row=row, column=4, sticky='NW')
        # ttk.Label(self.parent, text='start:').grid(row=row, column=6, sticky='NW')
        ttk.Entry(self.parent, textvariable=self.time_of_interestS, width=7).grid(row=row, column=5, sticky='NW')
        row += 1

        # out_fname entry
        ttk.Label(self.parent, text='*Output inf Name: ').grid(row=row, column=1, sticky='NW')
        ttk.Entry(self.parent, textvariable=self.out_fname, width=24).grid(row=row, column=2, columnspan=2, sticky='NW')

        # Time of interest end
        ttk.Label(self.parent, text='Time of Interest End (ns)').grid(row=row, column=4, sticky='NW')
        ttk.Entry(self.parent, textvariable=self.time_of_interestE, width=7).grid(row=row, column=5, sticky='NW')
        row += 1

        # Checkbutton to save a copy of all the hyades data as an excel sheet. Default False.
        ttk.Checkbutton(self.parent, text="Save Excel copy of output",
                        variable=self.save_excel).grid(row=row, column=2, sticky="NW")

        # Run Optimizer button
        ttk.Button(root, text='Run optimizer', command=self.run_optimizer).grid(row=row, column=4, sticky='NW')
        row += 1

        # Add the number of layers entry and button
        pad_y = (5, 0)
        ttk.Label(self.parent, text='*Number of layers').grid(column=1, row=row, sticky='NW', pady=pad_y)
        ttk.Entry(self.parent, textvariable=self.n_layers, width=7).grid(column=2, row=row, sticky='NW', pady=pad_y)
        ttk.Button(self.parent, text='Generate layers',
                   command=self.generate_layers).grid(column=3, row=row, sticky='NW', pady=pad_y)

        '''functions for the tv file and directory selection'''
        def select_pres_file():
            pres_filename = filedialog.askopenfilename(initialdir='../data', title='Select Pressure Profile')
            self.pres_fname.set(pres_filename)
            self.pres_label_variable.set(os.path.basename(pres_filename))

        def select_temp_file():
            temp_filename = filedialog.askopenfilename(initialdir='../data', title='Select Temperature Profile')
            self.temp_fname.set(temp_filename)
            self.temp_label_variable.set(os.path.basename(temp_filename))

        def select_laser_file():
            laser_filename = filedialog.askopenfilename(initialdir='../data', title='Select Laser Profile')
            self.laser_fname.set(laser_filename)
            self.laser_label_variable.set(os.path.basename(laser_filename))

        def select_dir():
            out_dir = filedialog.askdirectory(initialdir='../data/inf', title='Select .inf destination')
            self.out_dir.set(out_dir)

        row += 10

        ttk.Label(self.parent, text='Everything below is optional').grid(column=1, row=row, columnspan=4,
                                                                         sticky='N', pady=(5, 5))
        row += 1

        # Optional X-ray probe time
        pad_y = (0, 0)
        Label(self.parent, text='X-Ray Start Time (ns)').grid(row=row, column=1, sticky='NE', pady=pad_y)
        ttk.Entry(self.parent, textvariable=self.xray_probe_start, width=7).grid(row=row, column=2, sticky='NW')
        Label(self.parent, text='X-Ray Stop Time (ns)').grid(row=row, column=3, sticky='NE', pady=pad_y)
        ttk.Entry(self.parent, textvariable=self.xray_probe_stop, width=7).grid(row=row, column=4, sticky='NW')
        row += 1

        # Select tv inputs from two column .txt files
        self.source_multiplier.set(1.0)
        Label(root, text='Source Multiplier').grid(row=row, column=1, sticky='NW',)
        ttk.Entry(root, textvariable=self.source_multiplier, width=7).grid(row=row, column=2, sticky='NW')
        Label(root, text='Source Multiplier applies to all inputs').grid(row=row, column=3, columnspan=2, sticky='NW')
        row += 1
        self.temp_label_variable = StringVar()
        self.temp_label_variable.set('None selected')
        Label(root, textvariable=self.temp_label_variable).grid(row=row, column=2, sticky='NW', pady=(5, 0))
        ttk.Button(root, text='Pick Temperature', command=select_temp_file).grid(row=row, column=1,
                                                                                 sticky='NW', pady=(5, 0))
        row += 1
        self.pres_label_variable = StringVar()
        self.pres_label_variable.set('None selected')
        Label(root, textvariable=self.pres_label_variable).grid(row=row, column=2, sticky='NW', pady=(0, 0))
        ttk.Button(root, text='Pick Pressure', command=select_pres_file).grid(row=row, column=1,
                                                                              sticky='NW', pady=(0, 0))

        self.is_optimize_pressure = IntVar()  # 0/1 for False/True
        ttk.Checkbutton(root, text='Set Pressure for Optimization',
                        variable=self.is_optimize_pressure).grid(column=3, columnspan=2, row=row, sticky='NW')
        row += 1
        self.laser_label_variable = StringVar()
        self.laser_label_variable.set('None selected')
        Label(root, textvariable=self.laser_label_variable).grid(row=row, column=2, sticky='NW', pady=(0, 0))
        ttk.Button(root, text='Pick Laser', command=select_laser_file).grid(row=row, column=1, sticky='NW', pady=(0, 0))
        row += 1
        # Additional Laser Parameters - these will be known from experiment
        Label(root, text='Laser Wavelength (nm)').grid(row=row, column=1, sticky='NE',)
        ttk.Entry(root, textvariable=self.laser_wavelength, width=7).grid(row=row, column=2, sticky='NW')
        Label(root, text='Laser Spot Diameter (mm)').grid(row=row, column=3, sticky='NE')
        ttk.Entry(root, textvariable=self.laser_spot_diameter, width=7).grid(row=row, column=4, sticky='NW')
        row += 1

        # Optionally select directory for inf
        pad_y = (5, 5)
        self.out_dir.set('./data/inf')
        Label(root, textvariable=self.out_dir).grid(row=row, column=2, sticky='NW', pady=pad_y)
        ttk.Button(root, text='Select .inf destination', command=select_dir).grid(row=row, column=1,
                                                                                  sticky='NW', pady=pad_y)
        row += 1

    def run_optimizer(self):
        print(self.exp_file_name.get(), self.time_of_interestE.get(), self.time_of_interestS.get())
        inf_path = 'data/inf/'
        files = [f for f in os.listdir(inf_path) if f.endswith('_setup.inf')]
        print(files)
        for f in files:
            print(pathlib.Path(f).parent.parent.parent.absolute())
            try:
                os.makedirs(f'../data/{f[0:-10]}')
            except:
                print(f'../data/{f[0:-10]} exists')
            print(f[0:-10])
            os.system(f'mv ..\data\inf\{f} ..\data\{f[0:-10]}\{f}')
            os.system(f'.\hyopRunner {self.exp_file_name.get()} {self.time_of_interestS.get()} {self.time_of_interestE.get()} {f[0:-10]}')

    def generate_layers(self):
        """Generate the layer options inside the GUI"""
        self.tabs = []  # reset layers so they dont keep appending
        notebook = ttk.Notebook(self.parent) # reset the notebook
        notebook.grid(column=1, row=8, columnspan=9, sticky='NWE')
        for i in range(self.n_layers.get()):
            frame = ttk.Frame(notebook)
            tab = LayerTab(frame)
            tab.add_props()
            self.tabs.append(tab)
            notebook.add(frame, text=f'Layer {i+1}')

    def display(self):
        """Debugging function to display all variables in all layers"""
        for i, T in enumerate(self.tabs):
            print(f'Layer {i}')
            for k in vars(T):
                if k == 'parent' or k == 'row':
                    continue
                else:
                    print(f'{k}: {vars(T)[k].get()}')
            print()

    def get_tv(self, fname, var):
        """Read two column csv for tv inputs (in SI units) and convert them to Hyades units (cgs).

        Note:
            Temperatures are converted from degrees Kelvin to kiloElectron Volts.
            Pressures are converted from gigapascals to dynes / cm^2
            Laser Power (Terawatts) is converted to an intensity (ergs / second) by dividing by the spot size
            and multiplying by the unit conversion to get terajoules to ergs

        """
        df = pd.read_csv(fname, skiprows=1)
        time_column = df.columns[0]
        var_column = df.columns[1]
        if 'te' in var.lower():
            scale = 1 / 11604000  # degrees kelvin to kiloelectron volts
        elif 'pres' in var.lower():
            scale = 1e10  # GPa to dynes / cm^2
        elif 'laser' in var.lower():
            laser_spot_diameter = self.laser_spot_diameter.get() / 10  # convert mm to cm
            spot_area = np.pi * (laser_spot_diameter / 2)**2  # pi * r^2
            scale = (1 / spot_area) * 1e19  # TeraWatts to ergs / sec
        else:
            raise Exception(f'Unknown variable requested from get_tv: {var}')

        tv_lines = []
        for t, v in zip(df[time_column], df[var_column]):
            line = f'tv {t * 1e-9:.2e} {v * scale:.2e}'
            tv_lines.append(line)

        return tv_lines

    def write_out_props(self):
        """Convert the GUI properties to a Layer object then pass all the Layers to the InfWriter"""
        layers = []
        for i, T in enumerate(self.tabs):
            prop_dict = {}  # scraps all the properties out of GUI
            for prop in vars(T):
                if prop == 'parent' or prop == 'row':
                    continue
                else:
                    prop_dict[prop] = vars(T)[prop].get()
            i_layer = Layer(prop_dict)  # Layer class fills in missing layer info
            layers.append(i_layer)

        sim_props = {'time_max': self.time_max.get(),
                     'time_step': self.time_step.get(),
                     'sourceMultiplier': self.source_multiplier.get()
                     }

        if self.is_optimize_pressure.get() == 1:
            if not sum([L.is_material_of_interest for L in layers]) == 1:
                messagebox.showerror("Hyades Input File GUI",
                                     "Exactly one layer must be selected as Material of Interest when optimizing")
                raise Exception("Exactly one layer must be selected as Material of Interest when optimizing")
            if not sum([L.is_shock_material_of_interest for L in layers]) < 2:
                messagebox.showerror("Hyades Input File GUI",
                                     "No more than 1 layer can be selected as Shock MOI when optimizing")
                raise Exception("No more than 1 layer can be selected as Shock MOI when optimizing")
            sim_props['tvPres'] = ['TV_PRES']
        elif ('None' not in self.pres_fname.get()) and (self.pres_fname.get()):
            sim_props['tvPres'] = self.get_tv(self.pres_fname.get(), 'pres')

        if ('None' not in self.temp_fname.get()) and (self.temp_fname.get()):
            sim_props['tvTemp'] = self.get_tv(self.temp_fname.get(), 'temp')
        if ('None' not in self.laser_fname.get()) and (self.laser_fname.get()):
            sim_props['tvLaser'] = self.get_tv(self.laser_fname.get(), 'laser')
            sim_props['laserWavelength'] = self.laser_wavelength.get()
        if (self.xray_probe_stop.get() != 0) and (self.xray_probe_start.get() != 0):
            sim_props['xray_probe_start'] = self.xray_probe_start.get()
            sim_props['xray_probe_stop'] = self.xray_probe_stop.get()

        writer = InfWriter()
        writer.add_layers(layers, sim_props)  # put layers & simulation properties in the InfWriter
        # writer.display()  # displays a formatted inf file

        if self.out_dir.get() == 'Select Directory':
            if os.path.isdir('./data/inf'):
                out_dir = './data/inf'
            elif os.path.isdir('./data/inf'):
                out_dir = './data/inf'
            else:
                out_dir = './'
        else:
            out_dir = self.out_dir.get()

        writer.write_out(os.path.join(out_dir, self.out_fname.get()))


if __name__ == "__main__":
    root = Tk()
    GUI = InputGUI(root)
    root.mainloop()
