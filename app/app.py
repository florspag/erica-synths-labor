# -*- coding: utf-8 -*-
import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
from enum import StrEnum
import plotly.graph_objs as go
import numpy as np

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

class CircuitType(StrEnum):
    LOWPASS = 'lowpass'
    OHM = "ohm"
    RC = 'rc'
    SQUARE = 'square'
    VCA = "vca"


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
                                    {'label': "Ohm's Law", 'value': CircuitType.OHM},
                                    {'label': "RC Circuit", 'value': CircuitType.RC},
                                    {'label': "Low Pass Filter", 'value': CircuitType.LOWPASS},
                                    {'label': "Square Wave Generator", 'value': CircuitType.SQUARE},
                                    {'label': "Crude VCA", 'value': CircuitType.VCA}
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

def generate_square_ui():
    return dbc.Card([
        dbc.CardBody([
            html.H5("Square Wave Generator (CD40106 Schmitt Trigger)", 
                    style={"fontSize": "20px", "fontWeight": "bold"}),

            # Description
            html.P(
                "This oscillator uses a CD40106 Schmitt trigger inverter with an RC feedback network. "
                "The capacitor charges and discharges exponentially between two threshold voltages "
                "(V_T+ and V_T-). When these thresholds are reached, the inverter switches state, "
                "producing a stable square wave. The hysteresis of the Schmitt trigger ensures clean "
                "transitions and noise immunity.",
                style={"fontSize": "14px"}
            ),

            # Equations
            html.Div([
                html.B("Key Equations:"),

                html.Div(
                    "1. Period: $$T = RC \\cdot \\ln\\left(\\frac{V_{T+}(V_{cc}-V_{T-})}{V_{T-}(V_{cc}-V_{T+})}\\right)$$",
                    style={"fontSize": "16px", "marginTop": "5px", "fontFamily": "serif"}
                ),

                html.Div(
                    "2. Frequency: $$f = \\frac{1}{T}$$",
                    style={"fontSize": "16px", "marginTop": "5px", "fontFamily": "serif"}
                ),

                html.Div(
                    "3. Capacitor Voltage: $$V_C(t) = V_{final} + (V_{initial} - V_{final}) e^{-t/(RC)}$$",
                    style={"fontSize": "16px", "marginTop": "5px", "fontFamily": "serif"}
                )
            ], style={"marginBottom": "15px"}),

            # Resistance slider
            dbc.Label("Resistance (Ω)", style={"fontSize": "14px"}),
            dcc.Slider(
                id='sq_r',
                min=1000,
                max=1000000,
                step=1000,
                value=10000,
                marks={1000: '1k', 100000: '100k', 1000000: '1M'},
                tooltip={"placement": "bottom", "always_visible": True}
            ),

            # Capacitance slider
            dbc.Label("Capacitance (nF)", className="mt-3", style={"fontSize": "14px"}),
            dcc.Slider(
                id='sq_c',
                min=1,
                max=1000,
                step=1,
                value=100,
                marks={1: '1', 100: '100', 1000: '1000'},
                tooltip={"placement": "bottom", "always_visible": True}
            ),
            
            # VCC slider
            dbc.Label("Supply Voltage Vcc (V)", className="mt-3"),
            dcc.Slider(
                id='sq_vcc',
                min=3,
                max=15,
                step=0.5,
                value=5,
                marks={3: '3V', 5: '5V', 10: '10V', 15: '15V'},
                tooltip={"placement": "bottom", "always_visible": True}
            ),

            # Upper threshold
            dbc.Label("Upper Threshold Vt+ (ratio of Vcc)", className="mt-3"),
            dcc.Slider(
                id='sq_vtp',
                min=0.5,
                max=0.9,
                step=0.01,
                value=0.7,
                marks={0.5: '0.5', 0.7: '0.7', 0.9: '0.9'},
                tooltip={"placement": "bottom", "always_visible": True}
            ),

            # Lower threshold
            dbc.Label("Lower Threshold Vt- (ratio of Vcc)", className="mt-3"),
            dcc.Slider(
                id='sq_vtm',
                min=0.1,
                max=0.5,
                step=0.01,
                value=0.3,
                marks={0.1: '0.1', 0.3: '0.3', 0.5: '0.5'},
                tooltip={"placement": "bottom", "always_visible": True}
            ),
            # Graph
            dcc.Graph(
                id='sq-graph',
                style={"height": "350px", "marginTop": "20px"}
            )
        ])
    ], style={"margin": "20px"})

def generate_vca_ui():
    return dbc.Card([
        dbc.CardBody([

            html.H5(
                "Crude VCA / Collector Diode RC System",
                style={"fontSize": "20px", "fontWeight": "bold"}
            ),

            html.P(
                "Nonlinear analog system based on a BJT current source feeding a series diode "
                "and RC load. The transistor generates a nonlinear collector current, the diode "
                "acts as a one-way transfer element, and the RC network integrates the output.",
                style={"fontSize": "14px"}
            ),

            # =========================
            # EQUATIONS
            # =========================
            html.Div([
                html.B("Key Equations:"),

                dcc.Markdown(r"""
            Input signal
            $$
            V_{in}(t) = A \sin(2\pi f t)
            $$

            Base voltage
            $$
            V_B(t) = V_{bias} + V_{in}(t)
            $$

            Transistor collector current (Ebers–Moll model)
            $$
            I_C(t) = I_S \exp\left(\frac{V_{BE}(t)}{V_T}\right)
            $$

            Collector voltage
            $$
            V_C(t) = V_{CC} - R_C \cdot I_C(t)
            $$

            Series diode transfer condition
            $$
            V_{after}(t) =
            \begin{cases}
            V_C(t) - V_D & \text{if } V_C(t) > V_{out}(t) + V_D \\
            V_{out}(t) & \text{otherwise}
            \end{cases}
            $$

            RC output dynamics
            $$
            \frac{dV_{out}(t)}{dt} = \frac{1}{\tau} \left(V_{after}(t) - V_{out}(t)\right)
            $$

            Time constant
            $$
            \tau = R C
            $$
            """, mathjax=True)

            ], style={"margin": "20px"}),

            html.Div([
                html.B("Crude VCA / Collector Diode Topology"),

                html.Pre(
            """                                     Vcc
                                    │
                                    Rc
                                    │
                                    ●────────────── Vout
                                    │
                                    |>|   Diode
                                    │
                                Collector (C)
                                    │
                                    |\\
            Vin ──||───────┬───────| >──── Base (B)
                Cin       │         |/
                          │         │
                        Rbias      Emitter
                          │          │
                         Vbias      GND
                          │
                         GND

            CONTROL:
            Vcontrol ─── Rctrl ─── Cenv ─── GND
            """,
                    style={
                        "backgroundColor": "#0b0b0b",
                        "color": "#00ff88",
                        "padding": "14px",
                        "borderRadius": "8px",
                        "fontSize": "13px",
                        "lineHeight": "1.25",
                        "overflowX": "auto",
                        "border": "1px solid #1f1f1f"
                    }
                )
            ], style={"marginTop": "15px"}),

            # =========================
            # SLIDERS
            # =========================

            dbc.Label("Input Amplitude"),
            dcc.Slider(
                id='vca_amp',
                min=0.1, max=5, step=0.1, value=1,
                marks={0.1: "0.1", 2: "2", 5: "5"}
            ),

            dbc.Label("Input Frequency (Hz)", className="mt-3"),
            dcc.Slider(
                id='vca_freq',
                min=1, max=500, step=1, value=50,
                marks={1: "1", 250: "250", 500: "500"}
            ),

            dbc.Label("Control Voltage (Envelope Source)", className="mt-3"),
            dcc.Slider(
                id='vca_ctrl',
                min=0, max=5, step=0.1, value=2.5,
                marks={0: "0", 2.5: "2.5", 5: "5"}
            ),

            dbc.Label("Time Constant τ (RC Envelope)", className="mt-3"),
            dcc.Slider(
                id='vca_tau',
                min=0.001, max=0.1, step=0.001, value=0.02,
                marks={0.001: "1ms", 0.05: "50ms", 0.1: "100ms"}
            ),

            dbc.Label("Base Bias (V)", className="mt-3"),
            dcc.Slider(
                id='vca_bias',
                min=0, max=1.5, step=0.01, value=0.7,
                marks={0: "0", 0.7: "0.7", 1.5: "1.5"}
            ),

            # =========================
            # OUTPUT
            # =========================
            dcc.Graph(
                id='vca-graph',
                style={"height": "420px", "marginTop": "20px"}
            )
        ])
    ], style={"padding": "10px"})


# ---- CALLBACKS ----

@app.callback(
    Output('simulation-area', 'children'),
    Input('selected-circuit', 'value')
)
def render_simulation(circuit_type):
    match circuit_type: 
        case CircuitType.OHM:
            return generate_ohm_ui()
        case CircuitType.RC:
            return generate_rc_ui()
        case CircuitType.LOWPASS:
            return generate_lowpass_ui()
        case CircuitType.SQUARE:
            return generate_square_ui()
        case CircuitType.VCA:
            return generate_vca_ui()
        case _:
            return dbc.Alert("Select a circuit to begin", color="info")

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

@app.callback(
    Output('sq-graph', 'figure'),
    Input('sq_r', 'value'),
    Input('sq_c', 'value'),
    Input('sq_vcc', 'value'),
    Input('sq_vtp', 'value'),
    Input('sq_vtm', 'value'),
    prevent_initial_call=True
)
def update_40106_wave(R, C, Vcc, vtp_ratio, vtm_ratio):

    C = C * 1e-9  # nF → F

    # Convert ratios → actual voltages
    Vt_plus = vtp_ratio * Vcc
    Vt_minus = vtm_ratio * Vcc

    # Safety check
    if Vt_minus >= Vt_plus:
        return go.Figure().update_layout(
            template="plotly_dark",
            title="Error: Vt- must be lower than Vt+"
        )

    # Exact period
    T = R * C * np.log(
        (Vt_plus * (Vcc - Vt_minus)) /
        (Vt_minus * (Vcc - Vt_plus))
    )

    f = 1 / T if T > 0 else 0

    t = np.linspace(0, 5*T, 2000)

    vc = np.zeros_like(t)
    vout = np.zeros_like(t)

    vc_current = Vt_minus
    state_high = True
    last_switch_time = 0

    for i, time in enumerate(t):
        dt = time - last_switch_time

        if state_high:
            vc_current = Vcc - (Vcc - vc_current) * np.exp(-dt / (R * C))
            vout[i] = Vcc

            if vc_current >= Vt_plus:
                state_high = False
                last_switch_time = time
        else:
            vc_current = vc_current * np.exp(-dt / (R * C))
            vout[i] = 0

            if vc_current <= Vt_minus:
                state_high = True
                last_switch_time = time

        vc[i] = vc_current

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=t, y=vout, mode='lines', name='Output'))
    fig.add_trace(go.Scatter(x=t, y=vc, mode='lines', name='Capacitor Voltage'))

    # Threshold lines
    fig.add_hline(y=Vt_plus, line_dash="dot", annotation_text="Vt+")
    fig.add_hline(y=Vt_minus, line_dash="dot", annotation_text="Vt-")

    fig.update_layout(
        template="plotly_dark",
        title=f"f ≈ {f:.1f} Hz | Vcc={Vcc}V | Vt+={Vt_plus:.2f}V | Vt-={Vt_minus:.2f}V",
        xaxis_title="Time (s)",
        yaxis_title="Voltage (V)"
    )

    return fig

@app.callback(
    Output('vca-graph', 'figure'),
    Input('vca_amp', 'value'),
    Input('vca_freq', 'value'),
    Input('vca_ctrl', 'value'),
    Input('vca_tau', 'value'),
    Input('vca_bias', 'value'),
    prevent_initial_call=True
)
def update_vca(amp, freq, vctrl, tau, bias):

    import numpy as np
    import plotly.graph_objs as go

    # =========================
    # CONSTANTS
    # =========================
    Vcc = 5
    Rc = 1000
    Vd = 0.7
    Is = 1e-12
    Vt = 0.026

    # =========================
    # TIME VECTOR
    # =========================
    t = np.linspace(0, 0.1, 2000)
    dt = t[1] - t[0]

    # =========================
    # INPUT SIGNAL
    # =========================
    vin = amp * np.sin(2 * np.pi * freq * t)

    # =========================
    # CONTROL ENVELOPE (RC)
    # =========================
    venv = np.zeros_like(t)

    for i in range(1, len(t)):
        if vctrl > venv[i-1]:
            venv[i] = venv[i-1] + (vctrl - venv[i-1]) / tau * dt
        else:
            venv[i] = venv[i-1] - venv[i-1] / tau * dt

    # =========================
    # TRANSISTOR STAGE
    # =========================
    vb = bias + vin

    Ic = Is * np.exp(np.clip(vb / Vt, -40, 40))

    vc = Vcc - Rc * Ic
    vc = np.clip(vc, 0, Vcc)

    # =========================
    # SERIES DIODE STAGE
    # =========================
    v_after = np.zeros_like(t)

    for i in range(len(t)):

        prev = v_after[i-1] if i > 0 else 0

        # diode conduction condition
        if vc[i] > prev + Vd:
            v_after[i] = vc[i] - Vd
        else:
            v_after[i] = prev

    # =========================
    # RC OUTPUT FILTER
    # =========================
    vout = np.zeros_like(t)

    for i in range(1, len(t)):
        vout[i] = vout[i-1] + (v_after[i] - vout[i-1]) / tau * dt

    # =========================
    # PLOT
    # =========================
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=t, y=vin, name="Vin", opacity=0.6))
    fig.add_trace(go.Scatter(x=t, y=vc, name="Collector"))
    fig.add_trace(go.Scatter(x=t, y=v_after, name="After Diode"))
    fig.add_trace(go.Scatter(x=t, y=vout, name="Vout", line=dict(width=3)))
    fig.add_trace(go.Scatter(x=t, y=venv, name="Envelope", opacity=0.7))

    fig.update_layout(
        template="plotly_dark",
        title="Collector → Diode → RC Crude VCA (Single Topology)",
        xaxis_title="Time (s)",
        yaxis_title="Voltage (V)",
        legend=dict(orientation="h")
    )

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