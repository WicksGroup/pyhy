"""
Created on Wed Apr  4 22:52:49 2018
Connor Krill
Update August 22, 2019
"""
import matplotlib.pyplot as plt
import numpy as np
import os


def createOutput(run_path, var, debug=0, info=False):
    '''Create the Output here to handle the scales'''
    if 'pres' in var.lower():
        var = 'Pres'
        obj_scale = 1e-10
    elif 'sd1' in var.lower():
        var = 'sd1'
        obj_scale = 1e-10
    elif 'te' in var.lower():
        var = 'Te'
        obj_scale = 11604*1000
    elif ('Up'==var) or ('U'==var) or ('particle' in var.lower()) :
        var = 'U'
        obj_scale = 1e-5
    elif ('rho' in var.lower()) or ('den' in var.lower()):
        var = 'Rho'
        obj_scale = 1
    elif ('ion' in var.lower()) or (var=='Ti'):
        var = 'Ti'
        obj_scale = 11604*1000
    elif ('radition' in var.lower()) or (var=='Tr'):
        var = 'Tr'
        obj_scale = 11604*1000
    elif ('Us'==var) or ('shock' in var.lower()): # Return an entirely different class if Shock Velocity
        shock = shockVelocity(run_path)
        return shock
    else:
        error_str = f'Unexpected variable entered: {var!r}'
        error_str += '\nAccepted variables are: Pressure (Pres), Temperature (Te), Density (Rho), '
        error_str += 'Particle Velocity (Up), Shock Velocity (Us)'
        error_str += '\nEnter one of the variable names or abbrevations'
        raise ValueError(error_str)
    
    dat_fname = run_path
    inf_fname = run_path
    if run_path.endswith('.dat'):
        inf_fname = inf_fname[:-4]
    elif not dat_fname.endswith(var):
        dat_fname = f'{dat_fname}_{var}'
#        inf_fname = dat_fname
    hyades = hyadesOutput(dat_fname, inf_fname, obj_scale)
    
    # subtract sd1 when calculating pressure
    # sd1 is in the same units as pressure, so it also has the scale 1e-10
    if 'pres' in var.lower():
        sd1_dat = f'{run_path}_sd1.dat'
        sd1 = hyadesOutput(sd1_dat, inf_fname, 1e-10)
        hyades.output = hyades.output - sd1.output
        
    return hyades

    

class hyadesOutput:
    '''Instances take in a .DAT Output file and .inf input file
        and produce an object with the mesh, time, Output, and tv values.'''
    
    def __init__(self, dat_fname, inf_fname, scale):
        self.location = os.path.dirname(inf_fname)
        self.name     = os.path.basename(inf_fname)
        
        data, comment = self.hyadesDatReader(dat_fname)
        self.comment  = comment
        self.nMesh = int(data[0])
        self.nTime = int(data[1])
        self.mini = data[2]
        self.maxi = data[3]
        self.mesh = np.array(data[4:4+self.nMesh])
        self.time = np.array([t*1e9 for t in data[4+self.nMesh:4+self.nMesh+self.nTime]]) # scale for nano seconds
        
        output = np.zeros((self.nMesh, self.nTime)) # Pre-allocate
        for i in range(self.nMesh):
            start = 4+self.nMesh+(i+1)*self.nTime
            stop  = start + self.nTime # Go one time brick further
            output[i] = data[start:stop]
        self.output = np.array(output)*scale
        
        # calculates the Lagranian distance based on mesh spacing in inf file
        self.X, self.lim, self.mesh_prop = self.hyadesInfReader(inf_fname)
        
        # reads and formats the input tv values in a dictionary
        self.tv = self.getTV(inf_fname)
        
        
    def printMeshProp(self):
        '''method to print the mesh properties specified in the .inf file'''
        n = len(self.mesh_prop)
        print('Number of regions: ', n)
        for i in range(n):
            info = ('Region: ' + str(i+1) +
                    ' Mesh Start: ' + str(self.mesh_prop[i][0]) +
                    ' Mesh End: '   + str(self.mesh_prop[i][1]) +
                    ' Pos Start: '  + str(self.mesh_prop[i][2]) +
                    ' Pos End: '    + str(self.mesh_prop[i][3]) +
                    ' Increment: '  + str(self.mesh_prop[i][4]) )
            print(info)
            
            
    def hyadesDatReader(self, filename):
        '''
        Read the specified .dat file and seperates the numbers from the mesh_lines at the bottom.
        The data is used to create all of the attributes of the Output class.
        '''
        if not filename.endswith('.dat'):
            filename += '.dat'
        with open(filename) as fh:
            fContents = fh.read()
        fContents = fContents.split()
        end_of_nums = fContents.index('Problem') # assume this is the first non number
    #    print('end_of_nums index: ', end_of_nums)
        try:
            data = [float(num) for num in fContents[0:end_of_nums]]
        except:
            raise Exception('Non-number before the word "Problem" in file contents')
        comment = ' '.join(fContents[end_of_nums:])   

        return data, comment
    
    
    def hyadesInfReader(self, inf_filename):
        '''
        Read the specified .inf file looking for the lines that declare
        the mesh properties. The mesh properties are printed and passed out 
        of the function. They are incorporated in the class for the lagranian distance.
        '''
        with open(inf_filename+'.inf') as fh:
            contents = fh.readlines()
        description = ''
        for line in contents:
            if line.lower().startswith('c simulation'):
                description = line
            if line.lower().startswith('c xray'):
                Xray_line = line
#         print(description)
                
        if 'Xray_line' in locals():
            split = Xray_line.split()
            self.xray_probe_time = (float(split[-2]), float(split[-1]))
        else:
            self.xray_probe_time = None
            
        start = [i for i in range(len(description)) if description[i]=='[']
        stop  = [i for i in range(len(description)) if description[i]==']']
        materials = [description[a+1:b] for a, b in zip(start, stop)]
        self.material_of_interest = None
        for i in range(len(materials)):
            if '!' in materials[i]:
                materials[i] = materials[i].replace('!','')
                self.material_of_interest = materials[i]
            if '$' in materials[i]:
                materials[i] = materials[i].replace('$', '')
                self.shock_MOI = materials[i]
            
        mesh_lines = [line for line in contents if line.startswith('mesh')]
        num_of_regions = len(mesh_lines) # number of 'mesh' lines

        assert num_of_regions != 0, 'Found no mesh properties in .inf file'

        mesh_lines = [line.split() for line in mesh_lines] # seperate words within each line
        mesh_prop = []
        # assumed variables arranged as follows in mesh_prop array:
        # starting mesh index, end mesh index, starting distance, end dist, increment
        for line in mesh_lines:
            mesh_prop.append([float(num) for num in line[1:]])
            # the 0 entry is the word mesh, so start at 1
#         print(f'MESH PROP: {mesh_prop}')
        X = [] # variable for the lagranian distance
        lim = []
        self.material_properties = {}
        for material, properties in zip(materials, mesh_prop):
            start_mesh = properties[0]; end_mesh = properties[1];
            start_dist = properties[2]; end_dist = properties[3];
            increment  = properties[4]
            delta_dist = end_dist - start_dist
            delta_mesh = end_mesh - start_mesh
            self.material_properties[material] = {'startMesh':int(start_mesh),'endMesh':int(end_mesh),
                                                   'startX':start_dist*1e4,    'endX':end_dist*1e4,
                                                   'increment':increment}
           
            if increment == 1:
                # fzt - first zone thickness
                fzt = delta_dist / delta_mesh
            else:
                fzt = delta_dist*( (1-increment) / (1-(increment**delta_mesh)) )

            x_material = [start_dist] # Variable specific to this material
            t = [fzt]
#             print('delta_mesh: ', material, delta_mesh)
            for i in range(1, int(delta_mesh)): 
                t_i = t[i-1]*increment
                x_i = x_material[i-1] + t_i            
                x_material.append(x_i)
                t.append(t_i)
            X.append(x_material) # add this material to the total lagranian dist
            lim.append(end_dist)

        lim = [y*1e4 for y in lim]
        final_X = [] # need to get numbers out of list of lists
        for material in X:
            for num in material:
                final_X.append(num*1e4) # scale for microns
        final_X = np.array(final_X)

        return final_X, np.array(lim), np.array(mesh_prop)
    
    
    def getTV(self, inf_file):
        '''Get the tv values for all sources in a .inf'''
        with open(inf_file+'.inf') as f:
            contents = f.readlines()
        tv = {}
        for line in contents:
            # skip blank or commented out lines
            if line=='\n' or line.startswith('c ') or (line.replace(' ','').replace('\n','')==''):
                continue
            if line.startswith('tv end'):
                continue
            split = line.split()
            if len(split)==0:
                continue
            # add a key for every new source
            if split[0].lower()=='source': 
                key = split[1]
                key_time  = key+'-t'
                key_value = key+'-v'

                tv[key_time]  = []
                tv[key_value] = []

            # add tv values for the current source
            if split[0].lower()=='tv':
                _, t, v = split
                tv[key_time].append(float(t))
                tv[key_value].append(float(v))

        return tv


class shockVelocity:
    '''Class to handle a calculating the shock velocity from a hyades simulation'''
    def __init__(self, hyades_path):
        self.file = hyades_path
        self.time, self.Us, (pres, rho, Up) = self.calculateShockVelocity()
        self.shock_info = {'pressure':pres, 'density':rho, 'particleVelocity':Up}
        self.material_properties = {}
        
        interfaces = np.where( np.diff(rho) != 0 )[0]
        hyades = createOutput(hyades_path, 'Pres')
        if 'shock_MOI' in vars(hyades):
            self.shock_MOI = hyades.shock_MOI
        for i, mat in enumerate(hyades.material_properties):
            if i==0: # first material time starts at 0
                time_in = 0
                time_out = self.time[interfaces[i]]
            elif i==len(hyades.material_properties)-1: # last material time ends when time ends
                time_in = self.time[interfaces[i-1]]
                time_out = self.time[-1]
            else:
                time_in = self.time[interfaces[i-1]]
                time_out = self.time[interfaces[i]]
            material_thickness = hyades.material_properties[mat]['endX'] - hyades.material_properties[mat]['startX']
            average_speed = (time_out - time_in) / material_thickness # units? microns per nanosecond ?
            
            self.material_properties[mat] = {'timeIn':  time_in,
                                             'timeOut': time_out,
                                             'averageShockSpeed': average_speed}

    def calculateShockVelocity(self,):
        '''
        Trying to debug my translation of the MatLab code to calculate Shock Velocity from a Hyades run
        Works on a test case on August 19, 2019
        '''
        hyades_path = self.file
        hyades_pres = createOutput(hyades_path, 'Pressure')
        hyades_Up   = createOutput(hyades_path, 'Particle Velocity')
        hyades_rho  = createOutput(hyades_path, 'Density')
        start, stop   = 10, len(hyades_pres.time) # limits on the loop
        threshold     = 10 # minimum GPa to consider a shock
        offset_points = 10 # window size for finding max pressure in shock front
        pressure          = np.zeros((stop-start))
        density           = np.zeros((stop-start))
        particle_velocity = np.zeros((stop-start))
        time              = np.zeros((stop-start))
        j = 0
        for i in range(start, stop):
            index = max(np.where(hyades_pres.output[:, i] > threshold)[0]) # last instance of the condition
            pressure_slice = hyades_pres.output[index-offset_points:index+1, i]
            pressure_index = np.argmax(pressure_slice) # index of the maximum wrt the length of the pressure slice
            loc = pressure_index + index - offset_points
            
            # update pressure, particle velocity, time, density
            pressure[j]          = pressure_slice.max()
            particle_velocity[j] = hyades_Up.output[loc, i]
            time[j]              = hyades_rho.time[i]
            density[j]           = hyades_rho.output[loc,0]
            j += 1
        
        shock_velocity = pressure / (density * particle_velocity)
        return time, shock_velocity, (pressure, density, particle_velocity)

    def quickPlot(self, ax=None):
        '''Easy way to plot the shock velocity. Labels when the shock enters different materials'''
        if ax is None:
            fig, ax = plt.subplots()
        ax.plot(self.time, self.Us)
        i=0
        for mat in self.material_properties:
            text_x = (self.material_properties[mat]['timeOut'] +  self.material_properties[mat]['timeIn']) / 2
            text_y = ax.get_ylim()[1]
            ax.text(text_x, text_y * (0.95-0.1*(i%2)), mat, ha='center')
            ax.axvline(self.material_properties[mat]['timeOut'], color='k', linestyle=':', alpha=0.5)
            i+=1
        ax.set(title=f'{os.path.basename(self.file)} Shock Velocity',
               xlabel='Time (ns)', ylabel='Shock Velocity (km/s)')
        plt.show()
            
        return ax


    
    

if __name__ == '__main__':
    name = 'Fe_15um'
    variable = '_U'
    myDir = '/Users/ckrill1/hyades/Fe_batch/Fe_15um/'
    
    U = Output( myDir+name+variable, myDir+name, 1e-5)
