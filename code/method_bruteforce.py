"""
method_bruteforce.py
====================

Main GUI for brute-force execution using FreeSimpleGUI.

Features:
- File selection
- Advanced configuration
- Thread count control
- Accurate progress tracking
- Safe cancellation
- Clear result display

Author: Ahmed Bouali
Date: 2025-12-22
"""

import FreeSimpleGUI as sg
import threading

from bruteforce_engine import (
    brute_force_attack,
    DEFAULT_CHARSET,
    DEFAULT_MIN_LEN,
    DEFAULT_MAX_LEN,
    DEFAULT_THREADS
)

# ==========================================================
# ADVANCED SETTINGS POPUP
# ==========================================================
def advanced_settings_popup(min_len, max_len, threads, mask):
    """
    Allows the user to configure advanced brute-force options.
    """

    layout = [
        [sg.Text("Advanced Bruteforce Settings", font=("Arial", 13, "bold"))],
        [sg.HorizontalSeparator()],

        [sg.Text("Minimum length:"), sg.Input(min_len, size=(6,1), key="-MIN-")],
        [sg.Text("Maximum length:"), sg.Input(max_len, size=(6,1), key="-MAX-")],
        [sg.Text("Threads:"), sg.Input(threads, size=(6,1), key="-THREADS-")],

        [sg.HorizontalSeparator()],
        [sg.Text("Mask pattern (use | per position):")],
        [sg.Input(mask, size=(45,1), key="-MASK-")],
        [sg.Text("Example: a|bc||9", font=("Arial", 9, "italic"))],

        [sg.Push(), sg.Button("Apply"), sg.Button("Cancel")]
    ]

    window = sg.Window("Advanced Settings", layout, modal=True)

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "Cancel"):
            window.close()
            return None

        if event == "Apply":
            try:
                window.close()
                return (
                    int(values["-MIN-"]),
                    int(values["-MAX-"]),
                    int(values["-THREADS-"]),
                    values["-MASK-"]
                )
            except ValueError:
                sg.popup_error("Invalid numeric input")


# ==========================================================
# MAIN APPLICATION WINDOW
# ==========================================================
def method_bruteforce(file_path):

    sg.theme("DarkBlue3")

    min_len = DEFAULT_MIN_LEN
    max_len = DEFAULT_MAX_LEN
    threads = DEFAULT_THREADS
    mask_string = ""

    progress = [0]
    total = [1]
    result = [None]
    running = [False]
    stop_flag = threading.Event()

    layout = [
        [sg.Text("Target file:", font=("Arial", 11, "bold"))],
        [sg.Text(file_path, size=(70,1), key="-FILE-")],
        [sg.Button("Change target file")],

        [sg.HorizontalSeparator()],
        [sg.Text("Status:"), sg.Text("Idle", key="-STATUS-")],
        [sg.ProgressBar(100, size=(45,20), key="-PROG-")],
        [sg.Text("", key="-RESULT-", font=("Arial", 12, "bold"))],

        [sg.Button("Advanced Settings"),
         sg.Push(),
         sg.Button("Execute"),
         sg.Button("Cancel")]
    ]

    window = sg.Window("Bruteforce Method", layout, finalize=True)

    # ======================================================
    # PROGRESS CALLBACK
    # ======================================================
    def progress_cb(done, total_count):
        progress[0] = done
        total[0] = total_count

    # ======================================================
    # ENGINE THREAD
    # ======================================================
    def run_engine():
        res = brute_force_attack(
            file_path=file_path,
            min_len=min_len,
            max_len=max_len,
            charset=DEFAULT_CHARSET,
            table_string=mask_string,
            thread_count=threads,
            progress_callback=progress_cb,
            stop_flag=stop_flag
        )
        result[0] = res
        running[0] = False

    # ======================================================
    # EVENT LOOP
    # ======================================================
    while True:
        event, _ = window.read(timeout=100)

        if event in (sg.WINDOW_CLOSED, "Cancel"):
            stop_flag.set()
            break

        if event == "Change target file" and not running[0]:
            new = sg.popup_get_file("Select file")
            if new:
                file_path = new
                window["-FILE-"].update(file_path)

        if event == "Advanced Settings" and not running[0]:
            res = advanced_settings_popup(min_len, max_len, threads, mask_string)
            if res:
                min_len, max_len, threads, mask_string = res

        if event == "Execute" and not running[0]:
            stop_flag.clear()
            progress[0] = 0
            result[0] = None
            running[0] = True

            window["-STATUS-"].update("Running...")
            window["-RESULT-"].update("")

            threading.Thread(target=run_engine, daemon=True).start()

        if running[0]:
            percent = int((progress[0] / max(total[0],1)) * 100)
            window["-PROG-"].update(percent)
            window["-STATUS-"].update(f"Testing {progress[0]} / {total[0]-10} +-10")

        else:
            if result[0]:
                window["-RESULT-"].update(f"✔ Password FOUND: {result[0]}", text_color="green")
            elif progress[0] > 0:
                window["-RESULT-"].update("✘ Password NOT found", text_color="red")

    window.close()

# =================================================
# TEST RUN
# =================================================
#file_path = "C:\\Users\\ahmed\\Desktop\\New folder (2)\\Target\\New folder (4).7z"
#method_bruteforce(file_path)
