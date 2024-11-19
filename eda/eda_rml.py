import sys
sys.path.append('/home/davide/AI/Projects/apnea')

import os
import numpy as np
import xml.etree.ElementTree as ET
import pandas as pd
from settings import verbose
from utils.utils import print_time, print_progress
from utils.preprocessing import preprocess_events

rml_path = '/media/davide/T9/super_useful_dataset/downloaded_files/V3/APNEA_RML_clean/00001333-100507.rml'

def main():

    events_df = preprocess_events(rml_path, verbose = verbose)
    print("Unique event type: ")
    
    for event_type in events_df["Type"].unique():
        n_events = events_df[events_df["Type"] == event_type].shape[0]
        print("    - " + event_type + ":", n_events)
    
    print(events_df[events_df['Type'] == 'ObstructiveApnea'])
if __name__ == '__main__':
    main()