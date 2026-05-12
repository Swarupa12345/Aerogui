from scipy.optimize import differential_evolution
from predictor import aerodynamic_prediction


def objective_function(x, constraints=None):
    params = {
        'nose_len': x[0],
        'body_len': x[1],
        'wing_le': x[2],
        'root_chord': x[3],
        'tip_chord': x[4],
        'semi_span': x[5],
        'root_th': x[6],
        'tip_th': x[7],
        'wing_sweep': x[8],
        'tail_le': x[9],
        'root_chord1': x[10],
        'tip_chord1': x[11],
        'semi_span1': x[12],
        'root_th1': x[13],
        'tip_th1': x[14],
        'mach': x[15],
        'alpha': x[16],
        'alt': x[17]
    }

    result = aerodynamic_prediction(params)

    cl = result['CL']
    cd = max(result['CD'], 1e-6)
    xcp = result['XCP']

    lift_to_drag = cl / cd
    penalty = 0

    if constraints:
        if not (constraints['CL'][0] <= cl <= constraints['CL'][1]):
            penalty += 100
        if not (constraints['CD'][0] <= cd <= constraints['CD'][1]):
            penalty += 100
        if not (constraints['XCP'][0] <= xcp <= constraints['XCP'][1]):
            penalty += 100

    return -(lift_to_drag) + penalty


def run_optimization(bounds, maxiter=50, popsize=15, constraints=None):
    result = differential_evolution(
        lambda x: objective_function(x, constraints),
        bounds=bounds,
        maxiter=maxiter,
        popsize=popsize,
        polish=True,
        disp=True,
        updating='deferred'
    )

    return result