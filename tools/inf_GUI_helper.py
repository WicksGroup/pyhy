"""Several classes used by the `inf_GUI` to handle .inf creation

Todo:
    * make sure this works with cdf reader
    * reformat function names
    * document functions
    * reformat variables

"""
import datetime
import numpy as np
import pandas as pd
from tkinter import ttk
from tkinter import *


class LayerTab:
    """Presents all the input options for a single layer in inf_GUI.py as a tkinter tab.

    Each tab is used to package all the variables for a layer in the Hyades simulation.
    A single GUI can have multiple tabs, one per layer in the simulation.
    The LayerTab class has no function to write its information, all of the necessary information
    is saved as attributes that are scraped by the other classes.

    Todo:
        * Do we need the custom EOS option? Or should that material be added to the excel file?
    """
    def __init__(self, parent):
        """Declares all material properties as variables and formats tkinter tab."""
        self.parent = parent
        self.row = 2

        self.material = StringVar()
        self.custom_eos = StringVar()
        self.thickness = DoubleVar()
        self.n_mesh = IntVar()
        self.increment = StringVar()
        self.is_material_of_interest = IntVar()
        self.is_shock_material_of_interest = IntVar()
        self.thermal_model = DoubleVar()
        self.thermal_model_multiplier = StringVar()
        self.yield_modulus = StringVar()
        self.yield_model = DoubleVar()
        self.shear_modulus = StringVar()
        self.shear_model = DoubleVar()
        self.thermal_conductivity_temp_cutoff = StringVar()
        self.thermal_conductivity = StringVar()

    def quick_label(self, string):
        """Easily label a feature in the GUI. Short cut to save typing this line out."""
        if '*' in string:
            Label(self.parent, text=string).grid(column=1, row=self.row, stick='NW')
        else:
            ttk.Label(self.parent, text=string).grid(column=1, row=self.row, stick='NW')
        
    def add_props(self):
        """Adds all the GUI widgets with appropriate labels and styles

        Note:
            The options for materials are stored in `inf_GUI_materials.xlsx`

        """
        filename = './tools/inf_GUI_materials.xlsx'
        df = pd.read_excel(filename)
        material_options = []
        for m, e in zip(df['Material'], df['EOS']):
            material_options.append(f"{m} {e}")

        # Drop down menu to select one of the materials from inf_GUI_materials.xlsx
        ttk.Combobox(self.parent, textvariable=self.material,
                     values=material_options).grid(column=2, row=self.row, sticky='NW')
        self.quick_label('*Material')

        # Option to set custom EOS.
        self.custom_eos.set('Default')
        ttk.Label(self.parent, text='Custom EOS').grid(column=3, row=self.row, sticky='NSE')
        ttk.Entry(self.parent, textvariable=self.custom_eos,
                  width=7).grid(column=4, row=self.row, sticky='NW')
        
        self.row += 1
        
        # Input the material thickness in microns (float)
        ttk.Entry(self.parent, textvariable=self.thickness,
                  width=7).grid(column=2, row=self.row, sticky='NW')
        self.quick_label('*Thickness (um)')
        self.row += 1       
        
        # Input the number of mesh points (integer)
        ttk.Entry(self.parent, textvariable=self.n_mesh,
                  width=7).grid(column=2, row=self.row, sticky='NW')
        self.quick_label('*Num Mesh Points')
        self.row += 1
        
        # Settings for the increment for each layer
        # While the increment in the Hyades .inf is a float, we use a string to allow for the fast / accurate defaults
        self.increment.set('Custom')
        self.quick_label('*Increment')
        ttk.Entry(self.parent, textvariable=self.increment, width=7).grid(column=4, row=self.row, sticky='NW')
        ttk.Radiobutton(self.parent, text='Fast', value='fast',
                        variable=self.increment).grid(row=self.row, column=2, sticky='NW')
        ttk.Radiobutton(self.parent, text='Accurate', value='accurate',
                        variable=self.increment).grid(row=self.row, column=3, sticky='NW')
        self.row += 1

        ttk.Label(self.parent, text='Everything below is optional'
                  ).grid(row=self.row, column=1, columnspan=4, pady=(5, 5))
        self.row += 1

        # Optionally set the material of interest
        ttk.Label(self.parent, text='Set one Material of Interest if optimizing').grid(column=1, columnspan=2,
                                                                                       row=self.row, stick='NW')
        ttk.Checkbutton(self.parent, text='Set as Material of Interest',
                        variable=self.is_material_of_interest).grid(column=3, columnspan=2, row=self.row, sticky='NW')
        self.row += 1
        
        # Optionally set one material as shock material of interest # binary 0/1 for False/ True
        ttk.Checkbutton(self.parent, text='Set as Shock MOI',
                        variable=self.is_shock_material_of_interest).grid(column=3, columnspan=2,
                                                                          row=self.row, sticky='NW')
        ttk.Label(self.parent, text='Set one Shock MOI if optimizing shock velocity').grid(column=1, columnspan=2,
                                                                                           row=self.row, sticky='NW')
        self.row += 1
        
        # Drop down menu for thermal model, float input for multiplier on thermal model
        # float input for constant thermal conductivity
        # float input for temperature threshold on constant thermal conductivity
        self.thermal_model_multiplier.set(1.0)  # set the default value, the user can change this
        thermal_model_combobox = ttk.Combobox(self.parent, textvariable=self.thermal_model,
                                              values=('Default (Lee-More)', 'Purgatorio', 'Sesame'))
        thermal_model_combobox.current(0)
        thermal_model_combobox.grid(column=2, row=self.row, stick='NW')
        self.quick_label('Thermal Model')
        ttk.Entry(self.parent, textvariable=self.thermal_model_multiplier,
                  width=7).grid(column=3, row=self.row, sticky='NW')
        ttk.Label(self.parent, text='Thermal Multiplier').grid(row=self.row, column=4, sticky='NW')
        self.row += 1

        self.thermal_conductivity.set("Default to Model")
        self.thermal_conductivity_temp_cutoff.set("Default to Model")
        ttk.Label(self.parent, text="Thermal Conductivity (W/mK)").grid(row=self.row, column=1, sticky="NW")
        ttk.Entry(self.parent, textvariable=self.thermal_conductivity,
                  width=16).grid(row=self.row, column=2, sticky="NW")
        ttk.Label(self.parent, text="Below Temps (K)").grid(row=self.row, column=3, sticky="NW")
        ttk.Entry(self.parent, textvariable=self.thermal_conductivity_temp_cutoff,
                  width=16).grid(row=self.row, column=4, sticky="NW")
        self.row += 1

        # Drop down menu for shear model
        shear_model_combobox = ttk.Combobox(self.parent, textvariable=self.shear_model,
                                            values=['None', 'Constant', 'Steinberg',
                                                    'Temp Depend 1', 'Temp Depend 2'])
        shear_model_combobox.current(0)
        shear_model_combobox.grid(column=2, row=self.row, sticky='NW')
        self.quick_label('Shear Model')
        ttk.Entry(self.parent, textvariable=self.shear_modulus,
                  width=7).grid(column=3, row=self.row, sticky='NW')
        ttk.Label(self.parent, text='Shear Modulus (GPa)').grid(column=4, row=self.row, sticky='NW')
        self.row += 1

        # Drop down menu for yield model
        yield_model_combobox = ttk.Combobox(self.parent, textvariable=self.yield_model,
                                            values=['None', 'von Mises', 'Mohr-Coulomb',
                                                    'Steinberg-Guinan', 'Steinberg-Lund',
                                                    'Johnson-Cook', 'Zerili-Armstrong',
                                                    'Preston-Tonks-Wallace'])
        yield_model_combobox.current(0)
        yield_model_combobox.grid(column=2, row=self.row, sticky='NW')
        self.quick_label('Yield Model')
        ttk.Entry(self.parent, textvariable=self.yield_modulus,
                  width=7).grid(column=3, row=self.row, sticky='NW')
        ttk.Label(self.parent, text='Yield Modulus (GPa)').grid(column=4, row=self.row, sticky='NW')
        self.row += 1
        # Not adding in the Spall Model as Ray said he never had it working well in Hyades


class Layer:
    """Object for holding all the information about layer properties that comes out of the GUI"""
    def __init__(self, props):
        self.material = props['material']
        self.thickness = props['thickness']
        self.nMesh = props['n_mesh']
        self.thermalModel = props['thermal_model']
        self.thermalMultiplier = props['thermal_model_multiplier']
        self.thermalConductivity = props['thermal_conductivity']
        self.thermalConductivityTempCutoff = props['thermal_conductivity_temp_cutoff']
        self.shearModel = props['shear_model']
        self.shearModulus = props['shear_modulus']
        self.yieldModel = props['yield_model']
        self.yieldModulus = props['yield_modulus']
        self.isMaterialOfInterest = props['is_material_of_interest']
        self.isShockMaterialOfInterest = props['is_shock_material_of_interest']
        self.increment = props['increment']

        if props['custom_eos'] == 'Default':
            # get the EOS number from the material selection
            self.EOS = int(self.material.split()[1]) 
        else:
            try:
                self.EOS = int(props['custom_eos'])
            except ValueError as e:
                print('Enter an integer for the custom EOS value')
                raise e
        filename = './tools/inf_GUI_materials.xlsx'
        df = pd.read_excel(filename)
        material, eos = self.material.split()
        eos = int(eos)
        material_properties = df.loc[(df['Material'] == material) & (df['EOS'] == eos)]
        # If a variable is a string, it is a list of values. Otherwise it should just be a single value
        if isinstance(material_properties['Atomic Number'].iat[0], str):
            self.atomic_number = [int(i) for i in material_properties['Atomic Number'].iat[0].split(',')]
        else: 
            self.atomic_number = [material_properties['Atomic Number'].iat[0]]
        if isinstance(material_properties['Atomic Mass'].iat[0], str):
            self.atomic_mass = [float(i) for i in material_properties['Atomic Mass'].iat[0].split(',')]
        else:
            self.atomic_mass = [material_properties['Atomic Mass'].iat[0]]
        if isinstance(material_properties['Molar Fraction'].iat[0], str):
            self.molar_fraction = [float(i) for i in material_properties['Molar Fraction'].iat[0].split(',')]
        else:
            self.molar_fraction = [material_properties['Molar Fraction'].iat[0]]
        self.density = float(material_properties['Density'])

    def display(self):
        """Debugging function to print all the variables for each layer"""
        for k in sorted(vars(self)):
            print(f'{k}: {vars(self)[k]}')
            

class InfWriter:
    """Takes an iterable of Layers and formats them into an inf

    Todo:
        * Double check that the increment calculation is being done correctly
    """
    
    def __init__(self):
        self.inf = {'DESCRIPTION': [],
                    'GEOMETRY': [],
                    'MESH': [],
                    'REGION': [],
                    'MATERIAL': [],
                    'IONIZ': [],
                    'EOS': [],
                    'EOSXTRP': [],
                    'THERMALPROP': [],
                    'STRENGTH': [],
                    'PRES': [],
                    'TEMP': [],
                    'LASER': [],
                    'PARM': []
                    }

    def add_layers(self, layers, sim_props):
        """Converts Python variables to strings formatted for Hyades

        Args:
            layers (list): An iterable of Layers objects
            sim_props (dict): general simulation parameters, such as xray probe time and time step
        """
        # Check for increments. If any are default calculate all of them
        if layers[0].increment == 'fast':
            increments = self.calc_increments(layers, FZM_match_density=False)
        elif layers[0].increment == 'accurate':
            increments = self.calc_increments(layers, FZM_match_density=True)
        elif not any([(L.increment == 'fast') or (L.increment == 'accurate') for L in layers]):
            increments = [float(L.increment) for L in layers]
#        print("INCREMENTS", increments)
#        if any([L.increment=='Default' for L in layers]):
#            try:
#                increments = self.calc_increments(layers, FZM_match_density=True)
#            except:
#                increments = self.calc_increments(layers, FZM_match_density=False)
#        else:
#            increments = [float(L.increment) for L in layers]

        mesh_total = 1
        thickness_total = 0.0
        for i, L in enumerate(layers):
            
#             if (i==len(layers)-1):
#                 mesh_total -= 1
            mesh_line = f'mesh {mesh_total} {mesh_total + L.n_mesh} {thickness_total * 1e-4:.6f} {(thickness_total + L.thickness) * 1e-4:.6f} {increments[i]:.3f}'
            self.inf['MESH'].append(mesh_line)    

#            if (i==len(layers)-1):
#                region_end = mesh_total + L.n_mesh # if the last layer dont subtract 1
#            else:
            region_end = mesh_total + L.n_mesh - 1
            self.inf['REGION'].append(f'region {mesh_total} {region_end} {i+1} {L.density}')
            for atom_num, atom_mass, mol_frac in zip(L.atomic_number, L.atomic_mass, L.molar_fraction):
                self.inf['MATERIAL'].append(f'material {i+1} {atom_num} {atom_mass} {mol_frac}')
            self.inf['IONIZ'].append(f'ioniz {i+1} 3')
            self.inf['EOS'].append(f'EOS {L.EOS} {i+1}')
            self.inf['EOSXTRP'].append(f'eosxtrp {i+1} 2 2 2 2')
            if 'Default' not in L.thermal_model:
                self.inf['THERMALPROP'].append(f'data thrmcond {i+1} ENTER_{L.thermal_model}_FILENAME_HERE')
            if L.thermal_model_multiplier != 1:
                self.inf['THERMALPROP'].append(f'eosm tc {L.thermal_model_multiplier} {i + 1}')
            if ('Default' not in L.thermal_conductivity) and ('Default' not in L.thermal_conductivity_temp_cutoff):
                hyades_temperature_cutoff = float(L.thermal_conductivity_temp_cutoff) * (1 / (11604 * 1000))  # Kelvin to KeV
                hyades_thermal_conductivity = float(L.thermal_conductivity) * 1.1605e+12  # W/mK to ergs / second*cm*KeV
                self.inf['THERMALPROP'].append(f'data thrmcond {i+1} {hyades_temperature_cutoff:.4e} {hyades_thermal_conductivity:.6e}')
            if (L.shear_model != 'None') or (L.yield_model != 'None'):
                shear_options = ['None', 'Constant', 'Steinberg', 'Temp Depend 1', 'Temp Depend 2']
                yield_options = ['None', 'von Mises', 'Mohr-Coulomb', 'Steinberg-Guinan', 'Steinberg-Lund',
                                 'Johnson-Cook', 'Zerili-Armstrong', 'Preston-Tonks-Wallace']
                self.inf['STRENGTH'].append(f'strength {i+1} {shear_options.index(L.shear_model)} {yield_options.index(L.yield_model)}')
            if L.shear_model != 'None':
                self.inf['STRENGTH'].append(f'data shear {i+1} {1e10 * L.shear_modulus:.2e} 4.3e-13 0.0')
            if L.yield_model != 'None':
                self.inf['STRENGTH'].append(f'data yield {i+1} {1e10 * L.yield_modulus:.2e} 0.0 0.0 0.0 {1e10 * L.shear_modulus:.2e}')
                
            mesh_total += L.n_mesh
            thickness_total += L.thickness

        # most of these parameters are generic and used on all simulations
        self.inf['GEOMETRY'] = ['geometry 1 1']
        
        materials_with_MOI = []
        for L in layers:
            material_name = L.material.split()[0]
            if L.is_material_of_interest == 1:
                material_name += '!'
            if L.is_shock_material_of_interest == 1:
                material_name += '$'
            materials_with_MOI.append(material_name)
                
        self.inf['DESCRIPTION'] = ['c HYADES Simulation Input File',
                                   f'c Created {datetime.date.today().strftime("%A, %B %d %Y")}',
                                   f'c Simulation of [{"] [".join([mat for mat in materials_with_MOI])}]',
                                   ]
        if ('xray_probe_start' in sim_props) and ('xray_probe_stop' in sim_props):
            line = f'c xray_probe {sim_props["xray_probe_start"]} {sim_props["xray_probe_stop"]}'
            self.inf['DESCRIPTION'].append(line)
        
        if 'tvPres' in sim_props:
            self.inf['PRES'] = ['source pres 1 10', f'sourcem {sim_props["sourceMultiplier"]}'] + sim_props['tvPres']
        if 'tvTemp' in sim_props:
            self.inf['TEMP'] = ['source te 1 10',   f'sourcem {sim_props["sourceMultiplier"]}'] + sim_props['tvTemp']
        if 'tvLaser' in sim_props:
            wavelength = sim_props['laserWavelength'] / 1000  # convert nm to microns for Hyades
            self.inf['LASER'] = [f'source laser {wavelength} 1',
                                 f'sourcem {sim_props["sourceMultiplier"]}']
            self.inf['LASER'] += sim_props['tvLaser']  # extends the list, not a numerical addition

        self.inf['PARM'] = ['pparray r u acc rho te ti tr pres zbar sd1',
                            'parm nstop 5000000',
                            'parm IRDTRN 0',
                            f'parm tstop {sim_props["time_max"] * 1e-9:.2e}',
                            f'parm postdt {sim_props["time_step"] * 1e-9:.2e}',
                            'parm alvism 0.5',
                            'parm aqvism 2.0',
                            'parm flxlem .03',
                            'parm temin 2.58e-05',
                            'parm timin 2.58e-05',
                            'parm qstimx 0.00001',  
                            ]

    def display(self):
        """Debugging function to print all the variables for each layer"""
        for key in self.inf:
            for line in self.inf[key]:
                print(line)

    def write_out(self, out_filename):
        """Write the internal variables out to a text file"""
        if not out_filename.endswith('.inf'):
            out_filename += '.inf'
        
        outlines = []
        for key in self.inf:
            for line in self.inf[key]:
                if not line.endswith('\n'):
                    line += '\n'
                outlines.append(line)
            
        with open(out_filename, 'w') as fh:
            fh.writelines(outlines)
        print(f'Wrote {out_filename}')

    def calc_increments(self, layers, FZM_match_density=False):
        """Calculate the increment powers for all of the layers"""
        n_mesh = [L.n_mesh for L in layers]
        thickness = [L.thickness * 1e-6 for L in layers]
        density = [L.density for L in layers]
        increments = [1.0 for i in range(len(layers))]  # lists are ugly but numpy caused issues
        increment_range = np.arange(0.90, 1.10, step=0.001)

        if FZM_match_density:
            # Calculate the first increment so the FirstZoneMass is as close to the density of the material as possible
            FZM = np.zeros(increment_range.shape) * np.nan
            for i in range(len(increment_range)):
                incr = increment_range[i]
                # First Zone Mass formulas from self.calc_IMJ
                if incr == 1.0:
                    first_zone_mass = 100 * thickness[0] * density[0] / n_mesh[0]
                else:
                    first_zone_mass = 100 * thickness[0] * density[0]
                    first_zone_mass *= (1 - incr) * (1 - (incr ** n_mesh[0]))
                FZM[i] = first_zone_mass
            ix = np.argmin(abs(FZM - density[0]))
            first_increment = increment_range[ix]
            increments[0] = first_increment
#            print("First Material", layers[0].material)
#            print("Density:", density[0], "First Zone Mass:", FZM[ix], "Increment:", first_increment)

            return increments
        ###
        # For loop always skips the first material
        # if FZM_match_density, then this leaves the altered increment alone
        # else the first increment is just one
        for i in range(1, len(increments)):
            j = 0
            while j < len(increment_range):
                increments[i] = increment_range[j]
                IMJ = self.calc_IMJ(n_mesh, thickness, density, increments)
                
                if abs(IMJ[i]) < 10: # index is from outer loop
#                    print("IMJ Less than 10", IMJ[i], "|", IMJ, "|", increment_range[j])
                    # if this IMJ < threshold move onto the next one
                    break
                if j==len(increment_range)-1:
                    # if gets to the last increment in the increment_range
                    raise Exception(f'Failed to find increment for layer {i+1}\ni_ignore={i_ignore}')
                
                j += 1
                
        return increments
            
    def calc_IMJ(self, n_mesh, thickness, density, increments):
        """Calculate the interface mass jump between each of the layers.

        Note:
            This formula came from an old excel sheet that Ray and June had.

        """
        FZM, LZM, IMJ = [], [], []
        for i in range(len(n_mesh)):
            azm = 100 * thickness[i] * density[i] / n_mesh[i]
            
            if increments[i] == 1:
                fzm = azm
                lzm = azm
            else:
                fzm = 100 * thickness[i] * density[i]
                fzm *= (1-increments[i]) * (1 - (increments[i] ** n_mesh[i]))
                lzm = fzm * (increments[i] ** (n_mesh[i] - 1))
            FZM.append(fzm)
            LZM.append(lzm)
            
            if i == 0:
                imj = np.nan
            else:
                imj = 200 * (FZM[i] - LZM[i]) / (FZM[i] + LZM[i-1])
            IMJ.append(imj)
            
        return IMJ
