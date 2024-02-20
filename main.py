import pygetwindow as gw
import time
import os
import socket
from pynput import mouse, keyboard

class ActivityChecker:
    def __init__(self):
        self.last_activity_time = time.time()

    def on_activity(self, *args):
        self.last_activity_time = time.time()

    def is_inactive(self, interval):
        return time.time() - self.last_activity_time > interval

def write_log(message):
    computer_name = socket.gethostname()
    log_filename = f"activity_log_{computer_name}.txt"
    log_path = os.path.join(os.path.expanduser("~"), log_filename)
    with open(log_path, 'a') as log_file:
        log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

def monitor_apps(app_names, inactivity_duration=1800):
    activity_checker = ActivityChecker()
    last_logged_app = None
    app_open_times = {}
    mouse_listener = mouse.Listener(on_click=activity_checker.on_activity, on_scroll=activity_checker.on_activity)
    keyboard_listener = keyboard.Listener(on_press=activity_checker.on_activity)
    mouse_listener.start()
    keyboard_listener.start()

    while True:
        current_active_window = gw.getActiveWindow()
        if current_active_window:
            current_app_name = current_active_window.title
            for app_name in app_names:
                if app_name in current_app_name:
                    app_open_times[app_name] = time.time()
                    if last_logged_app != current_app_name:
                        write_log(f"Switched to '{current_app_name}'")
                        last_logged_app = current_app_name

        # Check for application close conditions
        for app_name in app_open_times:
            if activity_checker.is_inactive(inactivity_duration) or \
               (time.time() - app_open_times[app_name]) > inactivity_duration:
                app_windows = gw.getWindowsWithTitle(app_name)
                for window in app_windows:
                    if window != current_active_window:
                        window.close()
                        write_log(f"Closed '{app_name}' due to inactivity or over 30 minutes of run time.")

        time.sleep(0.5)  # Check every half second

    mouse_listener.stop()
    keyboard_listener.stop()

application_names = ['Keyloop Drive', 'Sales Executive', 'Vehicle Stock Management',
                     'Sales Activity', 'New Enquiry', 'Sales Prospecting',
                     'Sales Performance Exec', 'Report Desktop', 'Advanced Option']

monitor_apps(application_names)
