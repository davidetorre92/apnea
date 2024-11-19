import os
from datetime import datetime

def print_time(string, fp = None):
    string = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {string}"
    if fp is None:
        print(string)
    else:
        fp.write(string)
    return 1

def print_progress(title_string, i, max, status_str = "", n_char = 100, null_str = '-', adv_str = '#'):
    n_adv = int((i / max) * n_char)
    n_null = n_char - n_adv
    string = f"{title_string}"
    string += f" |{adv_str * n_adv}{null_str * n_null}| {i}/{max}"
    print(string, end = '\r')
    return

def create_folder(path, is_file = True, verbose = False):
    # If path is a file with extension, extract folder from filename
    if is_file: folder = os.path.dirname(path)
    else: folder = path
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
        print_time(f"Created folder {folder}")
        return 1
    else:
        if verbose: print_time(f"Folder {folder} already exists")
        return 0
