from plotly.subplots import make_subplots
import plotly.graph_objects as go

def plot_channels(sigs, event_highlights=None, x_range=None, event_colors = ['red', 'yellow', 'greed', 'orange'], signal_color = 'blue'):
    # Create a figure with subplots for each channel
    if len(sigs) == 0:
        return {
            "data": [],
            "layout": {
                "xaxis": {"type": "linear"},
                "yaxis": {"type": "linear"},
                "showlegend": True,
                "title": "Signal Plot"
            }
        }

    fig = make_subplots(rows=len(sigs), cols=1, shared_xaxes=True)
    for i, (k, v) in enumerate(sigs.items()):
        # Add traces for signal data
        fig.add_trace(
            go.Scatter(
                x=v[0], y=v[1],
                name=k,
                line=dict(color=signal_color),  # Uniform color for all traces
            ),
            row=i + 1, col=1
        )

    # Add event highlights as vertical shaded regions
    if event_highlights:
        for (event, event_data) in event_highlights.items():
            time_ranges = event_data['data']
            i = event_data['order']
            color = event_colors[i % len(event_colors)]  # Cycle through colors
            for time_range in time_ranges:
                fig.add_vrect(
                    x0=time_range[0], x1=time_range[1],
                    fillcolor=color,
                    layer="below",  # Behind the signals
                    line_width=2,
                    line_color='#111111',
                    annotation_text=event,
                    annotation_position="top left",
                    opacity=1,
                    name=f"{event}",
                )
            # Add a dummy trace for legend
            fig.add_trace(
                go.Scatter(
                    x=[None],
                    y=[None],
                    mode="markers",
                    marker=dict(size=10, color=color),
                    name=f"{event}"
                )
            )
    # Update x-axis range if specified
    if x_range:
        fig.update_xaxes(range=x_range)

    # Customize layout
    fig.update_layout(
        height=300 + 100 * len(sigs),
        title="EDF Signal Viewer with Events",
        template="simple_white",
    )

    return fig