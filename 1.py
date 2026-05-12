# Fully Integrated Professional PySimpleGUI Aerospace Optimization Platform (`app.py`)

import PySimpleGUI as sg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# Backend imports
from predictor import aerodynamic_prediction
from optimizer import run_optimization
from envelope import alpha_sweep, mach_sweep, altitude_sweep

# =========================================================
# THEME CONFIGURATION
# =========================================================
sg.LOOK_AND_FEEL_TABLE['AERO_PRO'] = {
    'BACKGROUND': '#0B0F14',
    'TEXT': '#C9D1D9',
    'INPUT': '#161B22',
    'TEXT_INPUT': '#FFFFFF',
    'SCROLL': '#1F6FEB',
    'BUTTON': ('white', '#238636'),
    'PROGRESS': ('#58A6FF', '#0D1117'),
    'BORDER': 1,
    'SLIDER_DEPTH': 0,
    'PROGRESS_DEPTH': 0
}
sg.theme('AERO_PRO')

# =========================================================
# SAFE FLOAT PARSER
# =========================================================
def safe_float(values, key, default=0.0):
    try:
        return float(values[key])
    except:
        return default

# =========================================================
# MATPLOTLIB CANVAS DRAWER
# =========================================================
def draw_figure(canvas_elem, figure):
    canvas = canvas_elem.TKCanvas
    for child in canvas.winfo_children():
        child.destroy()
    fig_canvas = FigureCanvasTkAgg(figure, canvas)
    fig_canvas.draw()
    fig_canvas.get_tk_widget().pack(side='top', fill='both', expand=1)
    return fig_canvas

# =========================================================
# DEFAULT PARAMETER BOUNDS
# =========================================================
default_bounds = {
    'nose_len': (1, 10),
    'body_len': (10, 40),
    'wing_le': (1, 10),
    'root_chord': (2, 12),
    'tip_chord': (1, 8),
    'semi_span': (5, 25),
    'root_th': (0.2, 3),
    'tip_th': (0.1, 2),
    'wing_sweep': (0, 70),
    'tail_le': (5, 25),
    'root_chord1': (1, 8),
    'tip_chord1': (1, 6),
    'semi_span1': (2, 12),
    'root_th1': (0.1, 2),
    'tip_th1': (0.1, 2),
    'mach': (0.1, 5),
    'alpha': (-5, 20),
    'alt': (0, 50000)
}

params_list = list(default_bounds.keys())
optimization_history = []

# =========================================================
# SINGLE PREDICTION PANEL
# =========================================================
prediction_inputs = []
for param in params_list:
    low, high = default_bounds[param]
    default = round((low + high) / 2, 2)
    prediction_inputs.append([
        sg.Text(param.replace('_', ' ').title(), size=(16, 1)),
        sg.Input(default, key=param, size=(10, 1))
    ])

single_prediction_panel = sg.Frame("SINGLE PREDICTION", [
    [sg.Text("Aerodynamic Digital Twin Estimation", text_color='cyan')],
    [sg.Column(prediction_inputs, scrollable=True, vertical_scroll_only=True, size=(320, 350))],
    [
        sg.Button("Estimate", size=(10, 1)),
        sg.Button("Clear Prediction", size=(14, 1)),
        sg.Button("Exit", size=(8, 1))
    ],
    [sg.Frame("Predicted Outputs", [
        [sg.Text("CL:"), sg.Text("", key='CL_OUT', size=(15, 1))],
        [sg.Text("CD:"), sg.Text("", key='CD_OUT', size=(15, 1))],
        [sg.Text("XCP:"), sg.Text("", key='XCP_OUT', size=(15, 1))]
    ])],
    [sg.Frame("Error Metrics", [
        [sg.Text("MAE:"), sg.Text("", key='MAE_OUT', size=(15, 1))],
        [sg.Text("RMSE:"), sg.Text("", key='RMSE_OUT', size=(15, 1))],
        [sg.Text("R2:"), sg.Text("", key='R2_OUT', size=(15, 1))]
    ])],
    [sg.Canvas(key='PLOT1', size=(320, 220))]
])

# =========================================================
# OPTIMIZATION PANEL
# =========================================================
bounds_rows = [[sg.Text("Parameter", size=(14,1)), sg.Text("Low", size=(8,1)), sg.Text("High", size=(8,1))]]
for param in params_list:
    low, high = default_bounds[param]
    bounds_rows.append([
        sg.Text(param, size=(14,1)),
        sg.Input(low, key=f'{param}_LOW', size=(8,1)),
        sg.Input(high, key=f'{param}_HIGH', size=(8,1))
    ])

optimization_panel = sg.Frame("OPTIMIZATION", [
    [sg.Text("Differential Evolution Design Exploration", text_color='yellow')],
    [sg.Column(bounds_rows, scrollable=True, vertical_scroll_only=True, size=(380, 250))],

    [sg.Frame("Output Constraints", [
        [
            sg.Frame("CL Limits", [
                [sg.Text("Min"), sg.Input("0", key='CL_MIN', size=(6,1))],
                [sg.Text("Max"), sg.Input("10", key='CL_MAX', size=(6,1))]
            ]),
            sg.Frame("CD Limits", [
                [sg.Text("Min"), sg.Input("0", key='CD_MIN', size=(6,1))],
                [sg.Text("Max"), sg.Input("10", key='CD_MAX', size=(6,1))]
            ]),
            sg.Frame("XCP Limits", [
                [sg.Text("Min"), sg.Input("0", key='XCP_MIN', size=(6,1))],
                [sg.Text("Max"), sg.Input("10", key='XCP_MAX', size=(6,1))]
            ])
        ]
    ])],

    [sg.Frame("Optimization Settings", [
        [sg.Text("Population Size"), sg.Input("10", key='POPSIZE', size=(8,1))],
        [sg.Text("Max Iterations"), sg.Input("20", key='MAXITER', size=(8,1))]
    ])],

    [
        sg.Button("Run Optimization", size=(16,1)),
        sg.Button("Clear Optimization", size=(16,1))
    ],
    [sg.Button("Select & Run", size=(20,1))],

    [sg.Multiline(size=(45, 8), key='OPT_OUTPUT')],
    [sg.Canvas(key='PLOT2', size=(380, 220))]
])

# =========================================================
# FLIGHT ENVELOPE PANEL
# =========================================================
flight_panel = sg.Frame("FLIGHT ENVELOPE", [
    [sg.Text("Optimum Geometry Flight Envelope Analysis", text_color='orange')],

    [sg.Frame("Alpha Sweep", [
        [
            sg.Text("Min"), sg.Input("0", key='ALPHA_MIN', size=(6,1)),
            sg.Text("Max"), sg.Input("10", key='ALPHA_MAX', size=(6,1)),
            sg.Text("Step"), sg.Input("1", key='ALPHA_STEP', size=(6,1))
        ]
    ])],

    [sg.Frame("Mach Sweep", [
        [
            sg.Text("Min"), sg.Input("0.5", key='MACH_MIN', size=(6,1)),
            sg.Text("Max"), sg.Input("5", key='MACH_MAX', size=(6,1)),
            sg.Text("Step"), sg.Input("0.5", key='MACH_STEP', size=(6,1))
        ]
    ])],

    [sg.Frame("Altitude Sweep", [
        [
            sg.Text("Min"), sg.Input("0", key='ALT_MIN', size=(6,1)),
            sg.Text("Max"), sg.Input("50000", key='ALT_MAX', size=(6,1)),
            sg.Text("Step"), sg.Input("5000", key='ALT_STEP', size=(6,1))
        ]
    ])],

    [
        sg.Button("Run Flight Envelope Analysis", size=(24,1)),
        sg.Button("Clear Analysis", size=(14,1))
    ],

    [sg.Multiline(size=(48, 10), key='FLIGHT_OUTPUT')],
    [sg.Text("Analysis Summary")],
    [sg.Multiline(size=(48, 5), key='SUMMARY_OUTPUT')],
    [sg.Canvas(key='PLOT3', size=(400, 240))]
])

# =========================================================
# MAIN LAYOUT
# =========================================================
layout = [
    [sg.Text(
        "OPTIMIZATION AERODYNAMIC CONFIGURATION DESIGN OF AEROSPACE VEHICLES",
        font=('Any', 18, 'bold'),
        text_color='#58A6FF',
        justification='center',
        expand_x=True
    )],

    [
        sg.Column([[single_prediction_panel]], vertical_alignment='top'),
        sg.VSeperator(),
        sg.Column([[optimization_panel]], vertical_alignment='top'),
        sg.VSeperator(),
        sg.Column([[flight_panel]], vertical_alignment='top')
    ]
]

# =========================================================
# WINDOW
# =========================================================
window = sg.Window(
    "DRDO Aerospace Optimization Platform",
    layout,
    size=(1800, 950),
    finalize=True,
    resizable=True
)

# =========================================================
# EVENT LOOP
# =========================================================
while True:
    event, values = window.read()

    if event in (sg.WINDOW_CLOSED, 'Exit'):
        break

    if event == 'Estimate':
        params = {p: safe_float(values, p) for p in params_list}

        try:
            result = aerodynamic_prediction(params)

            window['CL_OUT'].update(result.get('CL', 'N/A'))
            window['CD_OUT'].update(result.get('CD', 'N/A'))
            window['XCP_OUT'].update(result.get('XCP', 'N/A'))

            metrics = result.get('metrics', {})
            window['MAE_OUT'].update(metrics.get('MAE', 'N/A'))
            window['RMSE_OUT'].update(metrics.get('RMSE', 'N/A'))
            window['R2_OUT'].update(metrics.get('R2', 'N/A'))

            fig, ax = plt.subplots(figsize=(4,2.5))
            ax.plot(
                ['CL', 'CD', 'XCP'],
                [result.get('CL',0), result.get('CD',0), result.get('XCP',0)],
                marker='o',
                linewidth=2
            )
            ax.set_title("Prediction Response")
            ax.grid(True)
            draw_figure(window['PLOT1'], fig)

        except Exception as e:
            sg.popup_error(f"Prediction Error: {e}")

    if event in ('Run Optimization', 'Select & Run'):
        bounds = [(safe_float(values, f'{p}_LOW'), safe_float(values, f'{p}_HIGH')) for p in params_list]

        constraints = {
            'CL': (safe_float(values, 'CL_MIN'), safe_float(values, 'CL_MAX')),
            'CD': (safe_float(values, 'CD_MIN'), safe_float(values, 'CD_MAX')),
            'XCP': (safe_float(values, 'XCP_MIN'), safe_float(values, 'XCP_MAX'))
        }

        try:
            result = run_optimization(
                bounds,
                maxiter=int(values['MAXITER']),
                popsize=int(values['POPSIZE']),
                constraints=constraints
            )

            optimization_history.append(-result.fun)

            output = f"Optimization Completed\n\nBest Objective: {-result.fun}\n\nBest Parameters:\n{result.x}"
            window['OPT_OUTPUT'].update(output)

            fig, ax = plt.subplots(figsize=(4.5,2.5))
            ax.plot(optimization_history, marker='o', linewidth=2)
            ax.set_title("Optimization Convergence")
            ax.set_xlabel("Run")
            ax.set_ylabel("Objective")
            ax.grid(True)
            draw_figure(window['PLOT2'], fig)

        except Exception as e:
            sg.popup_error(f"Optimization Error: {e}")

    if event == 'Run Flight Envelope Analysis':
        params = {p: safe_float(values, p) for p in params_list}

        try:
            alpha_results = alpha_sweep(
                params,
                safe_float(values, 'ALPHA_MIN'),
                safe_float(values, 'ALPHA_MAX'),
                safe_float(values, 'ALPHA_STEP')
            )

            mach_results = mach_sweep(
                params,
                safe_float(values, 'MACH_MIN'),
                safe_float(values, 'MACH_MAX'),
                safe_float(values, 'MACH_STEP')
            )

            alt_results = altitude_sweep(
                params,
                safe_float(values, 'ALT_MIN'),
                safe_float(values, 'ALT_MAX'),
                safe_float(values, 'ALT_STEP')
            )

            full_output = "ALPHA SWEEP:\n"
            for r in alpha_results:
                full_output += str(r) + "\n"

            full_output += "\nMACH SWEEP:\n"
            for r in mach_results:
                full_output += str(r) + "\n"

            full_output += "\nALTITUDE SWEEP:\n"
            for r in alt_results:
                full_output += str(r) + "\n"

            window['FLIGHT_OUTPUT'].update(full_output)

            summary = (
                f"Alpha Cases: {len(alpha_results)}\n"
                f"Mach Cases: {len(mach_results)}\n"
                f"Altitude Cases: {len(alt_results)}\n"
                f"Total Simulations: {len(alpha_results)+len(mach_results)+len(alt_results)}"
            )
            window['SUMMARY_OUTPUT'].update(summary)

            alpha_vals = [r['alpha'] for r in alpha_results if isinstance(r, dict)]
            cl_vals = [r['CL'] for r in alpha_results if isinstance(r, dict)]

            fig, ax = plt.subplots(figsize=(5,3))
            ax.plot(alpha_vals, cl_vals, marker='o', linewidth=2)
            ax.set_title("CL vs Alpha Envelope")
            ax.set_xlabel("Alpha")
            ax.set_ylabel("CL")
            ax.grid(True)
            draw_figure(window['PLOT3'], fig)

        except Exception as e:
            sg.popup_error(f"Flight Envelope Error: {e}")

    if event == 'Clear Prediction':
        for key in ['CL_OUT','CD_OUT','XCP_OUT','MAE_OUT','RMSE_OUT','R2_OUT']:
            window[key].update('')

    if event == 'Clear Optimization':
        window['OPT_OUTPUT'].update('')

    if event == 'Clear Analysis':
        window['FLIGHT_OUTPUT'].update('')
        window['SUMMARY_OUTPUT'].update('')

window.close()