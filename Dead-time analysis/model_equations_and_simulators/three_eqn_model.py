# three_eqn_model.py
import numpy as np
import scipy.integrate as scint

def dydt(t, x, params, input='dark'):
    p = params.valuesdict()
    M, P, C = x

    C_max = p['C_max']
    k_gr = p['k_gr']
    k_tx = p['k_tx']
    d_m = p['d_m']
    k_tl = p['k_tl']
    Kc = p['Kc']
    l0 = p['l0']
    n_gamma = p['n_gamma']
    Ac_green = p['Ac_green']
    Ac_dark = p['Ac_dark']
    Ac_red = p['Ac_red']
    d_p = p['d_p']

    if input.lower() == 'green':
        Ac = Ac_green
    elif input.lower() == 'red':
        Ac = Ac_red
    else:
        Ac = Ac_dark

    k_tx = k_tx * (Ac / (Ac + Kc) + l0)

    f = C / C_max
    y = f * (1 - f)
    y_resources = np.power(y, n_gamma)

    k_tx *= y_resources
    k_tl *= y_resources
    d_dil = k_gr * (1 - f)
    d_m *= (1 - f)
    d_p = d_p * (f**5.5 / (1 + f**5.5))

    dMdt = k_tx - (d_m + d_dil) * M
    dPdt = k_tl * M - (d_p + d_dil) * P
    dCdt = k_gr * C * (1 - f)

    return [dMdt, dPdt, dCdt]

def run_three_eqn_model(x0, time, params, input='dark', output='solve_ivp'):
    p = params.valuesdict()

    #x0 = [p['M_0'], p['P_0'], p['C_0']] 

    sol = scint.solve_ivp(dydt, [time[0], time[-1]], x0, args=(params, input),
                          t_eval=time, method='LSODA')
    if output == 'solve_ivp':
        return sol
    else:
        return sol.y.T
