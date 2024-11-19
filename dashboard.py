import sys
sys.path.append('/home/davide/AI/Projects/apnea')
import os

from dash import Dash, dcc, html, Input, Output, State, callback
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from utils.preprocessing import get_signals, preprocess_events, process_signals_for_plot, process_events_for_plot
from utils.signals import resample_signals
from utils.dashboard import plot_channels
from settings import target_sps, verbose, event_colors, signal_color

sigs = {}
events = {}

def check_dictory(path):
    # Check if path exists
    if os.path.exists(path):
        # Check if the path contains the subdirectories APNEA_EDF and APNEA_RML_clean
        if os.path.exists(os.path.join(path, "APNEA_EDF")) and os.path.exists(os.path.join(path, "APNEA_RML_clean")):
            return 1
        else:
            return 0
    else:
        return -1

def scrape_patients_from_path(path):
    patients = []
    return_value = check_dictory(path)
    if return_value == 1:
        patients_edf = [patient.split(".")[0] for patient in os.listdir(os.path.join(path, "APNEA_EDF"))]
        patients_rml = [patient.split(".")[0] for patient in os.listdir(os.path.join(path, "APNEA_RML_clean"))]
        for patient in patients_edf:
            if patient in patients_rml:
                patients.append(patient)
    return patients

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Input(id='path', type='text', value='/media/davide/T9/super_useful_dataset/downloaded_files/V3', placeholder='Enter path'),
    html.Button(id='submit-button-state', n_clicks=0, children='Submit'),
    html.Div(id='output-state'),
    html.Div(
        id='dropdown-container', 
        children=[
            dcc.Dropdown(id='patient-selection-bar', options=[])
        ],
        style={'display': 'none'}  # Initially hidden
    ),
    html.Output(id = 'patient-loader', children=''),
    html.Div(id = 'graph-container', children=[
            html.Div([
            # Channel checklist
            html.Div([
                html.Label("Channels"),
                dcc.Checklist(
                    id="channel-checklist",
                    options=[{"label": k, "value": k} for k in sigs.keys()],
                    inline=False
                )
            ], style={"width": "40%", "display": "inline-block", "verticalAlign": "top"}),

            # Event checklist
            html.Div([
                html.Label("Events"),
                dcc.Checklist(
                    id="event-checklist",
                    options=[{"label": k, "value": k} for k in events.keys()],
                    inline=False
                )
            ], style={"width": "40%", "display": "inline-block", "marginLeft": "20px", "verticalAlign": "top"}),

        ], style={"display": "flex", "flexDirection": "row"}),
        dcc.Graph(id="channel-plot", config={"scrollZoom": True}),
        # RangeSlider for x-axis selection
        html.Div([
                html.Label("Adjust X-Axis Range"),
                dcc.RangeSlider(
                    id="x-range-slider",
                    min=0,
                    max=0,
                    step=1,
                    value=[0, 0],
                    marks={i: f"{i:.0f}" for i in range(1)},
                    tooltip={"placement": "bottom", "always_visible": False},
                )
            ], style={"display": "inline-block", "verticalAlign": "top"},
            id="x-range-slider-container"
                )
    ], style={"display": "none", "flexDirection": "column"})
])

@callback(
    Output('output-state', 'children'),
    Input('submit-button-state', 'n_clicks'),
    State('path', 'value')
)
def return_output(_, path):
    return_value = check_dictory(path)
    if return_value == 1:
        return f"✅ Path {path} contains APNEA_EDF and APNEA_RML_clean"
    elif return_value == 0:
        return f"⚠️ Path '{path}' doesn't contain APNEA_EDF and APNEA_RML_clean"
    else:
        return f"⚠️ Path '{path}' doesn't exist"

@callback(
    [Output('patient-selection-bar', 'options'),
     Output('dropdown-container', 'style')],
    Input('submit-button-state', 'n_clicks'),
    State('path', 'value')
)
def update_dropdown(_, path):
    return_value = check_dictory(path)
    if return_value == 1:
        patients = scrape_patients_from_path(path)
        options = [{'label': patient, 'value': patient} for patient in patients]
        return options, {'display': 'block'}  # Show dropdown
    else:
        return [], {'display': 'none'}  # Hide dropdown

@callback(
    Output('patient-loader', 'children'),
    Input('patient-selection-bar', 'value'),
    State('path', 'value')
)
def launch_loader(selected_patients, path):
    global sigs, events
    if selected_patients:
        # Get file
        directory_path = os.path.join(path, "APNEA_EDF", selected_patients)
        edf_file_path = os.path.join(directory_path, selected_patients + "[001].edf")
        # Get signals
        signals, sampling_frequencies, signal_labels = get_signals(edf_file_path, verbose = verbose)
        local_sigs = {signal_labels[i]: (signals[i], sampling_frequencies[i]) for i in range(len(signals))}
        resample_sigs_raw = resample_signals(local_sigs, target_sps)
        sigs = process_signals_for_plot(resample_sigs_raw)
        # # Get events
        rml_file_path = os.path.join(path, "APNEA_RML_clean", selected_patients + ".rml")
        events_df = preprocess_events(rml_file_path, verbose = verbose)
        events = process_events_for_plot(events_df)
        return f"Data for {selected_patients} loaded successfully."
    else:
        return ""

@app.callback([Output("channel-checklist", "options"),
                Output("event-checklist", "options"),
                Output("x-range-slider", "min"), Output("x-range-slider", "max"), Output("x-range-slider", "value"),
                Output("graph-container", "style")],
              Input('patient-loader', 'children'))
def update_graph(children):
    if children == '':
        return [""], [""], 0, 0, [0, 0], {"display": "none"}
    else:
        min_time = min([min(sig[0]) for sig in sigs.values()])
        max_time = max([max(sig[0]) for sig in sigs.values()])
        return [key for key in sigs.keys()], [key for key in events.keys()], min_time, max_time, [min_time, max_time], {"display": "block"}

@app.callback(
    [Output("channel-plot", "figure"),
    Output("channel-plot", "style")],
    [Input("channel-checklist", "value"),
     Input("event-checklist", "value"),
     Input("x-range-slider", "value")]
)
def update_plot(selected_channels, selected_events, x_range):
    # Filter signals based on selected channels
    if not selected_channels:
        return plot_channels({}), {'display': 'none'}

    filtered_sigs = {k: sigs[k] for k in selected_channels}

    # Filter events based on selection
    highlighted_events = {k: events[k] for k in selected_events} if selected_events else None
    return plot_channels(filtered_sigs, highlighted_events, x_range=x_range, event_colors = event_colors, signal_color = signal_color), {'display': 'block'}

if __name__ == '__main__':
    app.run(debug=True)
