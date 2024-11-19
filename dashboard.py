from dash import Dash, dcc, html, Input, Output, State, callback
import os

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
    dcc.Input(id='path', type='text', value='', placeholder='Enter path'),
    html.Button(id='submit-button-state', n_clicks=0, children='Submit'),
    html.Div(id='output-state'),
    html.Div(
        id='dropdown-container', 
        children=[
            dcc.Dropdown(id='patient-selection-bar', options=[])
        ],
        style={'display': 'none'}  # Initially hidden
    )
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

if __name__ == '__main__':
    app.run(debug=True)
