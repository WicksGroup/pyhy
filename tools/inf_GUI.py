#!/usr/bin/env python3
import os
import pathlib
os.chdir(pathlib.Path(__file__).parent.absolute())
import matplotlib
matplotlib.use("TkAgg")
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import *
from inf_GUI_helper import Layer, inf_writer, myTab
import datetime
import asyncio
import pandas as pd
import hyades_runner
import numpy as np
# import excel_writer # imports fine
# import hyades_output_reader # imports fine

class myGUI:
    '''Big GUI Class that houses everything'''
    
    def __init__(self, root):
        # intialize some variables
        self.tabs = []
        self.nLayers = IntVar()
        self.timeMax, self.timeStep = DoubleVar(), DoubleVar()
        self.presfname, self.tempfname = StringVar(), StringVar()
        self.laserfname = StringVar()
        self.laser_wavelength    = DoubleVar()
        self.laser_spot_diameter = DoubleVar()
        self.outDir     = StringVar()
        self.outfname   = StringVar()
        self.isXrayProbe    = IntVar()      # binary 0/1 for False/True
        self.XrayProbeStart = DoubleVar()
        self.XrayProbeStop  = DoubleVar()        
        self.source_multiplier = DoubleVar()
        self.time_of_interestS = DoubleVar(root)
        self.time_of_interestE = DoubleVar(root)
        self.exp_file_name = StringVar(root)
        
        # set up the window and root of all the widgets
        root.title('Hyades Input File GUI')
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        
        # parent most widgets will use
        self.parent = ttk.Frame(root, padding=' 3 3 12 12').grid(column=0, row=0, sticky='NW')
        
        row = 1
        # Add titles
        Label(self.parent, text='Hyades Input File GUI',
                  font=('Arial',16),).grid(column=1, row=row, columnspan=4, pady=(5,0))
        row += 1
        ttk.Label(self.parent, text='* are required',).grid(column=1, row=row, columnspan=4, pady=(0,5))
        row += 1
        
        self.save_excel = IntVar()
        self.save_excel.set(1)
        def simulate():
            '''Function to run all .inf files in a directory for Run Hyades button'''
            inf_path = '../data/inf/'
            final_destination = '../data/'
            if self.save_excel.get() == 1:
                copy_data_to_excel = True
            else:
                copy_data_to_excel = False

            title ='Hyades Input File GUI'
            files = [f for f in os.listdir(inf_path) if f.endswith('.inf')]
            message = f'Do you want to start {len(files)} Hyades Simulations?'
            message += f'\nInput files in {inf_path}: {", ".join(files)}'
            if len(files) == 0:
                messagebox.showerror(title, f'Found no .inf files in {inf_path}')
            elif messagebox.askyesno(title, message):
                hyades_runner.batchRunHyades(inf_path, final_destination, copy_data_to_excel)
        # timeMax and timeStep entries
        ttk.Label(self.parent, text='*Simulation Time (ns)').grid(row=row, column=1, sticky='NW')
        ttk.Entry(self.parent, textvariable=self.timeMax, width=7).grid(row=row, column=2,sticky='NW')
        # Run hyades button
        ttk.Button(self.parent, text='Run Hyades', command=simulate).grid(row=row, column=3, sticky='NW')
        # Checkbutton to save a copy of all the hyades data as an excel sheet. Default True.
        ttk.Checkbutton(self.parent, text="Save Excel copy",
                        variable=self.save_excel).grid(row=row, column=4, sticky="NW")
        #Entry for visar for optimizer
        ttk.Label(self.parent, text='t-up Datafile Name').grid(row=row, column=5, sticky='NW')
        ttk.Entry(self.parent, textvariable=self.exp_file_name, width=7).grid(row=row, column=6,sticky='NW')
        row += 1

        # Post Processor time step
        ttk.Label(self.parent, text='*Time Step (ns)').grid(row=row, column=1, sticky='NW')
        ttk.Entry(self.parent, textvariable=self.timeStep, width=7).grid(row=row, column=2, sticky='NW')
        # Write the .inf button
        ttk.Button(self.parent, text='Write inf',command=self.write_out_props).grid(row=row, column=3, sticky='NW')
        #Time of interest
        ttk.Label(self.parent, text='time of interest').grid(row=row, column=5, sticky='NW')
        ttk.Label(self.parent, text='start:').grid(row=row, column=6, sticky='NW')
        ttk.Entry(self.parent, textvariable= self.time_of_interestS, width=7).grid(row=row, column=7,sticky='NW')
        row += 1
        
        # Outfname entry
        ttk.Label(self.parent, text='*Output inf Name: ').grid(row=row, column=1, sticky='NW')
        ttk.Entry(self.parent, textvariable=self.outfname, width=24).grid(row=row, column=2, columnspan=2, sticky='NW')
        
        #time of interest end
        ttk.Label(self.parent, text='end:').grid(row=row, column=6, sticky='NW')
        ttk.Entry(self.parent, textvariable=self.time_of_interestE, width=7).grid(row=row, column=7,sticky='NW')
        row += 1
        
        


        # add the number of layers entry and button
        pady = (5, 0)
        ttk.Label(self.parent, text='*Number of layers').grid(column=1, row=row, sticky='NW', pady=pady)
        ttk.Entry(self.parent, textvariable=self.nLayers, width=7).grid(column=2, row=row, sticky='NW', pady=pady)
        ttk.Button(self.parent, text='Generate layers',
                   command=self.generate_layers).grid(column=3, row=row, sticky='NW', pady=pady)        
        #Run Optimizer button
        ttk.Button(root, text='Run optimizer', command= self.RunOptimizer).grid(row=row, column=5, sticky='NW')
        '''functions for the tv file and directory selection'''
        def selectPresFile():
            presfname =  filedialog.askopenfilename(initialdir='../data', title='Select Pressure Profile')
            self.presfname.set(presfname)
            self.pres_label_variable.set(os.path.basename(presfname))
            
        def selectTempFile():
            tempfname = filedialog.askopenfilename(initialdir ='../data', title='Select Temperature Profile')
            self.tempfname.set(tempfname)
            self.temp_label_variable.set(os.path.basename(tempfname))
            
        def selectLaserFile():
            laserfname = filedialog.askopenfilename(initialdir='../data', title='Select Laser Profile')
            self.laserfname.set(laserfname)
            self.laser_label_variable.set(os.path.basename(laserfname))
            
        def selectDir():
            outDir = filedialog.askdirectory(initialdir='../data/inf', title='Select .inf destination')
            self.outDir.set(outDir)
        
        row += 10
        
        ttk.Label(self.parent, text='Everything below is optional').grid(column=1, row=row, columnspan=4, sticky='N', pady=(5,5))
        row += 1
        
        
        # optional X-ray probe time
        pady = (0, 0)
        Label(self.parent, text='X-Ray Start Time (ns)').grid(row=row, column=1, sticky='NE', pady=pady)
        ttk.Entry(self.parent, textvariable=self.XrayProbeStart, width=7).grid(row=row, column=2, sticky='NW')
        Label(self.parent, text='X-Ray Stop Time (ns)').grid(row=row, column=3, sticky='NE', pady=pady)
        ttk.Entry(self.parent, textvariable=self.XrayProbeStop, width=7).grid(row=row, column=4, sticky='NW')
        row += 1
        
        # select tv inputs from two column .txt files
        self.source_multiplier.set(1.0)
        Label(root, text='Source Multiplier').grid(row=row, column=1, sticky='NW',)
        ttk.Entry(root, textvariable=self.source_multiplier, width=7).grid(row=row, column=2, sticky='NW')
        Label(root, text='Source Multiplier applies to all inputs').grid(row=row, column=3, columnspan=2, sticky='NW')
        row += 1
        self.temp_label_variable = StringVar() 
        self.temp_label_variable.set('None selected')
        Label(root, textvariable=self.temp_label_variable).grid(row=row, column=2, sticky='NW', pady=(5,0))
        ttk.Button(root, text='Pick Temperature', command=selectTempFile).grid(row=row, column=1, sticky='NW', pady=(5,0))
        row += 1
        self.pres_label_variable = StringVar()
        self.pres_label_variable.set('None selected')
        Label(root, textvariable=self.pres_label_variable).grid(row=row, column=2, sticky='NW', pady=(0,0))
        ttk.Button(root, text='Pick Pressure', command=selectPresFile).grid(row=row, column=1, sticky='NW', pady=(0,0))

        self.is_optimize_pressure = IntVar() # 0/1 for False/True
        ttk.Checkbutton(root, text='Set Pressure for Optimization',
                        variable=self.is_optimize_pressure).grid(column=3, columnspan=2, row=row, sticky='NW')
        row += 1
        self.laser_label_variable = StringVar()
        self.laser_label_variable.set('None selected')
        Label(root, textvariable=self.laser_label_variable).grid(row=row, column=2, sticky='NW', pady=(0,0))
        ttk.Button(root, text='Pick Laser', command=selectLaserFile).grid(row=row, column=1, sticky='NW', pady=(0,0))
        row += 1
        # Additional Laser Parameters - these will be known from experiment
        Label(root, text='Laser Wavelength (nm)').grid(row=row, column=1, sticky='NE',)
        ttk.Entry(root, textvariable=self.laser_wavelength, width=7).grid(row=row, column=2, sticky='NW')
        Label(root, text='Laser Spot Diameter (mm)').grid(row=row, column=3, sticky='NE')
        ttk.Entry(root, textvariable=self.laser_spot_diameter, width=7).grid(row=row, column=4, sticky='NW')
        

        row += 1
        
        # Optionally select directory for inf
        pady = (5, 5)
        self.outDir.set('../data/inf')
        Label(root, textvariable=self.outDir).grid(row=row, column=2, sticky='NW', pady=pady)
        ttk.Button(root, text='Select .inf destination', command=selectDir).grid(row=row, column=1, sticky='NW', pady=pady)
        row += 1
        
    def RunOptimizer(self):
        print(self.exp_file_name.get(),self.time_of_interestE.get(),self.time_of_interestS.get())
        inf_path = '../data/inf/'
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
        # Add nLayers number of tabs to the notebook, each tab holding a 'Layer' object
        self.tabs = [] # reset layers so they dont keep appending
        notebook = ttk.Notebook(self.parent) # reset the notebook
        notebook.grid(column=1, row=8, columnspan=9, sticky='NWE')
        for i in range(self.nLayers.get()):
            frame = ttk.Frame(notebook)
            T = myTab(frame)
            T.add_props()
            self.tabs.append(T)
            notebook.add(frame, text=f'Layer {i+1}')

            
    def display(self):
        # display the contents of all the 'Layer' objects in self.tabs
        for i, T in enumerate(self.tabs):
            print(f'Layer {i}')
            for k in vars(T):
                if k=='parent' or k=='row':
                    continue
                else:
                    print(f'{k}: {vars(T)[k].get()}')
            print()
            
            
    def get_tv(self, fname, var):
        df = pd.read_csv(fname, skiprows=1)
        timeColumn = df.columns[0]
        varColumn  = df.columns[1]
        if 'te' in var.lower():
            scale = 1 / 11604000 # K to KeV
        elif 'pres' in var.lower():
            scale = 1e9 # GPa to dynes / cm^2
        elif 'laser' in var.lower():
            laser_spot_diameter = self.laser_spot_diameter.get() / 10  # convert mm to cm
            spot_area = np.pi * (laser_spot_diameter / 2)**2 # pi * r^2
            # We want laser intensity in the Hyades Simulation, but are experimentally given laser power
            # laser intensity = laser power / spot_area
            # this scale converts to laser intensity then to hyades units of intensity
            scale = (1 / spot_area) * 1e19 # TeraWatts to ergs / sec
            print('LASER TV SPOT AREA', spot_area)
            print('SCALE:', scale, 'SCALE / 1e19', scale/1e19)
        else:
            raise Exception(f'Unknown variable requested from get_tv: {var}')
        
        tv_lines = []
        for t, v in zip(df[timeColumn], df[varColumn]):
            line = f'tv {t * 1e-9:.2e} {v * scale:.2e}'
            tv_lines.append(line)

        return tv_lines
            
            
    def write_out_props(self):
        # convert the GUI properties to a Layer object,
        # then pass all the Layer objects into the inf_writer
        layers = []
        for i, T in enumerate(self.tabs):
            prop_dict = {} # scraps all the properties out of GUI
            for prop in vars(T):
                if prop=='parent' or prop=='row':
                    continue
                else:
                    prop_dict[prop] = vars(T)[prop].get()
            iLayer = Layer(prop_dict) # Layer class fills in missing layer info
            layers.append( iLayer )
        
        simProps = {'timeMax' :self.timeMax.get(),
                    'timeStep':self.timeStep.get(),
                    'sourceMultiplier':self.source_multiplier.get()
                   }
                    
        if self.is_optimize_pressure.get() == 1:
            if not sum([L.isMaterialOfInterest for L in layers]) == 1:
                messagebox.showerror("Hyades Input File GUI", "Exactly one layer must be selecter as Material of Interest when optimizing")
                raise Exception("Exactly one layer must be selecter as Material of Interest when optimizing")
            if not sum([L.isShockMaterialOfInterest for L in layers]) < 2:
                messagebox.showerror("Hyades Input File GUI", "No more than 1 layer can be selected as Shock MOI when optimizing")
                raise Exception("No more than 1 layer can be selected as Shock MOI when optimizing")
            simProps['tvPres'] = ['TV_PRES']
        elif (not 'None' in self.presfname.get()) and (self.presfname.get()):
            simProps['tvPres'] = self.get_tv(self.presfname.get(), 'pres')

        if (not 'None' in self.tempfname.get()) and (self.tempfname.get()):
            simProps['tvTemp'] = self.get_tv(self.tempfname.get(), 'temp')
        if (not 'None' in self.laserfname.get()) and (self.laserfname.get()):
            simProps['tvLaser'] = self.get_tv(self.laserfname.get(), 'laser')
            simProps['laserWavelength'] = self.laser_wavelength.get()
        if (self.XrayProbeStop.get() != 0) and (self.XrayProbeStart.get() != 0):
            simProps['XrayProbeStart'] = self.XrayProbeStart.get()
            simProps['XrayProbeStop']  = self.XrayProbeStop.get()
        
        writer = inf_writer()
        writer.add_layers(layers, simProps) # put layers & simulation properties in the inf_writer
#         writer.display() # displays a formatted inf file
        if (self.outDir.get()=='Select Directory'):
                if os.path.isdir('./data/inf'):
                    outdir = './data/inf'
                elif os.path.isdir('../data/inf'):
                    outdir = '../data/inf'
                else:
                    outdir = './'
        else:
            outdir = self.outDir.get()
            
        writer.write_out(os.path.join(outdir, self.outfname.get()))
            
                    
if __name__=="__main__":
    root = Tk()
    GUI = myGUI(root)
    print(GUI.exp_file_name)
    root.mainloop()


