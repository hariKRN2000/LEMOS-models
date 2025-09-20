## Model equations for TCS model

import numpy as np 
import scipy.integrate as scint


def dydt(t, x, params, input = 'dark'):
    
    if input.lower() == 'dark': 
        red, green = (0, 0)

    if input.lower() == 'green': 
        red, green = (0, 1)

    if input.lower() == 'red': 
        red, green = (1, 0)

    # Unpack variables 
    S, Sp, R, Rp, Ac, M, P, Pm = x 

    # Parameters
        
    #p = params.to_dict()
    p = params.valuesdict()


    k_green = p['k_green'] * green # 1/min
    k_red = p['k_red'] * red # 1/min
    b_green = p['b_green'] # 1/min
    b_red = p['b_red'] # 1/min
    k_sp_b = p['k_sp_b'] # 1/min
    k_sp_u = p['k_sp_u'] # 1/min
    k_rp_b = p['k_rp_b'] # 1/min
    k_rp_u = p['k_rp_u'] # 1/min 

    beta = p['beta'] # nM/min 
    l0 = p['l0'] # leak coefficient
    Kc = p['Kc'] # nM
    d_m = p['d_m'] # 1/min 
    k_tl = p['k_tl'] # 1/min 
    d_p = p['d_p'] # 1/min 
    k_fold = p['k_fold'] # 1/min

    n_tcs = p['n_tcs'] # hill coefficient for TCS
    


    # ODEs

    ODEs = []
    dSdt = - (k_green + b_green) * S + (k_red + b_red) * Sp + k_sp_b * Sp * R - k_sp_u * Rp * S
    ODEs.append(dSdt) # Light sensing module 

    dSpdt =  (k_green + b_green) * S - (k_red + b_red) * Sp - k_sp_b * Sp * R + k_sp_u * Rp * S
    ODEs.append(dSpdt) # Transcription output module

    dRdt =  - k_sp_b * Sp * R + k_sp_u * Rp * S
    ODEs.append(dRdt) # Activating complex monomer formation
    
    dRpdt = k_sp_b * Sp * R - k_sp_u * Rp * S - k_rp_b * Rp * Rp + k_rp_u * Ac 
    ODEs.append(dRpdt) # Activating complex monomer formation

    dAcdt = k_rp_b * Rp * Rp - k_rp_u * Ac
    ODEs.append(dAcdt) # Activating complex dimer formation

    dMdt = beta * (Ac**n_tcs / (Kc**n_tcs + Ac**n_tcs) + l0) - d_m * M 
    ODEs.append(dMdt) # Transcription 


    dPdt = k_tl * M - k_fold * P - d_p * P 
    ODEs.append(dPdt) # Translation 

    dPmdt = k_fold * P - d_p * Pm 
    ODEs.append(dPmdt) # Protein folding 


    return ODEs

def run_TCS_model(x0, time, params, input, output = 'solve_ivp'): 

    # sol = scint.odeint(dydt, x0, time, args = (params, input)) # if you want to use odeint
    sol = scint.solve_ivp(dydt, [time[0], time[-1]], x0, args = (params, input), t_eval = time, 
                          method = 'Radau')

    # # # Extract results in odeint format
    if output == 'solve_ivp':
        return sol
    else:
        return sol.y.T
 