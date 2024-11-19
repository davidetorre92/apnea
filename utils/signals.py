import sys
sys.path.append('/home/davide/AI/Projects/apnea')

import os
import numpy as np
from settings import verbose
from utils.utils import print_time, print_progress
from scipy.signal import resample, butter, filtfilt
import pyedflib

def resample_signals(sigs, target_sps):
    # Resampling sps
    cutoff_freq = target_sps / 3  # Less than half of the target_sps frequency
    filter_order = 6  # Third order filter

    def low_pass_filter(data, cutoff, fs, order=3):
        nyquist = 0.5 * fs
        normal_cutoff = cutoff / nyquist
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        y = filtfilt(b, a, data)
        return y

    resampled_sigs = {}

    for k, v in sigs.items():
        # Resample the signals
        original_signal = sigs[k][0]
        original_sps = sigs[k][1]
        num_samples = len(original_signal)
        
        if original_sps > target_sps:
            if verbose: print_time(f"Applying low-pass filter of order {filter_order} to {k} at {cutoff_freq:.2f} Hz and resampling from {int(original_sps)} to {target_sps} sps")
            
            # Apply low-pass filter
            filtered_signal = low_pass_filter(original_signal, cutoff_freq, original_sps, filter_order)
            
            # Resample the filtered signal
            num_resampled_samples = int(num_samples * target_sps / original_sps)
            resampled_signal = resample(filtered_signal, num_resampled_samples)
            
            # Update the signal in the dictionary
            resampled_sigs[k] = (resampled_signal, target_sps)
        else:
            resampled_sigs[k] = sigs[k]
    return resampled_sigs