# Python for Hyades - PyHy 
This repository is a Python wrapper for the Hyades hydrocode.
The primary goal of this repository is lower the barrier to entry of the Hyades hydrocode by 
automating the tedious parts of the most common uses including creating input files, running the simulation,
organizing the outputs, visualizing the inputs and outputs, and fitting Hyades velocities to experimental measurements.
  
Some aspects of Hyades were deliberately left out, and the user does not have control over every aspect of Hyades inputs and outputs.
This repository is supposed to make the basics very easy, not completely replace the Hyades command line interface.

This repository assumes the user has familiarity with Hyades simulations and basic terminal usage.
Little to no Python knowledge is required.

Developed by Connor Krill et al. under the Wicks Lab at Johns Hopkins University.  
First Published: December 2021  
Last Updated: December 2021

___
# Requirements & Set Up
This repository was written on Python version 3.7.6 and requires Python 3. It uses several additional Python packages,
all of which are listed under `pyhy/requirements.txt`.
To install all packages at once, navigate to the PyHy repository in terminal and use the command 
`pip install -r requirements.txt`. This will attempt to install compatible versions of all required packages if they are not 
already present on your machine.

This repository should work on all operating systems and was tested on a MacOS installation of Hyades.

___
# GUIs for:

### Creating Inputs
`inf_GUI.py` is a GUI to help create the input files for Hyades.
Gives user easy control over many, but not all, options for Hyades input.
 
Use:
* Launch the GUI from terminal with the command `python inf_GUI.py`
* Set the simulation parameters, such as length of the simulation and time step in the output.
* Input the number of layers and click `generate layers`.
This will bring up more settings to be specified for each layer.  
* Set the Pressure, Temperature, and/or Laser drives by specifying the two-column text file to be used.
Examples of inputs can be found under `pyhy/data/tvInputs`
* Click the button to write the file, which will be created in `pyhy/data/inf` by default.
**You do not need Hyades installed for the `Write Inf` button to work.**
* Click the button to run Hyades. **You must have Hyades installed locally for the `Run Hyades` button to work.**

To add or remove a material as an option from the inf_GUI, edit the excel spreadsheet `pyhy/tools/inf_GUI_materials.xlsx`.
Follow the formatting (using comma separated entries for materials with multiple elements) used in existing columns.

### Viewing Data  
`view_hyades_GUI.py` is a GUI to explore the output of a Hyades simulation. Launch it with `python view_hyades_GUI.py`
and use the onscreen buttons to load a file and view different variables.
There are options for viewing lineouts, creating simple animations, and saving data. See the section on Plotting Hyades under Command Line Interfaces for more graphics.
The options to save static figures and export a .csv of the data on screen are built into the GUI.
Saving animations requires ffmpeg installed.

---
# Command Line Interfaces for:

### Running Hyades
`run_hyades.py` is a command line interface to run multiple Hyades simulations.  
Run `python run_hyades.py` in terminal to run all simulations 
and neatly format the output for all .inf files in `pyhy/data/inf`.
See `python run_hyades.py --help` for more details and examples.

### Plotting Hyades
`plot.py` is a command line interface to plot common types of Hyades graphics.
It can create many different static graphics, such as XT Diagrams, diagrams of the target design, 
and/or a plot of the shock velocity.
Please note the shock velocity function is only designed for shock simulations 
and may not yield useful results for ramp compression.
See `python plot.py --help` for more details and examples.

### Animating Hyades
`animate.py` is a command line interface to make simple animations of Hyades runs.
It can create animations of the Eulerian position of a sample during a simulation, distributions of a variable over time,
or show the lineout of any variable over time. See `python animate.py --help` for more details and examples.

### Optimizing Hyades

**Note: As of Dec 1, 2021 the PyHy Optimizer is only intended to optimize Particle Velocities in ramp compression experiments.
Options to optimize Shock Velocity in shock compression experiments will be added.**

`optimize.py` is a command line script to fit a Hyades simulated velocity to a VISAR measured velocity.
To run the optimizer, three things must be set up before hand. This repository includes an example to run an optimization
for the experimental data `pyhy/data/experimental/FeSi_s77742.xlsx`. 
This experimental data is from [Crystal structure and equation of state of Fe-Si alloys 
at super-Earth core conditions (Wicks et al., 2018)](https://www.osti.gov/pages/biblio/1634289). 
To run this optimization, the following would need to be set up inside a directory `pyhy/data/FeSi_s77742`:
1. `pyhy/data/FeSi_s77742/FeSi_s77742_setup.inf` **The filename format `FeSi_s77742_setup.inf` must be used.** 
This a Hyades .inf file with the phrase `TV_PRES` inserted where the tv pressure values would go. 
This can be done for you by selecting `Set Pressure for Optimization` while using `inf_GUI.py`. 
Additionally, inside `inf_GUI.py` you must set a Material of Interest, 
which leaves a comment in the .inf file indicating which layer should be used for velocity calculations.
2. `pyhy/data/experimental/FeSi_s77742.xlsx` an excel file containing the experimental data. 
**Any filename can be used, as long as it is specified in the .cfg**. 
See `pyhy/data/experimental/FeSi_s77742.xlsx` for formatting.
3. `pyhy/data/FeSi_s77742/FeSi_s77742.cfg` a short text file with parameters for the optimization. 
**The filename format `FeSi_s77742.cfg` must be used.** See `pyhy/optimizer/example.cfg` for formatting and further details.

Once these three things are set up, the optimization can be run with `python optimize.py FeSi_s77742 --run`.
The iteration number, residual, and pressure drive will be printed in the terminal.
The optimization can be stopped at any time by pressing `control + C` or `control + Z`.
Once completed, the optimization output can be plotted and compared to experiment.
See `python optimize.py --help` for more details.

---
### Building off these tools
If you wish to use this repository to build your own graphics or customize Hyades inputs, all of the scripts are written
as callable classes and functions that you can use in your own Python scripts. `pyhy/tools/hyades_reader.py` is used to 
handle all the data output from Hyades, and `pyhy/graphics/static_graphics.py` provides many examples of how the 
`HyadesOutput` class can be used to plot the data in many different ways.

```
                      ___      _  _      
                     | _ \_  _| || |_  _ 
                     |  _/ || | __ | || |
                     |_|  \_, |_||_|\_, |
                          |__/      |__/ 
               Developed by the Wicks Lab at JHU
```
