# PyHy
Python for Hyades - PyHy  
This repository is a Python wrapper for the Hyades hydrocode. It contains tools to help with creating input files, running the simulation, organizing the outputs, and visualizing the inputs and outputs.  

## inf_GUI
A GUI to help create the input files for Hyades. Gives user easy control over many, but not all, options for Hyades input.
 
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

## Optimizer

Determines the pressure history of an experimental sample by comparing the Hyades simulated velocity to the experimentally measured one.
