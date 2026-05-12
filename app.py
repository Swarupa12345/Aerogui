# Fully Integrated Professional ML-GUI Aerospace Optimization Platform (`app.py`)
import PySimpleGUI as sg
import time

from predictor import aerodynamic_prediction
from optimizer import run_optimization
from envelope import alpha_sweep, mach_sweep, altitude_sweep

# =========================================================
# PROFESSIONAL THEME SETTINGS
# =========================================================
sg.theme('DarkTeal9')

FONT_MAIN = ('Segoe UI', 10)
FONT_TITLE = ('Segoe UI', 16, 'bold')
FONT_HEADER = ('Segoe UI', 11, 'bold')
BUTTON_SIZE = (14, 1)
INPUT_SIZE = (10, 1)
TAB_FONT = ('Segoe UI', 10, 'bold')

# =========================================================
# BUTTON STYLE FUNCTION
# =========================================================
def styled_button(text, color):
    return sg.Button(
        text,
        size=BUTTON_SIZE,
        button_color=('white', color),
        font=FONT_HEADER
    )

# =========================================================
# INPUT PARAMETERS
# =========================================================
def input_row(label, key):
    return [
        sg.Text(label, size=(18, 1), font=FONT_MAIN),
        sg.Input(key=key, size=INPUT_SIZE, font=FONT_MAIN)
    ]

input_layout = [
    input_row('Nose Length', 'nose_len'),
    input_row('Body Length', 'body_len'),
    input_row('Wing LE', 'wing_le'),
    input_row('Root Chord', 'root_chord'),
    input_row('Tip Chord', 'tip_chord'),
    input_row('Semi Span', 'semi_span'),
    input_row('Root Thickness', 'root_th'),
    input_row('Tip Thickness', 'tip_th'),
    input_row('Wing Sweep', 'wing_sweep'),
    input_row('Tail LE', 'tail_le'),
    input_row('Root Chord 1', 'root_chord1'),
    input_row('Tip Chord 1', 'tip_chord1'),
    input_row('Semi Span 1', 'semi_span1'),
    input_row('Root Thickness 1', 'root_th1'),
    input_row('Tip Thickness 1', 'tip_th1'),
    input_row('Mach', 'mach'),
    input_row('Alpha', 'alpha'),
    input_row('Altitude', 'alt')
]

# =========================================================
# TAB 1 : SIMPLE PREDICTION
# =========================================================
prediction_tab = [[
    sg.Column(
        input_layout,
        scrollable=True,
        vertical_scroll_only=True,
        size=(340, 500)
    ),
    sg.VSeparator(),
    sg.Column([
        [sg.Text('Predicted Outputs', font=FONT_HEADER)],
        [sg.HorizontalSeparator()],
        [sg.Text('CL :', size=(15, 1)), sg.Text('', key='cl_out', size=(25, 1), font=FONT_HEADER)],
        [sg.Text('CD :', size=(15, 1)), sg.Text('', key='cd_out', size=(25, 1), font=FONT_HEADER)],
        [sg.Text('XCP :', size=(15, 1)), sg.Text('', key='xcp_out', size=(25, 1), font=FONT_HEADER)],
        [sg.HorizontalSeparator()],
        [
            styled_button('Estimate', '#007ACC'),
            styled_button('Clear', '#555555'),
            styled_button('Exit', '#8B0000')
        ]
    ], size=(500, 500))
]]

# =========================================================
# TAB 2 : OPTIMIZATION
# =========================================================
def bound_row(label, low_key, high_key, low, high):
    return [
        sg.Text(label, size=(18, 1)),
        sg.Input(low, key=low_key, size=(8, 1)),
        sg.Input(high, key=high_key, size=(8, 1))
    ]

optimization_tab = [
    [sg.Text('Optimization Design Variables', font=FONT_HEADER)],
    [sg.Text('Parameter', size=(18, 1)), sg.Text('Lower', size=(10, 1)), sg.Text('Upper', size=(10, 1))],

    bound_row('Nose Length', 'nose_lower', 'nose_upper', '1', '10'),
    bound_row('Body Length', 'body_lower', 'body_upper', '5', '30'),
    bound_row('Wing LE', 'wingle_lower', 'wingle_upper', '1', '10'),
    bound_row('Root Chord', 'root_lower', 'root_upper', '1', '10'),
    bound_row('Tip Chord', 'tip_lower', 'tip_upper', '1', '10'),
    bound_row('Semi Span', 'span_lower', 'span_upper', '1', '20'),
    bound_row('Root Thickness', 'rootth_lower', 'rootth_upper', '0.1', '1'),
    bound_row('Tip Thickness', 'tipth_lower', 'tipth_upper', '0.1', '1'),
    bound_row('Wing Sweep', 'sweep_lower', 'sweep_upper', '10', '60'),
    bound_row('Tail LE', 'tail_lower', 'tail_upper', '1', '10'),
    bound_row('Root Chord 1', 'root1_lower', 'root1_upper', '1', '10'),
    bound_row('Tip Chord 1', 'tip1_lower', 'tip1_upper', '1', '10'),
    bound_row('Semi Span 1', 'span1_lower', 'span1_upper', '1', '20'),
    bound_row('Root Thickness 1', 'rootth1_lower', 'rootth1_upper', '0.1', '1'),
    bound_row('Tip Thickness 1', 'tipth1_lower', 'tipth1_upper', '0.1', '1'),
    bound_row('Mach', 'mach_lower', 'mach_upper', '0.5', '5'),
    bound_row('Alpha', 'alpha_lower', 'alpha_upper', '0', '15'),
    bound_row('Altitude', 'alt_lower', 'alt_upper', '0', '30000'),

    [sg.HorizontalSeparator()],
    [sg.Text('Optimization Settings', font=FONT_HEADER)],
    [sg.Text('Population Size'), sg.Input('10', key='popsize', size=(8, 1))],
    [sg.Text('Max Iterations'), sg.Input('20', key='maxiter', size=(8, 1))],

    [
        styled_button('Run Optimization', '#2E8B57'),
        styled_button('Clear Optimization', '#555555')
    ],

    [sg.Multiline(size=(85, 18), key='opt_output', autoscroll=True)]
]

# =========================================================
# TAB 3 : FLIGHT ENVELOPE
# =========================================================
flight_tab = [
    [sg.Text('Alpha Sweep', font=FONT_HEADER)],
    [
        sg.Text('Min'), sg.Input('0', key='alpha_min', size=(5, 1)),
        sg.Text('Max'), sg.Input('10', key='alpha_max', size=(5, 1)),
        sg.Text('Step'), sg.Input('1', key='alpha_step', size=(5, 1))
    ],

    [sg.HorizontalSeparator()],

    [sg.Text('Mach Sweep', font=FONT_HEADER)],
    [
        sg.Text('Min'), sg.Input('0.5', key='mach_min', size=(5, 1)),
        sg.Text('Max'), sg.Input('3', key='mach_max', size=(5, 1)),
        sg.Text('Step'), sg.Input('0.5', key='mach_step', size=(5, 1))
    ],

    [sg.HorizontalSeparator()],

    [
        styled_button('Run Flight Envelope Analysis', '#CC6600'),
        styled_button('Clear Analysis', '#555555')
    ],

    [sg.Multiline(size=(85, 20), key='flight_output', autoscroll=True)]
]

# =========================================================
# MAIN LAYOUT
# =========================================================
layout = [
    [
        sg.Text(
            'AI-Based Aerodynamic Configuration Optimization Platform',
            font=FONT_TITLE,
            expand_x=True,
            justification='center',
            text_color='white'
        )
    ],

    [
        sg.TabGroup([
            [
                sg.Tab('Simple Prediction', prediction_tab, font=TAB_FONT),
                sg.Tab('Optimization', optimization_tab, font=TAB_FONT),
                sg.Tab('Flight Envelope', flight_tab, font=TAB_FONT)
            ]
        ],
        tab_background_color='#1E2A38',
        selected_title_color='white',
        selected_background_color='#007ACC',
        title_color='lightgray')
    ]
]

# =========================================================
# WINDOW
# =========================================================
window = sg.Window(
    'Aerospace Design GUI',
    layout,
    size=(1100, 750),
    resizable=True,
    finalize=True,
    background_color='#0B1726'
)

# =========================================================
# EVENT LOOP
# =========================================================
while True:
    event, values = window.read()

    if event in (sg.WINDOW_CLOSED, 'Exit'):
        break

    # CLEAR INPUTS
    if event == 'Clear':
        for key in values:
            try:
                window[key].update('')
            except:
                pass

    # SIMPLE PREDICTION
    if event == 'Estimate':
        try:
            result = aerodynamic_prediction(values)
            window['cl_out'].update(result['CL'])
            window['cd_out'].update(result['CD'])
            window['xcp_out'].update(result['XCP'])
        except Exception as e:
            sg.popup_error(str(e))

    # OPTIMIZATION
    if event == 'Run Optimization':
        try:
            start = time.time()

            bounds = [
                (float(values['nose_lower']), float(values['nose_upper'])),
                (float(values['body_lower']), float(values['body_upper'])),
                (float(values['wingle_lower']), float(values['wingle_upper'])),
                (float(values['root_lower']), float(values['root_upper'])),
                (float(values['tip_lower']), float(values['tip_upper'])),
                (float(values['span_lower']), float(values['span_upper'])),
                (float(values['rootth_lower']), float(values['rootth_upper'])),
                (float(values['tipth_lower']), float(values['tipth_upper'])),
                (float(values['sweep_lower']), float(values['sweep_upper'])),
                (float(values['tail_lower']), float(values['tail_upper'])),
                (float(values['root1_lower']), float(values['root1_upper'])),
                (float(values['tip1_lower']), float(values['tip1_upper'])),
                (float(values['span1_lower']), float(values['span1_upper'])),
                (float(values['rootth1_lower']), float(values['rootth1_upper'])),
                (float(values['tipth1_lower']), float(values['tipth1_upper'])),
                (float(values['mach_lower']), float(values['mach_upper'])),
                (float(values['alpha_lower']), float(values['alpha_upper'])),
                (float(values['alt_lower']), float(values['alt_upper']))
            ]

            result = run_optimization(
                bounds,
                int(values['maxiter']),
                int(values['popsize'])
            )

            elapsed = time.time() - start

            output = (
                f'Optimization Completed\n\n'
                f'Best CL/CD = {-result.fun:.6f}\n'
                f'Time Taken = {elapsed:.2f} seconds\n\n'
                f'Best Parameters:\n{result.x}'
            )

            window['opt_output'].update(output)

        except Exception as e:
            sg.popup_error(str(e))

    # FLIGHT ENVELOPE
    if event == 'Run Flight Envelope Analysis':
        try:
            params = values.copy()

            alpha_results = alpha_sweep(
                params,
                float(values['alpha_min']),
                float(values['alpha_max']),
                float(values['alpha_step'])
            )

            mach_results = mach_sweep(
                params,
                float(values['mach_min']),
                float(values['mach_max']),
                float(values['mach_step'])
            )

            final_text = 'ALPHA SWEEP RESULTS\n\n'
            for r in alpha_results:
                final_text += r + '\n'

            final_text += '\nMACH SWEEP RESULTS\n\n'
            for r in mach_results:
                final_text += r + '\n'

            window['flight_output'].update(final_text)

        except Exception as e:
            sg.popup_error(str(e))

window.close()
