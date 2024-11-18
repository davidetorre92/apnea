import sys
sys.path.append('/home/davide/AI/Projects/apnea')

import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pyedflib
from settings import testing_mode, images_path

# Replace 'your_file.edf' with the path to your EDF file
edf_file = "./downloaded_files/00001394-100507%5B002%5D.edf"

# Open the EDF file
f = pyedflib.EdfReader(edf_file)

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
    signals.append(f.readSignal(i))
    sampling_frequencies.append(f.getSampleFrequency(i))

# Close the EDF file
f.close()