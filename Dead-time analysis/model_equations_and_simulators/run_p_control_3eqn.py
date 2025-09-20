import numpy as np
from .three_eqn_model import run_three_eqn_model

def p_controller(protein, set_point, gain):
    error = set_point - protein
    time_green = gain * error
    control_interval = 8
    time_green = max(0, min(control_interval, time_green))  # Clamp [0, control_interval]
    time_red = control_interval - time_green
    return time_green, time_red


def run_p_control(total_time, set_point, gain, x0, dead_times, time_steps, params, dead_time_inc = True):
    dt = 1
    time_dark = 1  # minutes
    current_time = 0
    time_array = [0]
    protein_concentrations = [x0[1]]
    state = x0

    input_log = []
    green_time_log = []

    def get_feedback_from_past(theta, t, time_array, signal_array):
        target_time = t - theta
        idx = np.argmin(np.abs(np.array(time_array) - target_time))
        return signal_array[idx]

    def get_dead_time(t):
        if dead_time_inc:
            idx = np.argmin(np.abs(np.array(time_steps) - t))
            return dead_times[idx]
        else:
            return 0

    while current_time < total_time:

        theta = get_dead_time(current_time)

        if current_time > theta:
            feedback = get_feedback_from_past(theta, current_time, time_array, protein_concentrations)
        else:
            feedback = x0[1]

        time_green, time_red = p_controller(feedback, set_point, gain)
        green_time_log.append(time_green)

        for _ in range(2):

            # DARK 1
            t_dark1 = np.linspace(current_time, current_time + time_dark, int(time_dark/dt) + 100)
            sol_d1 = run_three_eqn_model(state, t_dark1, params, input='dark')
            state = sol_d1.y[:, -1]
            current_time += time_dark
            time_array = np.concatenate((time_array, sol_d1.t))
            protein_concentrations = np.concatenate((protein_concentrations, sol_d1.y[1, :]))
            input_log.extend(['dark'] * (len(sol_d1.t) - 1))

            # GREEN
            if time_green > 0:
                t_g = np.linspace(current_time, current_time + time_green, int(time_green/dt) + 100)
                sol_g = run_three_eqn_model(state, t_g, params, input='green')
                state = sol_g.y[:, -1]
                current_time += time_green
                time_array = np.concatenate((time_array, sol_g.t))
                protein_concentrations = np.concatenate((protein_concentrations, sol_g.y[1, :]))
                input_log.extend(['green'] * (len(sol_g.t) - 1))

            # RED
            if time_red > 0:
                t_r = np.linspace(current_time, current_time + time_red, int(time_red/dt) + 100)
                sol_r = run_three_eqn_model(state, t_r, params, input='red')
                state = sol_r.y[:, -1]
                current_time += time_red
                time_array = np.concatenate((time_array, sol_r.t))
                protein_concentrations = np.concatenate((protein_concentrations, sol_r.y[1, :]))
                input_log.extend(['red'] * (len(sol_r.t) - 1))

            # DARK 2
            t_dark2 = np.linspace(current_time, current_time + time_dark, int(time_dark/dt) + 100)
            sol_d2 = run_three_eqn_model(state, t_dark2, params, input='dark')
            state = sol_d2.y[:, -1]
            current_time += time_dark
            time_array = np.concatenate((time_array, sol_d2.t))
            protein_concentrations = np.concatenate((protein_concentrations, sol_d2.y[1, :]))
            input_log.extend(['dark'] * (len(sol_d2.t) - 1))

    return np.array(time_array), np.array(protein_concentrations), set_point, green_time_log