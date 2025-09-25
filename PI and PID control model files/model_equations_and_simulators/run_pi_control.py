
# run_pi_control.py
# import required files 

import numpy as np 
from .model_equations import run_TCS_model

# Define the PI controller
def pi_controller(protein, set_point, controller_gain, error_array, time_array, tau_I, integral_error, logic = 1):
    # Proportional term
    error = set_point - protein
    p_term = error
    
    # Integral term
    i_term = (1/tau_I) * integral_error
    
    # Control output (sum of P and I terms)
    time_green = controller_gain * (p_term + i_term) 

    control_interval = 8

    # Clamp the green time to a maximum of 8 minutes
    time_green = min(max(time_green, 0), control_interval)
    time_red = control_interval - time_green

    return time_green, time_red

def pi_controller_explicit_integral_discrete(protein, set_point, controller_gain, error_array, error_time_array, tau_I):
    """
    PI controller that explicitly calculates the integral error using trapezoidal rule
    over the discrete error samples at the end of each 10-min cycle.
    NOTE: There was no difference observed in the dynamics while calculating the integral discretely or as a state variable.
    This implementation is just to show an example of how to discretely estimate the integral of the error.
    """
    # Proportional term
    # error = set_point - protein
    if len(error_array) > 2:
        error = error_array[-1]
    else:
        error = set_point - protein
    p_term = error

    # Compute the explicit integral using trapezoidal rule
    integral_error = 0.0
    if len(error_array) >= 2 and len(error_time_array) >= 2:
        for i in range(1, len(error_array)):
            dt = error_time_array[i] - error_time_array[i-1]
            average_error = 0.5 * (error_array[i] + error_array[i-1])
            integral_error += average_error * dt

    # Integral term
    i_term = (1 / tau_I) * integral_error

    # Control output (sum of P and I terms)
    control_interval = 8
    time_green = controller_gain * (p_term + i_term) 

    # Clamp the green time to a maximum of 8 minutes
    time_green = min(max(time_green, 0), control_interval)
    time_red = control_interval - time_green

    return time_green, time_red

def run_pi_control(total_time, set_point, gain, tau_I, initial_conditions, params):

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
    integral_error_array = [0] # Array to store integrated errors
    error_array = []
    error_time_array = [0]

    # Initial state
    state = initial_conditions
    current_time = 0


    # Run the simulation
    while current_time < total_time:

        
        # Get the current protein concentration
        protein_concentration = state[8]

        integral_error = integral_error_array[-1]

        # #if not set_point_reached:
        ctrl_point = set_point
        # time_green, time_red = pi_controller(protein_concentration, ctrl_point, gain, error_array, 
        #                                      time_array, tau_I, integral_error)
        time_green, time_red = pi_controller_explicit_integral_discrete(
            protein_concentration, set_point, gain, error_array, error_time_array, tau_I)
        
        # Store green light duration
        time_green_values.append(time_green)
        
        # Repeat the green-red cycle twice (two 10-minute cycles)
        for _ in range(2):

            # Simulate Dark Period
            t_dark = np.linspace(current_time, current_time + time_dark, int(time_dark/dt) + 100)
            sol = run_TCS_model(state, t_dark, params, ctrl_point, input = 'dark')
            state = sol.y[:,-1]
            current_time += time_dark
            time_array = np.concatenate((time_array, sol.t))
        
            # Store protein concentration after dark
            protein_concentrations = np.concatenate((protein_concentrations, sol.y[8,:]))

            # store the solution after dark period: 
            solution_array = np.vstack((solution_array, sol.y.T))

            # Store the integral error and error for the current cycle
            integral_error_array = np.concatenate((integral_error_array, sol.y[10, :]))
            #error_array = np.concatenate((error_array, ctrl_point - sol.y[8,:]))

            # Simulate green light period
            if time_green == 0:
                pass
            
            else:
                t_green = np.linspace(current_time, current_time + time_green, int(time_green/dt) + 100)
                #state = odeint(protein_dynamics, state, t_green, args=(1,))[-1]  # Green light (1)
                sol = run_TCS_model(state, t_green, params, ctrl_point,  input = 'green')
                state = sol.y[:,-1]
                current_time += time_green
                # time_array = np.concatenate((time_array, t_green))
                time_array = np.concatenate((time_array, sol.t))
            
                # Store protein concentration after green light
                protein_concentrations = np.concatenate((protein_concentrations, sol.y[8,:]))

                # store the solution after dark period: 
                solution_array = np.vstack((solution_array, sol.y.T))

                # Store the integral error and error for the current cycle
                integral_error_array = np.concatenate((integral_error_array, sol.y[10, :]))
                #error_array = np.concatenate((error_array, ctrl_point - sol.y[8,:]))
            
            # Simulate red light period
            if time_red == 0:
                pass
            
            else:
                t_red = np.linspace(current_time, current_time + time_red, int(time_red/dt) + 100)
                #state = odeint(protein_dynamics, state, t_red, args=(0,))[-1]  # Red light (0)
                sol = run_TCS_model(state, t_red, params, ctrl_point,  input = 'red')
                state = sol.y[:,-1]
                current_time += time_red
                time_array = np.concatenate((time_array, sol.t))
                
                # Store protein concentration after red light
                protein_concentrations = np.concatenate((protein_concentrations, sol.y[8,:]))

                # store the solution after dark period: 
                solution_array = np.vstack((solution_array, sol.y.T))

                # Store the integral error and error for the current cycle
                integral_error_array = np.concatenate((integral_error_array, sol.y[10, :]))
                #error_array = np.concatenate((error_array, ctrl_point - sol.y[8,:]))

            # Simulate Dark Period
            t_dark = np.linspace(current_time, current_time + time_dark, int(time_dark/dt) + 100)
            sol = run_TCS_model(state, t_dark, params, ctrl_point,  input = 'dark')
            state = sol.y[:,-1]
            current_time += time_dark
            time_array = np.concatenate((time_array, sol.t))
        
            # Store protein concentration after dark
            protein_concentrations = np.concatenate((protein_concentrations, sol.y[8,:]))

            # store the solution after dark period: 
            solution_array = np.vstack((solution_array, sol.y.T))

            # Store the integral error and error for the current cycle
            integral_error_array = np.concatenate((integral_error_array, sol.y[10, :]))
            #error_array = np.concatenate((error_array, ctrl_point - sol.y[8,:]))

            error = set_point - sol.y[8,-1]
            error_array.append(error)
            error_time_array.append(current_time)
        
        
        # Check if the set point is reached
        if protein_concentration >= set_point:
            if set_point_reached:
                pass
            else:
                #print(f"Set point reached at time {current_time} minutes.")
                set_point_reached = True
        
            
    return time_array, protein_concentrations, solution_array, time_green_values
