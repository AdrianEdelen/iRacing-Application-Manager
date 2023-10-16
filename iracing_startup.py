import subprocess
import sys
import time
import tkinter as tk
from tkinter import ttk
import json
from tkinter import simpledialog
from tkinter import filedialog
import json
import tkinter as tk
from tkinter import ttk, simpledialog, filedialog
import psutil
from ttkthemes import ThemedTk
PROGRAMS_FILE = 'programs.json'
BUTTON_WIDTH = 10
LABEL_WIDTH = 20

processes = {}
status_labels = {}


def load_programs():
    try:
        with open(PROGRAMS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_programs(programs):
    with open(PROGRAMS_FILE, 'w') as f:
        json.dump(programs, f)


def add_program():
    name = simpledialog.askstring("Input", "What is the name of the program?")
    if name:
        path = filedialog.askopenfilename(title="Select the program executable")
        if path:
            programs[name] = {"path": path, "autostart": False}
            save_programs(programs)
            refresh_programs()


def delete_program(name):
    del programs[name]
    save_programs(programs)
    refresh_programs()


def start_program(name, path):
    pid = is_program_running(path)
    if pid:
        print(f"{name} is already running!")
        processes[name] = psutil.Process(pid)  # Store the process for later management
    else:
        if name not in processes:
            processes[name] = subprocess.Popen(path)
            status_labels[name].config(text="Running")



def stop_program(name):
    pid = is_program_running(programs[name]["path"]) # Modify this line to use the path instead of name
    if pid:
        process = psutil.Process(pid)
        process.terminate()
        status_labels[name].config(text="Not Running")
        processes.pop(name, None)
    else:
        print(f"{name} is not running!")



def update_statuses():
    for name, details in programs.items():
        if is_program_running(details["path"]):
            status_labels[name].config(text="Running")
        else:
            status_labels[name].config(text="Not Running")
            # Remove from processes dict if it's there
            processes.pop(name, None)
    root.after(1000, update_statuses)  # Check every 10 seconds

def fast_update_statuses():
    for name in list(processes.keys()):
        process = processes[name]
        if isinstance(process, subprocess.Popen):
            is_alive = process.poll() is None
        elif isinstance(process, psutil.Process):
            is_alive = process.is_running()
        else:
            is_alive = False
        
        if is_alive:
            status_labels[name].config(text="Running")
        else:
            status_labels[name].config(text="Not Running")
            processes.pop(name)
    root.after(500, fast_update_statuses)  # Check every 0.5 seconds for known PIDs


def slow_update_statuses():
    for name, details in programs.items():
        if name not in processes:
            pid = is_program_running(details["path"])
            if pid:
                processes[name] = psutil.Process(pid)
                status_labels[name].config(text="Running")
    root.after(10000, slow_update_statuses)  # Check every 10 seconds by program name


def refresh_programs():
    for widget in program_frame.winfo_children():
        widget.destroy()

    populate_program_ui()
    update_statuses()


def start_all_programs():
    for name, details in programs.items():
        start_program(name, details["path"])


def stop_all_programs():
    # Making a copy of keys as dictionary size will change during iteration
    for name in list(processes.keys()):
        stop_program(name)

def is_program_running(path):
    # Get the program name from the path
    program_name = path.split('/')[-1]

    for process in psutil.process_iter(attrs=['pid', 'name']):
        # Compare the process name with the program name
        if program_name == process.info['name']:
            return process.info['pid']
    return None


def command_line_run():
    for name, details in programs.items():
        if details.get('autostart', False):
            start_program(name, details["path"])

    # Wait until all processes are finished
    while processes:
        for name in list(processes.keys()):  # Making a copy of keys
            if processes[name].poll() is not None:
                del processes[name]
        time.sleep(1)


def toggle_autostart(name, var):
    programs[name]['autostart'] = var.get()
    save_programs(programs)

def populate_program_ui():
    global program_frame
    for name, details in programs.items():
        frame = ttk.Frame(program_frame)
        frame.pack(padx=10, pady=5, fill=tk.X, expand=True)
        
        autostart_var = tk.BooleanVar()
        autostart_var.set(details['autostart'])
        checkbox = ttk.Checkbutton(frame, text="Autostart", variable=autostart_var, 
                                   command=lambda n=name, var=autostart_var: toggle_autostart(n, var))
        checkbox.grid(row=0, column=0, sticky='w')
        
        ttk.Label(frame, text=name, width=LABEL_WIDTH).grid(row=0, column=1, sticky='w')
        
        ttk.Button(frame, text="Start", width=BUTTON_WIDTH, 
                   command=lambda n=name, p=details["path"]: start_program(n, p)).grid(row=0, column=2, sticky='w')
        ttk.Button(frame, text="Stop", width=BUTTON_WIDTH, 
                   command=lambda n=name: stop_program(n)).grid(row=0, column=3, sticky='w')
        ttk.Button(frame, text="Delete", width=BUTTON_WIDTH, 
                   command=lambda n=name: delete_program(n)).grid(row=0, column=4, sticky='w')
        pid = is_program_running(details["path"])
        if pid:
            status_text = "Running"
            processes[name] = psutil.Process(pid)  # Store the process for later management
        else:
            status_text = "Not Running"
        # Check if the program is already running and update label accordingly
        #if is_program_running(details["path"]):
        #    status_text = "Running"
        #else:
        #    status_text = "Not Running"
        

        status_label = ttk.Label(frame, text=status_text, width=LABEL_WIDTH)
        status_label.grid(row=0, column=5, sticky='w')
        status_labels[name] = status_label


if __name__ == "__main__":
    programs = load_programs()

    if len(sys.argv) > 1 and sys.argv[1] == "--run":
        command_line_run()
    else:
        root = ThemedTk(theme="arc")
        root.iconbitmap('checkmark.ico')
        root.title("iRacing Application Manager")
        program_frame = ttk.Frame(root)
        program_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        #style = ttk.Style()
        #print(style.theme_names())
        #style.theme_use('clam')
        populate_program_ui()
        for name, details in programs.items():
            if details.get('autostart', False):
                start_program(name, details["path"])
        #root.after(500, update_statuses)
        root.after(500, fast_update_statuses)  # Start the faster update cycle
        root.after(10000, slow_update_statuses)
        bottom_frame = ttk.Frame(root)
        bottom_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
    
        ttk.Button(bottom_frame, text="Start All", command=start_all_programs).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="Stop All", command=stop_all_programs).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="Add Program", command=add_program).pack(side=tk.LEFT, padx=5)
        root.mainloop()

