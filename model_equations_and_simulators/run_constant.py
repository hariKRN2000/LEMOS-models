
# import required files 

import numpy as np 
from .model_equations import run_TCS_model

def run_constant(total_time, initial_conditions, params, constant_input = 'green'):

    # Simulation parameters
    total_time = total_time  # Total simulation time in minutes
    dt = 1  # Time step in minutes
    initial_conditions = initial_conditions  # Initial mRNA and protein concentrations
    time_dark = 1

    # Variables to store results
    protein_concentrations = [initial_conditions[8]]
    solution_array = np.array([initial_conditions])
    time_array = [0]  # Array to store time points

    # Initial state
    state = initial_conditions
    current_time = 0
    


    # Run the simulation
    while current_time < total_time:

        
        # Get the current protein concentration
        protein_concentration = state[8]
        
        # set the input times: 
        if constant_input.lower() == 'green':
            time_green, time_red = 8, 0

        if constant_input.lower() == 'red':
            time_green, time_red = 0, 8

        if constant_input.lower() == 'dark':
            time_green, time_red, time_dark = 0, 0, 5

        
        # Repeat the green-red cycle twice (two 10-minute cycles)
        for _ in range(2):

            # Simulate Dark Period
            t_dark = np.linspace(current_time, current_time + time_dark, int(time_dark/dt) + 100)
            sol = run_TCS_model(state, t_dark, params, input = 'dark')
            state = sol.y[:,-1]
            current_time += time_dark
            time_array = np.concatenate((time_array, sol.t))
        
            # Store protein concentration after dark
            protein_concentrations = np.concatenate((protein_concentrations, sol.y[8,:]))

            # store the solution after dark period: 
            solution_array = np.vstack((solution_array, sol.y.T))

            # Simulate green light period
            if time_green == 0:
                pass
            
            else:
                t_green = np.linspace(current_time, current_time + time_green, int(time_green/dt) + 100)
                sol = run_TCS_model(state, t_green, params, input = 'green')
                state = sol.y[:,-1]
                current_time += time_green
                time_array = np.concatenate((time_array, sol.t))
            
                # Store protein concentration after green light
                protein_concentrations = np.concatenate((protein_concentrations, sol.y[8,:]))

                # store the solution after dark period: 
                solution_array = np.vstack((solution_array, sol.y.T))
            
            # Simulate red light period
            if time_red == 0:
                pass
            
            else:
                t_red = np.linspace(current_time, current_time + time_red, int(time_red/dt) + 100)
                sol = run_TCS_model(state, t_red, params, input = 'red')
                state = sol.y[:,-1]
                current_time += time_red
                time_array = np.concatenate((time_array, sol.t))
                
                # Store protein concentration after red light
                protein_concentrations = np.concatenate((protein_concentrations, sol.y[8,:]))

                # store the solution after dark period: 
                solution_array = np.vstack((solution_array, sol.y.T))

            # Simulate Dark Period
            t_dark = np.linspace(current_time, current_time + time_dark, int(time_dark/dt) + 100)
            sol = run_TCS_model(state, t_dark, params, input = 'dark')
            state = sol.y[:,-1]
            current_time += time_dark
            time_array = np.concatenate((time_array, sol.t))
        
            # Store protein concentration after dark
            protein_concentrations = np.concatenate((protein_concentrations, sol.y[8,:]))

            # store the solution after dark period: 
            solution_array = np.vstack((solution_array, sol.y.T))
        

        
            
    return time_array, protein_concentrations, solution_array