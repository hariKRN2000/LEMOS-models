
# import required files 

import numpy as np 
import scipy.integrate as scint 
from .model_equations import run_TCS_model

# P-controller for adjusting green light time
def p_controller(protein, set_point, gain, logic = 1):
    
    if logic == 1:
        error = set_point - protein
        time_green = gain * error 
        
        control_interval = 8
        # Clamp the green time to a maximum of 8 minutes
        
        if time_green >= control_interval:
            time_green = control_interval
        if time_green < 0:
            time_green = 0
        time_red = control_interval - time_green

    return time_green, time_red

def run_p_control(total_time, set_point, gain, initial_conditions, params):

    # Simulation parameters
    total_time = total_time  # Total simulation time in minutes
    dt = 1  # Time step in minutes
    set_point = set_point  # Desired protein concentration (fluorescence)
    gain = gain # Proportional gain for the controller
    initial_conditions = initial_conditions  # Initial mRNA and protein concentrations
    time_dark = 1
    set_point_reached = False

    # Variables to store results
    protein_concentrations = [initial_conditions[8]]
    solution_array = np.array([initial_conditions])
    time_green_values = []
    time_array = [0]  # Array to store time points

    # Initial state
    state = initial_conditions
    current_time = 0
    


    # Run the simulation
    while current_time < total_time:

        
        # Get the current protein concentration
        protein_concentration = state[8]
        
        # #if not set_point_reached:
        ctrl_point = set_point
        time_green, time_red = p_controller(protein_concentration, ctrl_point, gain)
        
        # Store green light duration
        time_green_values.append(time_green)
        
        # Repeat the green-red cycle twice (two 10-minute cycles)
        for _ in range(2):

            # Simulate Dark Period
            t_dark = np.linspace(current_time, current_time + time_dark, int(time_dark/dt) + 100)
            sol = run_TCS_model(state, t_dark, params, 0, input = 'dark')
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
                #state = odeint(protein_dynamics, state, t_green, args=(1,))[-1]  # Green light (1)
                sol = run_TCS_model(state, t_green, params, 0,  input = 'green')
                state = sol.y[:,-1]
                current_time += time_green
                # time_array = np.concatenate((time_array, t_green))
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
                #state = odeint(protein_dynamics, state, t_red, args=(0,))[-1]  # Red light (0)
                sol = run_TCS_model(state, t_red, params, 0,  input = 'red')
                state = sol.y[:,-1]
                current_time += time_red
                time_array = np.concatenate((time_array, sol.t))
                
                # Store protein concentration after red light
                protein_concentrations = np.concatenate((protein_concentrations, sol.y[8,:]))

                # store the solution after dark period: 
                solution_array = np.vstack((solution_array, sol.y.T))

            # Simulate Dark Period
            t_dark = np.linspace(current_time, current_time + time_dark, int(time_dark/dt) + 100)
            sol = run_TCS_model(state, t_dark, params, 0,  input = 'dark')
            state = sol.y[:,-1]
            current_time += time_dark
            time_array = np.concatenate((time_array, sol.t))
        
            # Store protein concentration after dark
            protein_concentrations = np.concatenate((protein_concentrations, sol.y[8,:]))

            # store the solution after dark period: 
            solution_array = np.vstack((solution_array, sol.y.T))
        
        
        # Check if the set point is reached
        if protein_concentration >= set_point:
            if set_point_reached:
                pass
            else:
                #print(f"Set point reached at time {current_time} minutes.")
                set_point_reached = True
        
            
    return time_array, protein_concentrations, solution_array