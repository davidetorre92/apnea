import sys
sys.path.append('/home/davide/AI/Projects/apnea')

import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from utils.utils import print_progress, print_time, create_folder
from utils.preprocessing import get_signals
from utils.signals import resample_signals
from settings import verbose, testing_mode, edf_path, images_directory

edf_filename = "00001701-100507/00001701-100507[002].edf"
labels = ["ECG I", "Snore", "SpO2", "PulseRate", "Mic", "Tracheal", "Flow Patient"]
target_sps = 500

def plot_channels(sigs):
    # Set plot
    fig, axs = plt.subplots(len(sigs), 1, figsize=(15, 10), sharex=True)
    # Set truncation time to 60 seconds
    length_to_plot = target_sps * 60
    for i, (k, v) in enumerate(sigs.items()):
        # Normalize time to seconds
        time = np.arange(0, len(v[0])) / v[1]
        # Truncate the signal to 60 seconds
        time = time[:length_to_plot]

        axs[i].plot(time, v[0][:length_to_plot], linewidth=0.2)
        axs[i].set_ylabel(k)
        axs[i].set_xlim([0, time[-1]])
        axs[i].grid()

    fig.suptitle("EDF file: " + edf_filename)
    axs[-1].set_xlabel("Time (s)")
    fig.tight_layout()

    return fig, axs
def main():
    edf_file_path = os.path.join(edf_path, edf_filename)
    signals, sampling_frequencies, signal_labels = get_signals(edf_file_path, labels)
    sigs = {signal_labels[i]: (signals[i], sampling_frequencies[i]) for i in range(len(signals)) if signal_labels[i] in labels}
    resampled_sigs = resample_signals(sigs, target_sps)
    fig, axs = plot_channels(resampled_sigs)
    img_path = os.path.join(images_directory, "signal_plot.png")
    create_folder(img_path)
    fig.savefig(img_path)
    if verbose: print_time(f"Plot saved to {img_path}")

if __name__ == "__main__":
    main()