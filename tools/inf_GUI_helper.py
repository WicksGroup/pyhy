"""Several classes used by the `inf_GUI` to handle .inf creation

Todo:
    * confirm the increment calculator works well
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
        self.thermal_model = StringVar()
        self.thermal_model_multiplier = StringVar()
        self.yield_modulus = DoubleVar()
        self.yield_model = StringVar()
        self.shear_modulus = DoubleVar()
        self.shear_model = StringVar()
        self.thermal_conductivity_temp_cutoff = StringVar()
        self.thermal_conductivity = StringVar()

    def quick_label(self, string):
        """Easily label a feature in the GUI. Short cut to save typing this line out."""
        if '*' in string:
            Label(self.parent, text=string).grid(column=1, row=self.row, stick='NE')
        else:
            ttk.Label(self.parent, text=string).grid(column=1, row=self.row, stick='NE')
        
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
        self.quick_label('★Material ')

        # Option to set custom EOS.
        self.custom_eos.set('Default')
        ttk.Label(self.parent, text='Custom EOS ').grid(column=3, row=self.row, sticky='NE')
        ttk.Entry(self.parent, textvariable=self.custom_eos,
                  width=10).grid(column=4, row=self.row, sticky='NW')
        
        self.row += 1
        
        # Input the material thickness in microns (float)
        ttk.Entry(self.parent, textvariable=self.thickness,
                  width=7).grid(column=2, row=self.row, sticky='NW')
        self.quick_label('★Thickness (µm) ')
        self.row += 1       
        
        # Input the number of mesh points (integer)
        ttk.Entry(self.parent, textvariable=self.n_mesh, width=7).grid(column=2, row=self.row, sticky='NW')
        self.quick_label('★Num Mesh Points ')
        self.row += 1
        
        # Settings for the increment for each layer
        # While the increment in the Hyades .inf is a float, we use a string to allow for the fast / accurate defaults
        self.increment.set('Custom')
        self.quick_label('★Increment ')
        ttk.Entry(self.parent, textvariable=self.increment, width=10).grid(column=4, row=self.row, sticky='NW')
        ttk.Radiobutton(self.parent, text='Fast', value='fast',
                        variable=self.increment).grid(row=self.row, column=2, sticky='NW')
        ttk.Radiobutton(self.parent, text='Accurate', value='accurate',
                        variable=self.increment).grid(row=self.row, column=3, sticky='NW')
        self.row += 1

        # ttk.Label(self.parent, text='Everything below is optional'
        #           ).grid(row=self.row, column=1, columnspan=4, pady=(5, 5))
        # self.row += 1

        # Optionally set the material of interest
        ttk.Checkbutton(self.parent, text='Set as Material of Interest',
                        variable=self.is_material_of_interest).grid(column=1, row=self.row, sticky='NW')
        ttk.Label(self.parent, text='Set one Material of Interest if optimizing').grid(column=2, columnspan=2,
                                                                                       row=self.row, stick='NW')

        self.row += 1
        
        # Optionally set one material as shock material of interest using binary 0/1 for False/True
        ttk.Checkbutton(self.parent, text='Set as Shock MoI',
                        variable=self.is_shock_material_of_interest).grid(column=1, row=self.row, sticky='NW')
        ttk.Label(self.parent, text='Set one Shock MoI if optimizing shock velocity').grid(column=2, columnspan=2,
                                                                                           row=self.row, sticky='NW')
        self.row += 1
        
        # Drop down menu for thermal model, float input for multiplier on thermal model
        # float input for constant thermal conductivity
        # float input for temperature threshold on constant thermal conductivity
        self.thermal_model_multiplier.set(1.0)
        thermal_model_combobox = ttk.Combobox(self.parent, textvariable=self.thermal_model,
                                              values=('Default (Lee-More)', 'Purgatorio', 'Sesame'))
        thermal_model_combobox.current(0)
        thermal_model_combobox.grid(column=2, row=self.row, stick='NW')
        self.quick_label('Thermal Model ')
        ttk.Label(self.parent, text='Thermal Multiplier ').grid(row=self.row, column=3, sticky='NE')
        ttk.Entry(self.parent, textvariable=self.thermal_model_multiplier,
                  width=7).grid(column=4, row=self.row, sticky='NW')

        self.row += 1

        self.thermal_conductivity.set("Default to Model")
        self.thermal_conductivity_temp_cutoff.set("Default to Model")
        ttk.Label(self.parent, text="Thermal Conductivity (W/mK)").grid(row=self.row, column=1, sticky="NW")
        ttk.Entry(self.parent, textvariable=self.thermal_conductivity,
                  width=16).grid(row=self.row, column=2, sticky="NW")
        ttk.Label(self.parent, text="Below Temps (K) ").grid(row=self.row, column=3, sticky="NE")
        ttk.Entry(self.parent, textvariable=self.thermal_conductivity_temp_cutoff,
                  width=16).grid(row=self.row, column=4, sticky="NW")
        self.row += 1

        # Drop down menu for shear model
        shear_model_combobox = ttk.Combobox(self.parent, textvariable=self.shear_model,
                                            values=['None', 'Constant', 'Steinberg',
                                                    'Temp Depend 1', 'Temp Depend 2'])
        shear_model_combobox.current(0)
        shear_model_combobox.grid(column=2, row=self.row, sticky='NW')
        self.quick_label('Shear Model ')
        ttk.Label(self.parent, text='Shear Modulus (GPa) ').grid(column=3, row=self.row, sticky='NE')
        ttk.Entry(self.parent, textvariable=self.shear_modulus,
                  width=7).grid(column=4, row=self.row, sticky='NW')

        self.row += 1

        # Drop down menu for yield model
        yield_model_combobox = ttk.Combobox(self.parent, textvariable=self.yield_model,
                                            values=['None', 'von Mises', 'Mohr-Coulomb',
                                                    'Steinberg-Guinan', 'Steinberg-Lund',
                                                    'Johnson-Cook', 'Zerili-Armstrong',
                                                    'Preston-Tonks-Wallace'])
        yield_model_combobox.current(0)
        yield_model_combobox.grid(column=2, row=self.row, sticky='NW')
        self.quick_label('Yield Model ')
        ttk.Label(self.parent, text='Yield Modulus (GPa) ').grid(column=3, row=self.row, sticky='NE')
        ttk.Entry(self.parent, textvariable=self.yield_modulus,
                  width=7).grid(column=4, row=self.row, sticky='NW')

        self.row += 1
        # Not adding in the Spall Model as Ray said he never had it working well in Hyades


class Layer:
    """Object for holding all the information about layer properties that comes out of the GUI"""
    def __init__(self, props):
        self.material = props['material']
        self.thickness = props['thickness']
        self.n_mesh = props['n_mesh']
        self.thermal_model = props['thermal_model']
        self.thermal_model_multiplier = props['thermal_model_multiplier']
        self.thermal_conductivity = props['thermal_conductivity']
        self.thermal_conductivity_temp_cutoff = props['thermal_conductivity_temp_cutoff']
        self.shear_model = props['shear_model']
        self.shear_modulus = props['shear_modulus']
        self.yield_model = props['yield_model']
        self.yield_modulus = props['yield_modulus']
        self.is_material_of_interest = props['is_material_of_interest']
        self.is_shock_material_of_interest = props['is_shock_material_of_interest']
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
        * Determine if my new functions calculate_increment, can be swapped in or if we should just ignore increment
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
            # Fast increments are set to 1.0 for now.
            # increments = self.calc_increments(layers,  FZM_match_density=True)
            increments = [1.0 for L in layers]
        elif layers[0].increment == 'accurate':
            # Accurate increments space the mesh so the mass change between neighboring zones is less than 10%
            increments = self.calc_increments(layers,  FZM_match_density=False)
        elif not any([(L.increment == 'fast') or (L.increment == 'accurate') for L in layers]):
            increments = [float(L.increment) for L in layers]

        mesh_total = 1
        thickness_total = 0.0
        for i, L in enumerate(layers):
            mesh_line = f'mesh {mesh_total} {mesh_total + L.n_mesh} {thickness_total * 1e-4:.6f} {(thickness_total + L.thickness) * 1e-4:.6f} {increments[i]:.3f}'
            self.inf['MESH'].append(mesh_line)    

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
        
        materials_with_moi = []
        for L in layers:
            material_name = L.material.split()[0]
            if L.is_material_of_interest == 1:
                material_name += '!'
            if L.is_shock_material_of_interest == 1:
                material_name += '$'
            materials_with_moi.append(material_name)
                
        self.inf['DESCRIPTION'] = ['c HYADES Simulation Input File',
                                   f'c Created {datetime.date.today().strftime("%A, %B %d %Y")}',
                                   f'c Simulation of [{"] [".join([mat for mat in materials_with_moi])}]',
                                   ]
        if ('xray_probe_start' in sim_props) and ('xray_probe_stop' in sim_props):
            line = f'c xray_probe {sim_props["xray_probe_start"]} {sim_props["xray_probe_stop"]}'
            self.inf['DESCRIPTION'].append(line)
        
        if 'tvPres' in sim_props:
            self.inf['PRES'] = ['source pres 1 1', f'sourcem {sim_props["sourceMultiplier"]}'] + sim_props['tvPres']
        if 'tvTemp' in sim_props:
            self.inf['TEMP'] = ['source te 1 1',   f'sourcem {sim_props["sourceMultiplier"]}'] + sim_props['tvTemp']
        if 'tvLaser' in sim_props:
            wavelength = sim_props['laserWavelength'] / 1000  # convert nm to microns for Hyades
            self.inf['LASER'] = [f'source laser {wavelength} 1',
                                 f'sourcem {sim_props["sourceMultiplier"]}']
            self.inf['LASER'] += sim_props['tvLaser']  # extends the list, not a numerical addition

        self.inf['PARM'] = ['pparray r u acc rho te ti tr pres zbar sd1 eelc eion',
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

    def calculate_zone_width(self, layer, zone_index, increment):
        """Calculates the width of any Zone inside a given layer.

        A helper function for calculate_increment.

        Args:
            layer:
            zone_index:
            increment:

        Returns:
            Zone width in microns (float)
        """
        if increment == 1:
            return layer.thickness / layer.n_mesh

        denominator = sum([increment ** i for i in range(layer.n_mesh + 1)])
        width_0 = layer.thickness / denominator

        return width_0 * (increment ** zone_index)

    def calculate_increments(self, layers):
        """As of October 12, 2021 this function fails miserably for simulation setups with thin epoxy layers.
        Compute accurate increments so the mass difference at layer interfaces is less than 10%

        Args:
            layers (list): A list of Layer objects

        Returns:
            increments (list): A list of the increments, one per layer
        """
        output = []
        for i in range(len(layers)):
            if i == 0:  # Assume the first increment is 1.0
                output.append(1.0)
                continue

            # Compute the mass on the left side of the interface
            left_layer = layers[i - 1]
            left_zone_width = self.calculate_zone_width(left_layer,
                                                        left_layer.n_mesh - 1,
                                                        output[i - 1])
            left_zone_mass = left_layer.density * left_zone_width * 1e-4

            # Compute the right side mass for each increment between 0.9 and 1.1
            increments = np.arange(0.9, 1.1, step=0.001)
            right_layer = layers[i]
            right_zone_widths = np.array([self.calculate_zone_width(right_layer, 0, incr)
                                          for incr in increments])
            right_zone_masses = right_layer.density * right_zone_widths * 1e-4

            # Get the smallest mass change across the interface
            mass_difference = abs(right_zone_masses - left_zone_mass)
            k = np.argmin(mass_difference)  # Index of the smallest element in mass_difference
            increment = increments[k]
            right_zone_mass = right_zone_masses[k]

            # Throw an error if the mass difference is greater than  10%
            interface_mass_change = (left_zone_mass - right_zone_mass) / right_zone_mass
            if abs(interface_mass_change) > 0.10:
                raise ValueError(f'Could not find increment for Layer {i+1} that created interface mass change '
                                 f'of less than 10%. The best attempt is:\n'
                                 f'Increment: {increment} Mass Change (%): {100 * interface_mass_change}\n'
                                 f'Left Zone Mass (g): {left_zone_mass:.2e} Right Zone Mass (g): {right_zone_mass:.2e}')

            output.append(increment)

        return output

    def calc_increments(self, layers, FZM_match_density=False):
        """Calculate the increment powers for all of the layers"""
        n_mesh = [L.n_mesh for L in layers]
        thickness = [L.thickness * 1e-6 for L in layers]
        density = [L.density for L in layers]
        increments = [1.0 for i in range(len(layers))]  # lists are ugly but numpy caused issues
        increment_range = np.arange(0.90, 1.10, step=0.001)

        if FZM_match_density:
            '''
            Calculate the first increment so the FirstZoneMass is as close to the density of the material as possible.
            '''
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

                if abs(IMJ[i]) < 10:  # index is from outer loop
                    #                    print("IMJ Less than 10", IMJ[i], "|", IMJ, "|", increment_range[j])
                    # if this IMJ < threshold move onto the next one
                    break
                if j == len(increment_range) - 1:
                    # if gets to the last increment in the increment_range
                    raise Exception(f'Failed to find increment for layer {i + 1}')

                j += 1

        return increments
            
    def calc_IMJ(self, n_mesh, thickness, density, increments):
        """Calculate the interface mass jump between each of the layers.

        FZM is First Zone Mass
        LZM is Last Zone Mass
        AZM is Average Zone Mass

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
