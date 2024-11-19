import sys
sys.path.append('/home/davide/AI/Projects/apnea')

import numpy as np
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
from utils.dashboard import plot_channels
# Target sampling rate
target_sps = 20

# Example signal data (replace with real data)
sigs = {
    "Channel 1": (np.linspace(0, 20 * np.pi, 10000), np.sin(np.linspace(0, 20 * np.pi, 10000))),
    "Channel 2": (np.linspace(0, 20 * np.pi, 10000), np.cos(np.linspace(0, 20 * np.pi, 10000))),
    "Channel 3": (np.linspace(0, 20 * np.pi, 10000), np.random.rand(10000) - 0.5)
}

# Example events
events = {
    "Snoring": {'data': [[0, 10]], 'order' : 0},
    "Apnea": {'data': [[6, 10]], 'order' : 1},
    "Dislexia": {'data': [[10, 40], [20, 35]], 'order' : 2},
}


# Create a Dash app
app = Dash(__name__)

# App layout
app.layout = html.Div([
    html.H1("EDF Signal Viewer"),
    html.Div("Adjust signal visibility or explore individual channels:"),
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
                value=[0, 20 * np.pi],
                marks={i: f"{i:.0f}" for i in range(0, int(20 * np.pi) + 1, 10)},
                tooltip={"placement": "bottom", "always_visible": False},
            )
        ], style={"display": "inline-block", "verticalAlign": "top"},
        id="x-range-slider-container"
            )
    ])


# Callback to update the plot visibility
@app.callback(
    Output("channel-plot", "style"),
    Input("channel-checklist", "value")
)
def update_plot_visibility(selected_channels):
    return {"display": "block" if selected_channels else "none"}
# Callback to update the x-range selection visibility
@app.callback(
    Output("x-range-slider-container", "style"),
    Input("channel-checklist", "value")
)
def update_x_range_visibility(selected_channels):
    return {"display": "block" if selected_channels else "none"}
# Callback to update the plot based on channel, event, and x-range selection
@app.callback(
    Output("channel-plot", "figure"),
    [Input("channel-checklist", "value"),
     Input("event-checklist", "value"),
     Input("x-range-slider", "value")]
)
def update_plot(selected_channels, selected_events, x_range):
    # Filter signals based on selected channels
    if not selected_channels:
        return plot_channels({})

    filtered_sigs = {k: sigs[k] for k in selected_channels}

    # Filter events based on selection
    highlighted_events = {k: events[k] for k in selected_events} if selected_events else None

    return plot_channels(filtered_sigs, highlighted_events, x_range=x_range)
# Callback to update the x-range selection
@app.callback(
    Output("x-range-slider", "min"),
    Output("x-range-slider", "max"),
    Output("x-range-slider", "value"),
    Input("channel-checklist", "value")
)
def update_x_range(selected_channels):
    if not selected_channels:
        return 0, 0, [0, 0]
    filtered_sigs = {k: sigs[k] for k in selected_channels}
    min_time = min([min(sig[0]) for sig in filtered_sigs.values()])
    max_time = max([max(sig[0]) for sig in filtered_sigs.values()])
    return min_time, max_time, [min_time, max_time]

# Run the Dash app
if __name__ == "__main__":
    app.run_server(debug=True)
