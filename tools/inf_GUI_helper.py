# Connor Krill
# August 2019


import datetime
import numpy as np
from tkinter import ttk
from tkinter import filedialog
from tkinter import *
import pandas as pd


class myTab:
    '''
    Each tab is used to package all the variables for a layer in the Hyades simulation
    A single GUI can have multiple tabs, one per layer in the simulation
    The myTab class has no function to write its information, all of the necessary information
    is saved as attributes that are scraped by the other classes.
    '''
    def __init__(self, parent):
        self.parent = parent
        self.row = 2
        
    def quickLabel(self, string):
        '''short cut to save typing this line out'''
        if '*' in string:
            Label(self.parent, text=string).grid(column=1, row=self.row, stick='NW')
        else:
            ttk.Label(self.parent, text=string).grid(column=1, row=self.row, stick='NW')
        
    def add_props(self):
        '''
        Adds all the GUI widgets with appropriate labels and styles 
        '''
        # The options for materials are stored in inf_GUI_materials.xlsx
        filename = './inf_GUI_materials.xlsx'
        df = pd.read_excel(filename)
        material_options = []
        for m, e in zip(df['Material'], df['EOS']):
            material_options.append(f"{m} {e}")
        
        self.material = StringVar()
        ttk.Combobox(self.parent, textvariable=self.material,
                     values=material_options).grid(column=2,row=self.row, sticky='NW')
        self.quickLabel('*Material')
        
        self.customEOS = StringVar(); self.customEOS.set('Default')
        ttk.Label(self.parent, text='Custom EOS').grid(column=3, row=self.row, sticky='NSE')
        ttk.Entry(self.parent, textvariable=self.customEOS,
                  width=7).grid(column=4, row=self.row, sticky='NW')
        
        self.row += 1
        
        self.thickness = DoubleVar()
        ttk.Entry(self.parent, textvariable=self.thickness,
                  width=7).grid(column=2, row=self.row, sticky='NW')
        self.quickLabel('*Thickness (um)')
        self.row += 1       
        
        self.nMesh = IntVar()
        ttk.Entry(self.parent, textvariable=self.nMesh,
                  width=7).grid(column=2, row=self.row, sticky='NW')
        self.quickLabel('*Num Mesh Points')
        self.row += 1
        
        # Settings for the increment for each layer
        self.increment = StringVar(); self.increment.set('Custom')
        self.quickLabel('*Increment')
        ttk.Entry(self.parent, textvariable=self.increment, width=7).grid(column=4, row=self.row, sticky='NW')
#        ttk.Label(self.parent, text='Custom Increment').grid(column=4, row=self.row, sticky='NW')
#        self.row += 1

#        self.increment_type = StringVar()
#        self.increment_type.set('fast')
        ttk.Radiobutton(self.parent, text='Fast', value='fast',
                        variable=self.increment).grid(row=self.row, column=2, sticky='NW')
        ttk.Radiobutton(self.parent, text='Accurate', value='accurate',
                        variable=self.increment).grid(row=self.row, column=3, sticky='NW')
        self.row += 1
        
        
        ttk.Label(self.parent, text='Everything below is optional'
                  ).grid(row=self.row, column=1, columnspan=4, pady=(5,5))
        self.row += 1
        
#        self.quickLabel('Set one Material of Interest if opitimizing')
        ttk.Label(self.parent, text='Set one Material of Interest if optimizing').grid(column=1, columnspan=2, row=self.row, stick='NW')
        self.isMaterialOfInterest = IntVar()
        ttk.Checkbutton(self.parent, text='Set as Material of Interest',
                        variable=self.isMaterialOfInterest).grid(column=3, columnspan=2, row=self.row, sticky='NW')
        self.row += 1
        
        self.isShockMaterialOfInterest = IntVar() # binary 0/1 for False/ True
        ttk.Checkbutton(self.parent, text='Set as Shock MOI',
                        variable=self.isShockMaterialOfInterest).grid(column=3, columnspan=2, row=self.row, sticky='NW')
        ttk.Label(self.parent, text='Set one Shock MOI if optimizing shock velocity').grid(column=1, columnspan=2, row=self.row, sticky='NW')
        self.row += 1
        
        self.thermalModel, self.thermalMultiplier = StringVar(), DoubleVar()
        self.thermalMultiplier.set(1.0) # set the default value, the user can change this
        thermalModel_Combobox = ttk.Combobox(self.parent, textvariable=self.thermalModel,
                                             values=('Default (Lee-More)', 'Purgatorio', 'Sesame'))
        thermalModel_Combobox.current(0)
        thermalModel_Combobox.grid(column=2, row=self.row, stick='NW')
        self.quickLabel('Thermal Model')
#        self.row += 1
        ttk.Entry(self.parent, textvariable=self.thermalMultiplier,
                  width=7).grid(column=3, row=self.row, sticky='NW')
        ttk.Label(self.parent, text='Thermal Multiplier').grid(row=self.row, column=4, sticky='NW')
        self.row += 1

        self.thermalConductivity = StringVar()
        self.thermalConductivityTempCutoff = StringVar()
        self.thermalConductivity.set("Default to Model")
        self.thermalConductivityTempCutoff.set("Default to Model")
        ttk.Label(self.parent, text="Thermal Conductivity (W/mK)").grid(row=self.row, column=1, sticky="NW")
        ttk.Entry(self.parent, textvariable=self.thermalConductivity,
                  width=16).grid(row=self.row, column=2, sticky="NW")
        ttk.Label(self.parent, text="Below Temps (K)").grid(row=self.row, column=3, sticky="NW")
        ttk.Entry(self.parent, textvariable=self.thermalConductivityTempCutoff,
                  width=16).grid(row=self.row, column=4, sticky="NW")
        self.row += 1

        self.shearModel, self.shearModulus = StringVar(), DoubleVar()
        shearModel_ComboBox = ttk.Combobox(self.parent, textvariable=self.shearModel,
                                           values=['None', 'Constant', 'Steinberg',
                                                   'Temp Depend 1', 'Temp Depend 2'])
        shearModel_ComboBox.current(0)
        shearModel_ComboBox.grid(column=2,row=self.row,sticky='NW')
        self.quickLabel('Shear Model')
#        self.row += 1
        ttk.Entry(self.parent, textvariable=self.shearModulus,
                  width=7).grid(column=3, row=self.row, sticky='NW')
        ttk.Label(self.parent, text='Shear Modulus (GPa)').grid(column=4, row=self.row, sticky='NW')
#        self.quickLabel('Shear Modulus (GPa)')
        self.row += 1
        
        self.yieldModel, self.yieldModulus = StringVar(), DoubleVar()
        yieldModel_ComboBox = ttk.Combobox(self.parent, textvariable=self.yieldModel,
                                           values=['None', 'von Mises', 'Mohr-Coulomb',
                                                   'Steinberg-Guinan', 'Steinberg-Lund', 
                                                   'Johnson-Cook', 'Zerili-Armstrong',
                                                   'Preston-Tonks-Wallace'])
        yieldModel_ComboBox.current(0)
        yieldModel_ComboBox.grid(column=2, row=self.row, sticky='NW')
        self.quickLabel('Yield Model')
#        self.row += 1
        ttk.Entry(self.parent, textvariable=self.yieldModulus,
                  width=7).grid(column=3, row=self.row, sticky='NW')
        ttk.Label(self.parent, text='Yield Modulus (GPa)').grid(column=4, row=self.row, sticky='NW')
#        self.quickLabel('Yield Modulus (GPa)')
        self.row += 1
        # Not adding in the Spall Model as Ray said he never had it working well in HYADES



class Layer:
    '''object for holding all the information about layer properties that comes out of the GUI '''
    def __init__(self, props):
#         assert len(props)==5, 'Input must be an iterable of length 5'
        self.material          = props['material']
        self.thickness         = props['thickness']
        self.nMesh             = props['nMesh']
        self.thermalModel      = props['thermalModel']
        self.thermalMultiplier = props['thermalMultiplier']
        self.thermalConductivity = props['thermalConductivity']
        self.thermalConductivityTempCutoff = props['thermalConductivityTempCutoff']
        self.shearModel        = props['shearModel']
        self.shearModulus      = props['shearModulus']
        self.yieldModel        = props['yieldModel']
        self.yieldModulus      = props['yieldModulus']
        self.isMaterialOfInterest = props['isMaterialOfInterest']
        self.isShockMaterialOfInterest = props['isShockMaterialOfInterest']
        self.increment = props['increment']
        if props['customEOS']=='Default':
            # get the EOS number from the material selection
            self.EOS = int(self.material.split()[1]) 
        else:
            try:
                self.EOS = int(props['customEOS'])
            except ValueError as e:
                print('Enter an integer for the custom EOS value')
                raise e
        filename = './inf_GUI_materials.xlsx'
        df = pd.read_excel(filename)
        material, EOS = self.material.split()
        EOS = int(EOS)
        material_properties = df.loc[(df['Material']==material) & (df['EOS']==EOS)]
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
        self.density        = float(material_properties['Density'])

    def display(self):
        for k in sorted(vars(self)):
            print(f'{k}: {vars(self)[k]}')
            
            
            
            
class inf_writer:
    '''Takes an interable of Layers and formats them into an inf'''
    
    def __init__(self):
        self.inf = {'DESCRIPTION' : [],
                    'GEOMETRY'    : [],
                    'MESH'        : [],
                    'REGION'      : [],
                    'MATERIAL'    : [],
                    'IONIZ'       : [],
                    'EOS'         : [],
                    'EOSXTRP'     : [],
                    'THERMALPROP' : [],
                    'STRENGTH'    : [],
                    'PRES'        : [],
                    'TEMP'        : [],
                    'LASER'       : [],
                    'PARM'        : []
                   }
        
        
    def add_layers(self, layers, simProps):
        '''Add all the info from each layer to an internal dictionary'''
        # Check for increments. If any are default calculate all of them.s
        if layers[0].increment=='fast':
            increments = self.calc_increments(layers, FZM_match_density=False)
        elif layers[0].increment=='accurate':
            increments = self.calc_increments(layers, FZM_match_density=True)
        elif not any([(L.increment=='fast') or (L.increment=='accurate') for L in layers]):
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
            mesh_line = f'mesh {mesh_total} {mesh_total + L.nMesh} {thickness_total*1e-4:.6f} {(thickness_total + L.thickness)*1e-4:.6f} {increments[i]:.3f}' 
            self.inf['MESH'].append(mesh_line)    

#            if (i==len(layers)-1):
#                region_end = mesh_total + L.nMesh # if the last layer dont subtract 1
#            else:
            region_end = mesh_total + L.nMesh - 1
            self.inf['REGION'].append( f'region {mesh_total} {region_end} {i+1} {L.density}' )
            for atom_num, atom_mass, mol_frac in zip(L.atomic_number, L.atomic_mass, L.molar_fraction):
                self.inf['MATERIAL'].append( f'material {i+1} {atom_num} {atom_mass} {mol_frac}' )
            self.inf['IONIZ'].append( f'ioniz {i+1} 3' )
            self.inf['EOS'].append( f'EOS {L.EOS} {i+1}' )
            self.inf['EOSXTRP'].append( f'eosxtrp {i+1} 2 2 2 2' )
            if ('Default' not in L.thermalModel):
                self.inf['THERMALPROP'].append( f'data thrmcond {i+1} ENTER_{L.thermalModel}_FILENAME_HERE' )
            if (L.thermalMultiplier != 1):
                self.inf['THERMALPROP'].append( f'eosm tc {L.thermalMultiplier} {i+1}' )
            if ('Default' not in L.thermalConductivity) and ('Default' not in L.thermalConductivityTempCutoff):
                hyades_temperature_cutoff = float(L.thermalConductivityTempCutoff) * (1 / (11604 * 1000)) # Kelvin to KeV
                hyades_thermal_conductivity = float(L.thermalConductivity) * 1.1605e+12 # W/mK to ergs / second*cm*KeV
                self.inf['THERMALPROP'].append( f'data thrmcond {i+1} {hyades_temperature_cutoff:.4e} {hyades_thermal_conductivity:.6e}' )
            if  (L.shearModel != 'None') or (L.yieldModel != 'None'):
                shearOp = ['None', 'Constant', 'Steinberg', 'Temp Depend 1', 'Temp Depend 2']
                yieldOp = ['None', 'von Mises', 'Mohr-Coulomb', 'Steinberg-Guinan', 'Steinberg-Lund', 
                                   'Johnson-Cook', 'Zerili-Armstrong', 'Preston-Tonks-Wallace']
                self.inf['STRENGTH'].append(f'strength {i+1} {shearOp.index(L.shearModel)} {yieldOp.index(L.yieldModel)}')
            if (L.shearModel != 'None'):
                self.inf['STRENGTH'].append(f'data shear {i+1} {1e10 * L.shearModulus:.2e} 4.3e-13 0.0')
            if (L.yieldModel != 'None'):
                self.inf['STRENGTH'].append(f'data yield {i+1} {1e10 * L.yieldModulus:.2e} 0.0 0.0 0.0 {1e10 * L.shearModulus:.2e}')
                
            mesh_total += L.nMesh
            thickness_total += L.thickness

        # most of these parameters are generic and used on all simulations
        self.inf['GEOMETRY']    = ['geometry 1 1']
        
        materials_with_MOI = []
        for L in layers:
            material_name = L.material.split()[0]
            if L.isMaterialOfInterest==1:
                material_name += '!'
            if L.isShockMaterialOfInterest==1:
                material_name += '$'
            materials_with_MOI.append(material_name)
                    
                
        self.inf['DESCRIPTION'] = ['c HYADES Simulation INput File',
                                   f'c Created {datetime.date.today().strftime("%A, %B %d %Y")}',
                                   f'c Simulation of [{"] [".join([mat for mat in materials_with_MOI])}]',
                                  ]
        if ('XrayProbeStart' in simProps) and ('XrayProbeStop' in simProps):
            line = f'c XrayProbe {simProps["XrayProbeStart"]} {simProps["XrayProbeStop"]}'
            self.inf['DESCRIPTION'].append( line )        
        
        if 'tvPres' in simProps:
            self.inf['PRES'] = ['source pres 1 10', f'sourcem {simProps["sourceMultiplier"]}'] + simProps['tvPres']
        if 'tvTemp' in simProps:
            self.inf['TEMP'] = ['source te 1 10',   f'sourcem {simProps["sourceMultiplier"]}'] + simProps['tvTemp']
        if 'tvLaser' in simProps:
            wavelength = simProps['laserWavelength'] / 1000 # convert nm to microns for Hyades
            self.inf['LASER'] = [f'source laser {wavelength} 1',
                                 f'sourcem {simProps["sourceMultiplier"]}']
            self.inf['LASER'] += simProps['tvLaser'] # extends the list, not a numerical addition

        self.inf['PARM'] = ['pparray r u acc rho te ti tr pres zbar sd1',
                            'parm nstop 5000000',
                            'parm IRDTRN 0',
                            f'parm tstop {simProps["timeMax"] * 1e-9:.2e}',
                            f'parm postdt {simProps["timeStep"] * 1e-9:.2e}',
                            'parm alvism 0.5',
                            'parm aqvism 2.0',
                            'parm flxlem .03',
                            'parm temin 2.58e-05',
                            'parm timin 2.58e-05',
                            'parm qstimx 0.00001',  
                           ]

    def display(self):
        for key in self.inf:
            for line in self.inf[key]:
                print(line)
                
        
    def write_out(self, outfname):
        '''Write the internal variables out to a text file'''
        if not outfname.endswith('.inf'):
            outfname += '.inf'
        
        outlines = []
        for key in self.inf:
            for line in self.inf[key]:
                if not line.endswith('\n'):
                    line += '\n'
                outlines.append(line)
            
        with open(outfname, 'w') as fh:
            fh.writelines(outlines)
        print(f'Wrote {outfname}')
        
    
    def calc_increments(self, layers, FZM_match_density=False):
        '''Calculate the increment powers for all of the layers'''
        nMesh     = [L.nMesh for L in layers]
        thickness = [L.thickness * 1e-6 for L in layers]
        density   = [L.density for L in layers]        
        increments = [1.0 for i in range(len(layers))] # lists are ugly but numpy caused issues
        increment_range = np.arange(0.90, 1.10, step=0.001)
        ###
        if FZM_match_density:
#            print("CONDITION TO ENTER THE IF STATEMENT:", FZM_match_density)
            # Calculate the first increment so the FirstZoneMass is as close to the density of the material as possible
            FZM = np.zeros(increment_range.shape) * np.nan
            for i in range(len(increment_range)):
                incr = increment_range[i]
                # First Zone Mass formulas from self.calc_IMJ
                if incr == 1.0:
                    first_zone_mass = 100 * thickness[0] * density[0] / nMesh[0]
                else:
                    first_zone_mass = 100 * thickness[0] * density[0]
                    first_zone_mass *= (1 - incr) * (1 - (incr ** nMesh[0]) )
                FZM[i] = first_zone_mass
            ix = np.argmin( abs(FZM - density[0]) )
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
                IMJ = self.calc_IMJ(nMesh, thickness, density, increments)
                
                if abs(IMJ[i]) < 10: # index is from outer loop
#                    print("IMJ Less than 10", IMJ[i], "|", IMJ, "|", increment_range[j])
                    # if this IMJ < threshold move onto the next one
                    break
                if j==len(increment_range)-1:
                    # if gets to the last increment in the increment_range
                    raise Exception(f'Failed to find increment for layer {i+1}\ni_ignore={i_ignore}')
                
                j += 1
                
        return increments
        
            
    def calc_IMJ(self, nMesh, thickness, density, increments):
        '''
        Calculate the interface mass jump between each of the layers
        Formula from an old excel sheet that calculated this
        '''
        FZM, LZM, IMJ = [], [], []
        for i in range(len(nMesh)):
            azm = 100 * thickness[i] * density[i] / nMesh[i]
            
            if increments[i]==1:
                fzm = azm
                lzm = azm
            else:
                fzm = 100 * thickness[i] * density[i]
                fzm *= (1-increments[i]) * (1 - (increments[i]**nMesh[i]) )
                lzm = fzm * (increments[i]**(nMesh[i]-1))
            FZM.append(fzm)
            LZM.append(lzm)
            
            if i==0:
                imj = np.nan
            else:
                imj = 200 * (FZM[i] - LZM[i]) / (FZM[i] + LZM[i-1])
            IMJ.append(imj)
            
        return IMJ
        
        
