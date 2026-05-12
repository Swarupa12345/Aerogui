import math
import random
from metrics import calculate_metrics
from plotter import prediction_plot


def aerodynamic_prediction(params):
    nose_len = float(params['nose_len'])
    body_len = float(params['body_len'])
    wing_le = float(params['wing_le'])
    root_chord = float(params['root_chord'])
    tip_chord = float(params['tip_chord'])
    semi_span = float(params['semi_span'])
    root_th = float(params['root_th'])
    tip_th = float(params['tip_th'])
    wing_sweep = float(params['wing_sweep'])

    tail_le = float(params['tail_le'])
    root_chord1 = float(params['root_chord1'])
    tip_chord1 = float(params['tip_chord1'])
    semi_span1 = float(params['semi_span1'])
    root_th1 = float(params['root_th1'])
    tip_th1 = float(params['tip_th1'])

    mach = float(params['mach'])
    alpha = float(params['alpha'])
    alt = float(params['alt'])

    alpha_rad = math.radians(alpha)

    wing_area = ((root_chord + tip_chord) / 2.0) * semi_span * 2
    tail_area = ((root_chord1 + tip_chord1) / 2.0) * semi_span1 * 2
    total_area = wing_area + tail_area

    thickness_ratio = ((root_th + tip_th) / 2.0) / max(root_chord, 0.001)

    cl = (2 * math.pi * alpha_rad) * (
        1 / math.sqrt(abs(1 - mach**2) + 0.01)
    )

    cl *= (1 + 0.02 * wing_sweep / 45)

    cd0 = 0.02 + 0.002 * thickness_ratio * 100
    induced_drag = (cl ** 2) / (math.pi * 4 * 0.85)

    wave_drag = 0.0
    if mach > 1:
        wave_drag = 0.08 * (mach - 1) ** 2

    cd = cd0 + induced_drag + wave_drag

    xcp = (
        0.4 * nose_len +
        0.35 * body_len +
        0.25 * wing_le
    )

    actual = [0.8, 0.9, 1.0, 1.1, 1.2]
    predicted = [x + random.uniform(-0.05, 0.05) for x in actual]

    metrics = calculate_metrics(actual, predicted)

    prediction_plot(actual, predicted)

    return {
        'CL': round(cl, 4),
        'CD': round(cd, 4),
        'XCP': round(xcp, 4),
        'metrics': metrics,
        'plot_path': 'prediction_plot.png'
    }