# -*- coding: utf-8 -*-
import dash
from dash import html, dcc, Input, Output
import plotly.graph_objs as go
import numpy as np
import dash_bootstrap_components as dbc

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

# ---- MathJax (loaded once only) ----
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# ---- LAYOUT ----
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("⚡ Circuit Explorer", className="text-center mb-3", style={"fontSize": "28px"}))
    ]),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Select(
                                id='selected-circuit',
                                options=[
                                    {'label': "Ohm's Law", 'value': 'ohm'},
                                    {'label': "RC Circuit", 'value': 'rc'},
                                    {'label': "Low Pass Filter", 'value': 'lowpass'}
                                ],
                                placeholder="Choose a circuit",
                                className="mb-3"
                            )
                        ], width=6)
                    ])
                ])
            ]),

            html.Div(id='simulation-area', className="mt-3")
        ], width=6)
    ], justify="center"),

    # This hidden div is used only to trigger MathJax re-typesetting
    html.Div(id='mathjax-trigger', style={'display': 'none'})
], fluid=True)

# ---- UI GENERATORS ----

def generate_ohm_ui():
    return dbc.Card([
        dbc.CardBody([
            html.H5("Ohm's Law", style={"fontSize": "20px", "fontWeight": "bold"}),

            # Description
            html.P(
                "Ohm's Law defines the relationship between voltage (V), current (I), and resistance (R) in an electrical circuit. "
                "It states that the voltage across a resistor is directly proportional to the current flowing through it, "
                "with the resistance being the constant of proportionality. This allows calculation of any one quantity if the other two are known.",
                style={"fontSize": "14px"}
            ),

            # Mathematical formula
            html.Div([
                html.B("Key Equation:"),
                html.Div("$$V = I \\times R$$", style={"fontSize": "16px", "marginTop": "5px", "fontFamily": "serif"})
            ], style={"marginBottom": "15px"}),

            # Resistance slider
            dbc.Label("Resistance (Ω)", style={"fontSize": "14px"}),
            dcc.Slider(
                id='resistance',
                min=1,
                max=100,
                step=1,
                value=10,
                marks={1: '1', 25: '25', 50: '50', 75: '75', 100: '100'},
                tooltip={"placement": "bottom", "always_visible": True}
            ),

            # Current slider
            dbc.Label("Current (A)", className="mt-3", style={"fontSize": "14px"}),
            dcc.Slider(
                id='current',
                min=0,
                max=10,
                step=0.1,
                value=1,
                marks={0: '0', 2.5: '2.5', 5: '5', 7.5: '7.5', 10: '10'},
                tooltip={"placement": "bottom", "always_visible": True}
            ),

            # Output
            html.H4(id='voltage-output', className="mt-3 text-info", style={"fontSize": "16px"})
        ])
    ])

def generate_rc_ui():
    return dbc.Card([
        dbc.CardBody([
            html.H5("RC Circuit", style={"fontSize": "20px", "fontWeight": "bold"}),

            # Description
            html.P(
                "An RC circuit consists of a resistor (R) and capacitor (C) in series. "
                "When connected to a voltage source, the capacitor charges and discharges through the resistor, "
                "creating a time-dependent voltage across the capacitor. The rate of charging and discharging "
                "is determined by the time constant τ = R × C.",
                style={"fontSize": "14px"}
            ),

            # Mathematical formulas
            html.Div([
                html.B("Key Equations:"),
                html.Div("1. Capacitor Voltage during Charging: $$V_C(t) = V_s \\left(1 - e^{-t / (R C)}\\right)$$", 
                         style={"fontSize": "16px", "marginTop": "5px", "fontFamily": "serif"}),
                html.Div("2. Capacitor Voltage during Discharging: $$V_C(t) = V_0 e^{-t / (R C)}$$", 
                         style={"fontSize": "16px", "marginTop": "5px", "fontFamily": "serif"}),
                html.Div("3. Time Constant: $$\\tau = R \\times C$$", 
                         style={"fontSize": "16px", "marginTop": "5px", "fontFamily": "serif"})
            ], style={"marginBottom": "15px"}),

            # Resistance slider
            dbc.Label("Resistance (Ω)", style={"fontSize": "14px"}),
            dcc.Slider(
                id='rc_r',
                min=1,
                max=1000,
                step=10,
                value=100,
                marks={1: '1', 250: '250', 500: '500', 750: '750', 1000: '1000'},
                tooltip={"placement": "bottom", "always_visible": True}
            ),

            # Capacitance slider
            dbc.Label("Capacitance (F)", className="mt-3", style={"fontSize": "14px"}),
            dcc.Slider(
                id='rc_c',
                min=0.001,
                max=1,
                step=0.001,
                value=0.01,
                marks={0.001: '0.001', 0.25: '0.25', 0.5: '0.5', 0.75: '0.75', 1: '1'},
                tooltip={"placement": "bottom", "always_visible": True}
            ),

            # Graph output
            dcc.Graph(id='rc-graph')
        ])
    ])

def generate_lowpass_ui():
    return dbc.Card([
        dbc.CardBody([
            html.H5("Low Pass Filter", style={"fontSize": "20px", "fontWeight": "bold"}),

            html.P(
                "Adjustable RC Low-Pass Filter – This RC low-pass filter uses a potentiometer in series with a capacitor to provide a tunable cutoff frequency. By varying the potentiometer resistance, the filter attenuates high-frequency signals above the cutoff while passing lower-frequency components, enabling precise control over signal smoothing or noise reduction.", 
                style={"fontSize": "14px"}
            ),

            # MathJax equations
            html.Div([
                html.B("Key Equations:"),
                html.Div("1. Cutoff Frequency: $$f_c = \\frac{1}{2 \\pi R C}$$", style={"fontSize": "16px"}),
                html.Div("2. Transfer Function: $$H(f) = \\frac{V_{out}}{V_{in}} = \\frac{1}{\\sqrt{1 + (2 \\pi f R C)^2}}$$", style={"fontSize": "16px"}),
                html.Div("3. Phase Shift: $$\\phi(f) = -\\arctan(2 \\pi f R C)$$", style={"fontSize": "16px"})
            ]),

            # Image
            html.Div(
                html.Img(
                    src="/assets/lowpass.png", 
                    style={"width": "100%", "maxWidth": "400px", "marginTop": "10px"}
                ),
                style={"textAlign": "center"}
            ),

            # Sliders
            dbc.Label("Resistance (Ω)", className="mt-3"),
            dcc.Slider(id='lp_r', min=1000, max=100000, step=1000, value=10000,
                       marks={1000: '1k', 50000: '50k', 100000: '100k'}),

            dbc.Label("Capacitance (nF)", className="mt-3"),
            dcc.Slider(id='lp_c', min=1, max=1000, step=1, value=10,
                       marks={1: '1', 500: '500', 1000: '1000'}),

            dcc.Graph(id='lp-graph')
        ])
    ])

# ---- CALLBACKS ----

@app.callback(
    Output('simulation-area', 'children'),
    Input('selected-circuit', 'value')
)
def render_simulation(circuit_type):
    if not circuit_type:
        return dbc.Alert("Select a circuit to begin", color="info")
    
    if circuit_type == 'ohm':
        return generate_ohm_ui()
    if circuit_type == 'rc':
        return generate_rc_ui()
    if circuit_type == 'lowpass':
        return generate_lowpass_ui()

    return dbc.Alert("Unsupported circuit", color="warning")

@app.callback(
    Output('voltage-output', 'children'),
    Input('resistance', 'value'),
    Input('current', 'value'),
    prevent_initial_call=True
)
def update_voltage(R, I):
    return f"Voltage: {R * I:.2f} V"

@app.callback(
    Output('rc-graph', 'figure'),
    Input('rc_r', 'value'),
    Input('rc_c', 'value'),
    prevent_initial_call=True
)
def update_rc_graph(R, C):
    t = np.linspace(0, 5, 100)
    V = 1 * (1 - np.exp(-t / (R * C)))
    fig = go.Figure(go.Scatter(x=t, y=V))
    fig.update_layout(template="plotly_dark", title="RC Charging", xaxis_title="Time (s)", yaxis_title="Voltage (V)")
    return fig

@app.callback(
    Output('lp-graph', 'figure'),
    Input('lp_r', 'value'),
    Input('lp_c', 'value'),
    prevent_initial_call=True
)
def update_lowpass_graph(R, C):
    f = np.linspace(1, 20000, 500)
    omega = 2 * np.pi * f
    H = 1 / np.sqrt(1 + (omega * R * C * 1e-9)**2)
    fig = go.Figure(go.Scatter(x=f, y=H))
    fig.update_layout(template="plotly_dark", title="Low Pass Filter Response", xaxis_title="Frequency (Hz)", yaxis_title="Amplitude", xaxis_type='log')
    return fig

# ---- CLIENTSIDE CALLBACK to trigger MathJax ----
app.clientside_callback(
    """
    function(children) {
        if (window.MathJax) {
            MathJax.typesetPromise();
        }
        return "";
    }
    """,
    Output('mathjax-trigger', 'children'),
    Input('simulation-area', 'children')
)

# ---- RUN ----
if __name__ == "__main__":
    app.run_server(debug=True)