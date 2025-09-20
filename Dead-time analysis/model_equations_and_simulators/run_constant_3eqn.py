# run_constant.py
import numpy as np
from .three_eqn_model import run_three_eqn_model

def run_constant(total_time, initial_conditions, params, constant_input='green'):
    dt = 1  # Time step in minutes
    time_dark = 1  # Duration of dark interval

    # Initialize storage arrays
    protein_concentrations = [initial_conditions[1]]  # Store folded protein P
    solution_array = np.array([initial_conditions])  # Full solution state
    time_array = [0]  # Time tracking

    # Initialize system state and time
    state = initial_conditions
    current_time = 0

    # Run the simulation loop until total_time is reached
    while current_time < total_time:
        # Define input durations based on constant input
        if constant_input.lower() == 'green':
            time_green, time_red = 8, 0
        elif constant_input.lower() == 'red':
            time_green, time_red = 0, 8
        else:
            time_green, time_red, time_dark = 0, 0, 5

        # Repeat a full green-red-dark-dark cycle twice per outer loop iteration
        for _ in range(2):
            # Simulate dark interval
            t_dark = np.linspace(current_time, current_time + time_dark, int(time_dark/dt) + 100)
            sol = run_three_eqn_model(state, t_dark, params, input='dark')
            state = sol.y[:, -1]
            current_time += time_dark
            time_array = np.concatenate((time_array, sol.t))
            protein_concentrations = np.concatenate((protein_concentrations, sol.y[1, :]))
            solution_array = np.vstack((solution_array, sol.y.T))

            # Simulate green interval if applicable
            if time_green > 0:
                t_green = np.linspace(current_time, current_time + time_green, int(time_green/dt) + 100)
                sol = run_three_eqn_model(state, t_green, params, input='green')
                state = sol.y[:, -1]
                current_time += time_green
                time_array = np.concatenate((time_array, sol.t))
                protein_concentrations = np.concatenate((protein_concentrations, sol.y[1, :]))
                solution_array = np.vstack((solution_array, sol.y.T))

            # Simulate red interval if applicable
            if time_red > 0:
                t_red = np.linspace(current_time, current_time + time_red, int(time_red/dt) + 100)
                sol = run_three_eqn_model(state, t_red, params, input='red')
                state = sol.y[:, -1]
                current_time += time_red
                time_array = np.concatenate((time_array, sol.t))
                protein_concentrations = np.concatenate((protein_concentrations, sol.y[1, :]))
                solution_array = np.vstack((solution_array, sol.y.T))

            # Simulate another dark interval
            t_dark = np.linspace(current_time, current_time + time_dark, int(time_dark/dt) + 100)
            sol = run_three_eqn_model(state, t_dark, params, input='dark')
            state = sol.y[:, -1]
            current_time += time_dark
            time_array = np.concatenate((time_array, sol.t))
            protein_concentrations = np.concatenate((protein_concentrations, sol.y[1, :]))
            solution_array = np.vstack((solution_array, sol.y.T))

    # Return timepoints, protein levels, and full state solution
    return time_array, protein_concentrations, solution_array
