import xml.etree.ElementTree as ET
import pyedflib
import numpy as np
import pandas as pd
from .utils import print_time, print_progress

def preprocess_events(rml_path, verbose = True):
    # Load the .rml file
    tree = ET.parse(rml_path)
    root = tree.getroot()

    # Namespace handling
    namespace = {"ns": "http://www.respironics.com/PatientStudy.xsd"}

    # Extract <Event> data
    events = root.findall(".//ns:Events/ns:Event", namespaces=namespace)

    # Collect data into a list of dictionaries
    event_data = []
    n_events = len(events)
    for i_event, event in enumerate(events):
        if verbose: print_progress(f"Processing event", i_event + 1, n_events)
        event_data.append({
        "Family": event.get("Family"),
        "Type": event.get("Type"),
        "Start": float(event.get("Start")) if event.get("Start") else None,
        "Duration": float(event.get("Duration")) if event.get("Duration") else None,
        "Machine": event.get("Machine"),
        "OriginatedOnDevice": event.get("OriginatedOnDevice")
        })
    if verbose:
        print_progress(f"Processing event", n_events, n_events)
        print()
        print_time(f"Processed {n_events} events")

    # Create a DataFrame for events
    events_df = pd.DataFrame(event_data)
    return events_df

def get_signals(edf_file_path, labels = ["ECG I", "Snore", "SpO2", "PulseRate", "Mic", "Tracheal"], target_sps = np.inf, verbose = True):
    def report_signal_data(signals, sampling_frequencies, signal_labels):
        num_signals = len(signals)
        print_time("Signal reporting:")
        for i in range(num_signals):
            if signal_labels[i] in labels:
                print(f"\033[1m{signal_labels[i]}\033[0m\t{len(signals[i])} points @ {sampling_frequencies[i]} sps")
            else:
                print(f"{signal_labels[i]}\t{len(signals[i])} points @ {sampling_frequencies[i]} sps")        

    # Get the path
    if verbose: print_time(f"Opening file {edf_file_path}...")
    # Open the EDF file
    f = pyedflib.EdfReader(edf_file_path)

    # Get the number of signals (channels)
    num_signals = f.signals_in_file

    # Get the sampling frequency
    sampling_frequency = f.getSampleFrequency(0)

    # Get the signal labels
    signal_labels = f.getSignalLabels()

    # Read the signals
    signals = []
    sampling_frequencies = []
    for i in range(num_signals):
        if verbose: print_progress(f"Reading signal", i + 1, num_signals)
        signals.append(f.readSignal(i))
        sampling_frequencies.append(f.getSampleFrequency(i))

    if verbose:
        print_progress(f"Reading signal", num_signals, num_signals)
        print()
        print_time("Done. Closing file...")

    # Close the EDF file
    f.close()
    if verbose:
        report_signal_data(signals, sampling_frequencies, signal_labels)
    return signals, sampling_frequencies, signal_labels
