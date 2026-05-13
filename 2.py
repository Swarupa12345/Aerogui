import PySimpleGUI as sg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from predictor import aerodynamic_prediction, DEFAULT_PARAMS, PARAMETER_ORDER

sg.theme('DarkBlue3')

def draw_figure(canvas_elem, figure):
    canvas = canvas_elem.TKCanvas

    for child in canvas.winfo_children():
        child.destroy()

    fig_canvas = FigureCanvasTkAgg(figure, canvas)
    fig_canvas.draw()
    fig_canvas.get_tk_widget().pack(side='top', fill='both', expand=1)

input_layout = []

for p in PARAMETER_ORDER:
    input_layout.append([
        sg.Text(p, size=(16,1)),
        sg.Input(DEFAULT_PARAMS[p], key=p, size=(10,1))
    ])

layout = [
    [sg.Text('DRDO Aerospace AI Platform', font=('Any',18,'bold'))],

    [
        sg.Column([[sg.Column(input_layout, scrollable=True, size=(320,500))]]),

        sg.VSeperator(),

        sg.Column([
            [sg.Text('Select Model')],

            [sg.Combo(
                ['XGBoost','MLP','Ensemble XGBoost'],
                default_value='XGBoost',
                key='MODEL',
                readonly=True
            )],

            [sg.Button('Run Selected Model'), sg.Button('Exit')],

            [sg.Text('CL:'), sg.Text('', key='CL_OUT')],
            [sg.Text('CD:'), sg.Text('', key='CD_OUT')],
            [sg.Text('XCP:'), sg.Text('', key='XCP_OUT')],

            [sg.Canvas(key='PLOT', size=(700,400))]
        ])
    ]
]

window = sg.Window(
    'DRDO Aerospace Platform',
    layout,
    size=(1200,700),
    finalize=True,
    resizable=True
)

while True:

    event, values = window.read()

    if event in (sg.WINDOW_CLOSED, 'Exit'):
        break

    if event == 'Run Selected Model':

        params = {}

        for p in PARAMETER_ORDER:
            params[p] = float(values[p])

        result = aerodynamic_prediction(
            params,
            values['MODEL']
        )

        window['CL_OUT'].update(result['CL'])
        window['CD_OUT'].update(result['CD'])
        window['XCP_OUT'].update(result['XCP'])

        draw_figure(window['PLOT'], result['figure'])

window.close()
