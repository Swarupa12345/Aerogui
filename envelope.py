from predictor import aerodynamic_prediction
import numpy as np


def alpha_sweep(base_params, alpha_min, alpha_max, step):
    results = []

    for alpha in np.arange(alpha_min, alpha_max + step, step):
        params = base_params.copy()
        params['alpha'] = alpha
        result = aerodynamic_prediction(params)
        result['alpha'] = alpha
        results.append(result)

    return results


def mach_sweep(base_params, mach_min, mach_max, step):
    results = []

    for mach in np.arange(mach_min, mach_max + step, step):
        params = base_params.copy()
        params['mach'] = mach
        result = aerodynamic_prediction(params)
        result['mach'] = mach
        results.append(result)

    return results


def altitude_sweep(base_params, alt_min, alt_max, step):
    results = []

    for alt in np.arange(alt_min, alt_max + step, step):
        params = base_params.copy()
        params['alt'] = alt
        result = aerodynamic_prediction(params)
        result['alt'] = alt
        results.append(result)

    return results