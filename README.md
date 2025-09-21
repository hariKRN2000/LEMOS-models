# LED-Embedded Microplate for Optogenetic Studies (LEMOS)
Experiment run files and Dynamic models used to study the dynamics of optogenetic two component system and develop closed loop control strategies <br>

## Installation: 
To run the files in the repository, clone this repository via git. into your computer using the command:<br>
```
git clone https://github.com/hariKRN2000/Gene-Expression-Across-Growth-Stages.git
```
Once cloned, we recommend installing the dependencies in a new virtual environment (with Python version greater than 3.9). <br> 
Example code to set up a virtual environment in desired directory using terminal command: 
```
python -m venv <environment name>
```
And activate the environment using: 
Linux/macOS: Run ```source <environment_name>/bin/activate``` <br>
Windows: Run ```<environment_name>\Scripts\activate.bat``` <br>
This command activates the environment and modifies your shell's path to point to the virtual environment's Python interpreter and pip. <br>

## File Information: 
There are three types of files: 
1) Used to simulate and analyze dynamic models:
-- ```run_open_loop_simulation.ipynb``` : Jupyter notebook demonstrating the simulation of the open loop experiment under constant light inputs, using the growth dependent (GEAGS) model. 
-- ```run_p_control_simulation.ipynb``` : Jupyter notebook demonstrating the simulation of the P-control experiment, using the growth dependent (GEAGS) model. 
--```parameters``` : Folder containing the model parameters as csv files. Parameter files are imported by  ```run_open_loop_simulation.ipynb``` and ```run_p_control_simulation.ipynb```.
--```experiment_data``` : Folder containing the experimental data imported by  ```run_open_loop_simulation.ipynb``` and ```run_p_control_simulation.ipynb```.
--```model_equations_and_simulators``` : Contains the python files used to define the model equations and functions developed to simulate the experiments in ```run_open_loop_simulation.ipynb``` and ```run_p_control_simulation.ipynb```.
--```growth independent models``` : Folder containing the implementation of open loop experiments using the growth-independent dynamic models. 
--```Dead time analysis``` : Folder containing the files used to analyze the inherent system dead time in gene expression.
--```PI and PID control files``` : 

3) Used to analyze experimental data
-- ```timing diagram``` : Folder containing the python files used to generate the variation in duty cycle across the experimental time scale.
   
4) Used to run the experiments

