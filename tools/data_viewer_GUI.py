#!/usr/bin/env python3
'''
tkinter GUI to view the data output from HYADES simulations.
Allows for nearly all lineouts from the data
Plot pressure, density, particle velocity, shock velocity, or temperature on the y-axis
Plot distance or time on the x-axis
Includes animation features.
Includes drop down menu (along top of screen) to save many file types

Connor Krill 2019
'''
import matplotlib
matplotlib.use("TkAgg")
from hyades_output_reader import createOutput
import tkinter
from IPython import display
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import time
import os
import pandas as pd
plt.style.use('seaborn')


class App:
    
    def __init__(self, master, path, run, var):
        
        root.title('Hyades Data Viewer GUI')
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        
#        self.filename = os.path.join(path, run, run)
#        self.hyades = createOutput(self.filename, var)
        row = 1
        # Big title at the top
        myLabel = Label(root, text='Hyades Data Viewer')
        myLabel.grid(row=row, column=1, columnspan=3, sticky='NEW', padx=(100,0), pady=(10,0))
        myLabel.config(font=('Arial', 16))
        row += 1
        
        # Select the data from a folder
        self.select_fname = StringVar(); self.select_fname.set('No file selected')
        Button(root, text='Select file', command=self.selectDir).grid(row=row, column=1, sticky='NW', 
                                                                      padx=(100,0), pady=(10,0))        
        self.file_label = StringVar()
        self.file_label.set('Use button to select a folder to view')
        Label(root, textvariable=self.file_label).grid(row=row, column=2, sticky='NW', pady=(10,0))
        row +=1
        
        Label(root, text='_'*100).grid(row=row, column=1, columnspan=3, sticky='NEW', padx=(100,0))
        row += 1
        
        # Animation Controls
        self.ix = IntVar()
        Label(root, text='Click Play to start the animation').grid(row=row, column=1, sticky='NW', padx=(100,5))
        Label(root, text='[space bar] - pause/play').grid(row=row, column=2, sticky='NW')
        row += 1
        Button(root, text='Play Animation', command=self.playAnimation).grid(row=row, column=1, sticky='NW', padx=(100,5))
        Label(root, text='[L/R arrow keys] - move one frame').grid(row=row, column=2, sticky='NW')
        row += 1
        self.ix_scale = Scale(master, from_=0, to=142, #self.hyades.nTime-1,
                              var=self.ix, command=self.updateIX,
                              length=250, orient='horizontal')
        self.ix_scale.grid(row=row, column=1, sticky='NWE', columnspan=3, padx=(100,10))
        row += 1
        Label(root, text='User slider to move through sample').grid(row=row, column=1, sticky='NW', padx=(100,5))
        row += 1
        
        padx = (100,5)
#         Button(root, text='Save Animation', command=self.saveAnimation).grid(row=row, column=1, sticky='NW',
#                                                                              padx=padx, pady=(10,0))
#         Label(root, text='Save a complete loop of the animation').grid(row=row, column=2, sticky='NW',
#                                                                        pady=(10,0))
#         row += 1
#         Button(root, text='Save Plot', command=self.savePlot).grid(row=row, column=1, sticky='NW',padx=padx)
#         Label(root, text='Save the current plot as a static .png').grid(row=row, column=2, sticky='NW')
#         row += 1
#         Button(root, text='Save ASCII', command=self.saveCSV).grid(row=row, column=1, sticky='NW', padx=padx)
#         Label(root, text='Save the current data in the plot to a .csv file').grid(row=row, column=2, sticky='NW')
#         row += 1
        
        Label(root, text='_'*100).grid(row=row, column=1, columnspan=3, sticky='NEW', padx=padx)
        row += 1
        
        # Radiobuttons to select variables for the X and Y axis
        self.var = StringVar(); self.var.set('Pressure')
        Label(root, text='Select Y-axis variable').grid(row=row, column=1, columnspan=2, sticky='NEW', padx=(100,0), pady=(10,0))
        for i, op in enumerate(['Pressure', 'Density', 'Particle Velocity', 'Shock Velocity']):
            Radiobutton(root, text=op, 
                        value=op, variable=self.var,
                        command=self.updateVariable).grid(row=row+i+1, column=1, sticky='NW', padx=(100,0))
        
        for i, op in enumerate(['Temperature', 'Radiation Temperature', 'Ion Temperature']):
            Radiobutton(root, text=op,
                        value=op, variable=self.var,
                        command=self.updateVariable).grid(row=row+i+1, column=2, sticky='NW')
        
        self.x_mode = StringVar(); self.x_mode.set('Distance')
        x_mode_options = ['Distance', 'Time']
        Label(root, text='Select X-axis Variable').grid(row=row, column=3, sticky='NW', pady=(10,0))
        for i, mode in enumerate(x_mode_options):
            Radiobutton(root, text=mode,
                        value=mode, variable=self.x_mode,
                        command=self.updateXmode).grid(row=row+i+1, column=3, sticky='NW')
            
        # Initial plotting and labels
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.df = pd.read_csv('./DatasaurusDozen.csv')
        self.datasaur = self.ax.scatter([], [])
        self.ax.set(title='Select a file to begin',
                    xlabel='X Label', ylabel='Y Label',
                    xlim=(0,100), ylim=(0,100))

#
        # Initialize some variables to hold text but do not display them yet
        label_text_time = self.ax.text(self.ax.get_xlim()[1]*0.95, self.ax.get_ylim()[1]*0.9, 'Material', ha='right')
        self.label_text_time = label_text_time
        self.txt   = self.ax.text(self.ax.get_xlim()[1]*0.95, self.ax.get_ylim()[1]*0.95, 'Time', ha='right')

        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().grid(row=15, column=1, columnspan=10, rowspan=10, sticky='NSEW')
        # Configure row / column settings, fixed some spacing issues with the graph
        col, row = root.grid_size()
        for i in range(row):
            root.rowconfigure(i, weight=1)
            for j in range(col):
                root.columnconfigure(j, weight=1)
                
        # Create and fill the Menu at the top of the screen
        root_menu = tkinter.Menu(root)
        root.config(menu = root_menu)
        
        # creating sub menus in the root menu
        file_menu = tkinter.Menu(root_menu) # it intializes a new su menu in the root menu
        #file_menu.add_command(label = "New file.....", command = function)
        root_menu.add_cascade(label = 'File', menu=file_menu) # it creates the name of the sub menu
        file_menu.add_command(label = 'Open file', command=self.selectDir)
        file_menu.add_separator() # it adds a line 
        file_menu.add_command(label = 'Exit', command=root.quit)

        # creating another sub menu for saving
        save_menu = tkinter.Menu(root_menu)
        root_menu.add_cascade(label='Save', menu=save_menu)
        save_menu.add_command(label='Save Animation', command=self.saveAnimation)
        save_menu.add_command(label='Save Plot', command=self.savePlot)
        save_menu.add_command(label='Save CSV', command=self.saveCSV)
        # End Menu

        
    def animate(self, i):
        '''Helper function for the animator'''
        self.ix_scale.set(i)
        self.updateIX() # trying to get the saved animation to work
        if self.x_mode.get()=='Distance':
            self.line.set_ydata(self.hyades.output[:len(self.hyades.X),i])
        else:
            self.line.set_ydata(self.hyades.output[i,:])
        return self.line
    
    
    def playAnimation(self):
        '''Function for the button
           This isnt perfect weird things happen restarting and playing the animation'''
        def update_index():
            '''Helper function for the animator'''
            if 'index' not in locals():
                index = self.ix_scale.get()
            if self.x_mode.get()=='Distance':
                maximum = self.hyades.nTime
            else:
                maximum = self.hyades.nMesh
            while (0 <= index) and (index < maximum - 1):
                index += anim.direction
                yield index
        
        def on_press(event):
            '''Function to handle key presses during the animation'''
            if event.key.isspace():
                if anim.running:
                    anim.event_source.stop()
                else:
                    anim.event_source.start()
                anim.running ^= True
            elif event.key == 'left':
                anim.direction = -1
            elif event.key == 'right':
                anim.direction = +1
            if event.key in ['left','right']:
                index = anim.frame_seq.__next__()
                self.animate(index)

        self.fig.canvas.mpl_connect('key_press_event', on_press)
        anim = animation.FuncAnimation(self.fig, self.animate, frames=update_index,
                                      interval=10, blit=False, repeat=False)
        anim.running = True
        anim.direction = +1
        self.fig.canvas.draw()
    
    
    def saveAnimation(self):
        '''Save a .mp4 animation of the slider moving through its range'''
        if self.var.get()=='Shock Velocity':
            tkinter.messagebox.showwarning("Warning from Save Animation", 'WARNING: Nothing to animate when Shock Velocity is plotted')
            return
        
        print('Saving movie...')
        if self.x_mode.get()=='Distance':
            frame_num = self.hyades.nTime
        else:
            frame_num = self.hyades.nMesh
        anim = animation.FuncAnimation(self.fig, self.animate,
                                       frames=frame_num,
                                       interval=10, blit=False, repeat=False)
        Writer = animation.writers['ffmpeg']
        # Speed up the video when the time step is small
        # time step of 0.1 should have 12 fps, this formula scales accordingly from there
        if len(self.hyades.time) > 500:
            fps = 32
        elif (self.hyades.time[1] - self.hyades.time[0]) > 0.5:
            fps = 24
        else:
            fps = int( 12 * (0.1 / (self.hyades.time[1] - self.hyades.time[0])) )
        writer = Writer(fps=fps, metadata=dict(artist='Me'), bitrate=1800)
        
        selection = self.var.get()
        if selection=='Pressure':            var = 'Pres'
        elif selection=='Density':           var = 'Rho'
        elif selection=='Temperature':       var = 'Te'
        elif selection=='Particle Velocity': var = 'Up'
        
        if self.x_mode.get()=='Distance': suffix = "Time"
        else:                             suffix = "Distance"
        
        basename = f"{os.path.basename(self.filename)}_{var}_{suffix}"
        out_fname = basename
        counter = 2
        while out_fname+".mp4" in os.listdir("../data/"):
            out_fname = basename + f"_{counter}"
            counter += 1

        anim.save(f'../data/{out_fname}.mp4', dpi=200, writer=writer)
        print('Saved', out_fname)
        tkinter.messagebox.showinfo("Save Message", f'Succesfully saved the animation {out_fname!r}')
    
    
    def savePlot(self):
        '''Save a .png of the graph currently on screen'''
        selection = self.var.get()
        if selection=='Pressure':            var = 'Pres'
        elif selection=='Density':           var = 'Rho'
        elif selection=='Temperature':       var = 'Te'
        elif selection=='Radiation Temperature': var = 'Tr'
        elif selection=='Ion Temperature': var = 'Ti'
        elif selection=='Particle Velocity': var = 'Up'
        elif selection=='Shock Velocity'   : var = 'Us'
        if self.x_mode.get()=='Distance':
            suffix = f'{self.hyades.time[self.ix_scale.get()]:.1f}ns'
        else:
            suffix = f'{self.hyades.X[self.ix_scale.get()]:.1f}um'
        if selection=='Shock Velocity':
           basename = f'{os.path.basename(self.filename)}_{var}'
        else:
            basename = f'{os.path.basename(self.filename)}_{var}_{suffix}'
        out_fname = basename
        counter = 2
        while out_fname+".png" in os.listdir("../data/"):
            out_fname = basename + f"_{counter}"
            counter += 1
        
        self.fig.savefig(f'../data/{out_fname}.png', dpi=200)
        print('Saved', out_fname)
        tkinter.messagebox.showinfo("Save Message", f'Succesfully saved the plot {out_fname!r}')
        
    
    def saveCSV(self):
        '''Save a .csv of the data currently on screen'''
        if self.x_mode.get()=='Distance':
            x_title = 'Distance (um)'
            index = f'{self.hyades.time[self.ix_scale.get()]:.1f}ns'
        else:
            x_title = 'Time (ns)'
            index = f'{self.hyades.X[self.ix_scale.get()]:.1f}um'
        var = self.var.get()
        if var=='Pressure':            y_title = 'Pressure (GPa)'
        elif var=='Density':           y_title = 'Density (g/cc)'
        elif var=='Temperature':       y_title = 'Temperature (K)'
        elif selection=='Radiation Temperature': y_title = 'Radiation Temperature (K)'
        elif selection=='Ion Temperature': y_title = 'Ion Temperature (K)'
        elif var=='Particle Velocity': y_title = 'Particle Velocity (km/s)'
        elif var=='Shock Velocity'   : y_title = 'Shock Velocity (km/s)'

        df = pd.DataFrame({x_title: self.line.get_xdata(),
                           y_title: self.line.get_ydata(),})
        if var=='Shock Velocity':
            basename = f'{os.path.basename(self.filename)}_{var.replace(" ","")}'
            comment = f'{var} lineout of {os.path.basename(self.filename)}'
        else:
            basename = f'{os.path.basename(self.filename)}_{var.replace(" ","")}_{index}'
            comment = f'{var} lineout of {os.path.basename(self.filename)} taken at {index}'
        out_fname = basename
        counter = 2
        while out_fname+".csv" in os.listdir("../data/"):
            out_fname = basename + f"_{counter}"
            counter += 1
        with open(f'../data/{out_fname}.csv', 'a') as f:
            f.write(comment + '\n')
            df.to_csv(f, index=False, float_format='%.4f')
        print('Saved', out_fname)
        tkinter.messagebox.showinfo("Save Message", f'Succesfully saved the csv {out_fname!r}')
        
    
    def selectDir(self):
        '''Function to create a hyadesOutput when a new data directory is selected'''
        fname = filedialog.askdirectory(initialdir ='../data', title='Select Hyades output')
        if self.datasaur.get_visible():
            self.datasaur.set_visible(False)
        print(fname)
        end_dir = os.path.basename(os.path.normpath(fname))
        self.file_label.set(end_dir)
        found_variable = []
        for v in ('Pres', 'Rho', 'U', 'Te'):
            status = any( [f.endswith(f'{v}.dat') for f in os.listdir(fname)] )
            found_variable.append(status)
        if all(found_variable):
            self.filename = os.path.join(fname, end_dir)        
            self.updateVariable()
            self.updateXmode()
            self.ax.set(title=f'{end_dir} Lineout')
            for L, T in zip(self.label_lines, self.label_text):
                L.remove()
                T.remove() # remove the labels while we still have access to them
            self.label_lines, self.label_text = [], []
            y = 0.85; old_x = -100
            for mat in self.hyades.material_properties:
                label_line = self.ax.axvline(mat['startX'],
                                             color='k', linestyle='dashed', linewidth=1)
                x = (mat['startX'] + mat['endX']) / 2
                # if a label would be closer than 10% of the window width to the previous label, then lower it
                if (x - old_x) < ((self.ax.get_xlim()[1] - self.ax.get_xlim()[0]) * 0.1):
                    y -= 0.05
                else:
                    y = 0.85
                label_text = self.ax.text(x, self.ax.get_ylim()[1] * y, mat['material'], ha='center')
                self.label_lines.append( label_line )
                self.label_text.append( label_text )
                old_x = x
        self.canvas.draw()

        
    def updateXmode(self):
        '''Update plot, xlim, text._x'''
        self.ix_scale.set(0)
        ix = self.ix_scale.get()
        if self.x_mode.get()=='Distance':
            self.line.set_data(self.hyades.X, self.hyades.output[:len(self.hyades.X), ix])
            self.ax.set(xlim=(0,self.hyades.X.max()),
                        xlabel='Lagrangian Distance (um)')
            self.txt._text = f'{self.hyades.time[ix]} ns'
            self.txt._x    = self.ax.get_xlim()[1] * 0.95
            self.ix_scale.configure(to=self.hyades.nTime-1)
            for L, T in zip(self.label_lines, self.label_text):
                L.set_visible(True)
                T.set_visible(True)
            self.label_text_time.set_visible(False)
        elif self.x_mode.get()=='Time':
            self.line.set_data(self.hyades.time, self.hyades.output[ix, :])
            self.ax.set(xlim=(0,self.hyades.time.max()), 
                        xlabel='Time (ns)')
            self.txt._text = f'{self.hyades.X[ix]} um'
            self.txt._x    = self.ax.get_xlim()[1] * 0.95
            self.ix_scale.configure(to=len(self.hyades.X)-1)
            for L, T in zip(self.label_lines, self.label_text):
                L.set_visible(False)
                T.set_visible(False)
            self.label_text_time.set_visible(True)
            self.label_text_time._x = self.ax.get_xlim()[1] * 0.95
            self.label_text_time._y = self.ax.get_ylim()[1] * 0.9
        self.canvas.draw()
            
            
    def updateVariable(self):
        '''Update the variable when a new Pres, Rho, Temp, Up is selected'''
        if 'line' in vars(self):
            self.line.remove()
        selection = self.var.get()
        if selection=='Pressure':
            var = 'Pres'
            ylabel = 'Pressure (GPa)'
            color = 'blue'
        elif selection=='Density':
            var = 'Rho'
            ylabel = 'Density (g/cc)'
            color = 'green'
        elif selection=='Temperature':
            var = 'Te'
            ylabel = 'Temperature (K)'
            color = 'red'
        elif selection=='Ion Temperature':
            var = 'Ti'
            ylabel = 'Ion Temperature (K)'
            color = 'red'
        elif selection=='Radiation Temperature':
            var = 'Tr'
            ylabel = 'Radiation Temperature (K)'
            color = 'red'
        elif selection=='Particle Velocity':
            var = 'U'
            ylabel = 'Particle Velocity (km/s)'
            color = 'purple'
        elif selection=='Shock Velocity':
            var = 'Us'
            ylabel = 'Shock Velocity (kms/s)'
            color = 'black'

        if selection=='Shock Velocity':
            # Turn off the slider bc there is no index on the shock velocity
            self.ix_scale.config(state="disabled")
            # plot the shock velocity
            shock = createOutput(self.filename, var)
            self.line, = self.ax.plot(shock.time, shock.Us, color=color) # create a new line
            y_max = shock.Us.max() * 1.05
            y_min = shock.Us.min()
            self.ax.set(xlim=(min(shock.time), max(shock.time)), ylim=(y_min ,y_max),
                        xlabel='Time (ns)', ylabel=ylabel)
            # get rid of all the text onscreen
            self.txt._text = ''
            self.label_text_time._text = ''
            for L, T in zip(self.label_lines, self.label_text):
                L.remove()
                T.remove() # remove the labels while we still have access to them
            self.label_lines, self.label_text = [], []
            # add the material labels - calculated in Shock Velocity based on changes in density
            y = 0.85; old_x = -100
            for mat in shock.material_properties:
                label_line = self.ax.axvline(shock.material_properties[mat]['timeIn'],
                                             color='k', linestyle='dashed', linewidth=1, alpha=0.5)
                    
                x = (shock.material_properties[mat]['timeIn'] + shock.material_properties[mat]['timeOut']) / 2
                # if the new label would be placed closer than 10% of the window width, lower it
                if (x - old_x) < ((self.ax.get_xlim()[1] - self.ax.get_xlim()[0]) * 0.1):
                    y -= 0.05
                else:
                    y = 0.85
                label_text = self.ax.text(x, self.ax.get_ylim()[1] * y, mat, ha='center')
                self.label_lines.append( label_line )
                self.label_text.append( label_text )
                old_x = x
        else:
            # turn the slider back on
            self.ix_scale.config(state="normal")
            # create hyades and update the line
            self.hyades = createOutput(self.filename, var)
            self.line, = self.ax.plot(self.hyades.time, self.hyades.output[0,:], color=color) # create a new line
            ix = self.ix.get()
            if self.x_mode.get()=='Time':
                if ix > self.hyades.nMesh-1:
                    self.ix.set(0)
                self.line.set_data(self.hyades.time, self.hyades.output[ix, :])
                x_min, x_max = 0, self.hyades.time.max()
                xlabel = 'Time (ns)'
            elif self.x_mode.get()=='Distance':
                if ix > self.hyades.nTime-1:
                    self.ix.set(0)
                self.line.set_data(self.hyades.X, self.hyades.output[0:len(self.hyades.X), ix])
                x_min, x_max = self.hyades.X.min(), self.hyades.X.max()
                xlabel = 'Lagrangian Distance (um)'
            # format the plot
#            ten_micron_index = np.argmin( abs(self.hyades.X - 10) )
#            y_max = self.hyades.output[ten_micron_index:, :].max() * 1.05
            y_max = self.hyades.output[11:, :].max() * 1.05
#            y_min = self.hyades.output[ten_micron_index:, :].min()
            y_min = self.hyades.output.min()
            self.ax.set(xlim=(x_min, x_max), ylim=(y_min ,y_max),
                        ylabel=ylabel, xlabel=xlabel)
            self.txt._y = y_max * 0.95
            self.label_text_time._y = y_max * 0.9
            # remove the old material labels - need to do this when switching to / from shock velocity
            if ('label_lines' in vars(self)) and ('label_text' in vars(self)):
                for L, T in zip(self.label_lines, self.label_text):
                    L.remove()
                    T.remove() # remove the labels while we still have access to them
            self.label_lines, self.label_text = [], []
            # add the new material labels
            y = 0.85; old_x = -100
            for mat in self.hyades.material_properties:
                label_line = self.ax.axvline(mat['startX'],
                                             color='k', linestyle='dashed', linewidth=1, alpha=0.5)
                x = (mat['startX'] + mat['endX']) / 2
                # if the new label would be placed closer than 10% of the window width, lower it
                if (x - old_x) < ((self.ax.get_xlim()[1] - self.ax.get_xlim()[0]) * 0.1):
                    y -= 0.05
                else:
                    y = 0.85
                label_text = self.ax.text(x, self.ax.get_ylim()[1] * y,
                                           mat['material'], ha='center')
                self.label_lines.append( label_line )
                self.label_text.append( label_text )
                old_x = x
        self.canvas.draw()
        
        
    def updateIX(self, *args):
        '''Update the index being viewed within the sample'''
        if self.datasaur.get_visible():
            x = self.df.x[:self.ix_scale.get()]
            y = self.df.y[:self.ix_scale.get()]
            self.datasaur.set_offsets( np.array([x,y]).T )
        else:
            ix = self.ix.get()
            if self.x_mode.get()=='Time':
                self.txt._text = f'{self.hyades.X[ix]:.1f} um'
                self.line.set_data(self.hyades.time, self.hyades.output[ix, :])
                for mat in self.hyades.material_properties:
    #                x0 = mat['startX']
    #                x1 = mat['endX']
    #                x  = self.hyades.X[ix]
                    greater_than = ix >= mat['startMesh'] - 1
                    less_than    = ix < mat['endMesh'] - 1
                    if less_than and greater_than:
                        self.label_text_time._text = mat
                        break
            elif self.x_mode.get()=='Distance':
                self.txt._text = f'{self.hyades.time[ix]:.1f} ns'
                self.line.set_data(self.hyades.X, self.hyades.output[:len(self.hyades.X), ix])
        self.canvas.draw()


if __name__=='__main__':
    var = 'Pres'
    path = '../data/'
    file = 'demo'
    root = tkinter.Tk()
    app = App(root, path, file, 'Pres')
    root.mainloop()
