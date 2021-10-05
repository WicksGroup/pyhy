# PyHy
Python for Hyades - PyHy  
This repository is a Python wrapper for the Hyades hydrocode.
It contains tools to help with creating input files, running the simulation,
organizing the outputs, and visualizing the inputs and outputs.

This repository assumes familiarity with Hyades simulations and basic terminal usage.
Almost no Python knowledge is required.

---

### Creating Inputs
`inf_GUI.py` is a GUI to help create the input files for Hyades.
Gives user easy control over many, but not all, options for Hyades input.
 
Use
* Launch the GUI from terminal with the command `python inf_GUI.py`
* Set the simulation parameters, such as length of the simulation and time step in the output
* Input the number of layers and click `generate layers`. This will bring up more settings to be specified for each layer.  
* Set the Pressure, Temperature, and/or Laser drives by specifying the two-column text file to be used. Examples of inputs can be found under `data/tvInputs`
* Click the button to write the file, which will be created in `data/inf` by default. **You do not need Hyades installed for the `Write Inf` button to work.**
* Click the button to run Hyades. **You must have Hyades installed locally for the `Run Hyades` button to work.**

Adding or Removing a material:  
* To add or remove a material as an option from the inf_GUI, edit the excel spreadsheet `inf_GUI_materials.xlsx`.
Follow the formatting (using comma separated entries for materials with multiple elements) used in existing columns.
---
### Running Hyades
`run_hyades.py` is a command line interface to run multiple Hyades simulations.  
Run `python run_hyades.py` in terminal to run all simulations and neatly format the output for all .inf files in `data/inf`.
See `python run_hyades.py --help` for more details and examples.

### Plotting Hyades
`plot_hyades.py` is a command line interface to plot common types of Hyades graphics.
It can create many different static graphics, such as XT Diagrams, diagrams of the target design, and/or a plot of the shock velocity.
Please note the shock velocity function is only designed for shock simulations and may not yield useful results for ramp compression.
See `python plot_hyades.py --help` for more details and examples.

### Animating Hyades
`animate_hyades.py` is a command line interface to make simple animations of Hyades runs.
It can create animations of the Eulerian position of a sample during a simulation, distributions of a variable over time,
or show the lineout of any variable over time. See `python animate_hyades.py --help` for more details and examples.

```
                      ___      _  _      
                     | _ \_  _| || |_  _ 
                     |  _/ || | __ | || |
                     |_|  \_, |_||_|\_, |
                          |__/      |__/ 
               Developed by the Wicks Lab at JHU
```
