import FreeSimpleGUI as sg
import threading
import os
from Creating_custom_word_list import generate_custom_wordlist
from DefaultWordlistService import default_wordlist_crack, get_test_function, is_file_protected

# NEW: centralized logging service
from logging_service import add_test_log

# =================================================
# POPUP: INPUT MULTIPLE PASSWORD ELEMENTS
# =================================================
def implement_elements_popup():
    """
    Opens a popup window allowing the user to input multiple password prompts
    (one per line). Returns a list of cleaned strings or None if cancelled.
    """
    layout = [
        [sg.Text("Enter password elements (one per line):", font=("Arial", 12, "bold"))],
        [sg.Multiline(key="-ELEMENTS-", size=(45, 10), tooltip="Names, dates, usernames, etc.")],
        [sg.HorizontalSeparator()],
        [sg.Push(), sg.Button("Apply"), sg.Button("Cancel")]
    ]

    window = sg.Window("Implement Elements", layout, modal=True, finalize=True)

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "Cancel"):
            window.close()
            return None
        if event == "Apply":
            raw_inputs = values["-ELEMENTS-"].strip()
            if not raw_inputs:
                sg.popup_error("Please enter at least one element.")
                continue
            elements = [line.strip() for line in raw_inputs.splitlines() if line.strip()]
            window.close()
            return elements

# =================================================
# THREAD FUNCTION: GENERATE CUSTOM WORDLIST
# =================================================
def run_hybrid_generation(elements, output_path, window):
    """
    Runs generate_custom_wordlist in a separate thread to avoid freezing GUI.
    Uses window.write_event_value to notify main thread when done or if error.
    """
    try:
        generate_custom_wordlist(elements, output_file=output_path)
        window.write_event_value("-GEN_DONE-", output_path)
    except Exception as e:
        window.write_event_value("-GEN_ERROR-", str(e))

# =================================================
# THREAD FUNCTION: RUN DEFAULT WORDLIST CRACK
# =================================================
def run_default_crack(file_path, wordlist_file, window):
    """
    Calls default_wordlist_crack in a background thread.
    Updates GUI via window.write_event_value events.
    """
    test_function = get_test_function(file_path)
    if not test_function:
        window.write_event_value("-CRACK_ERROR-", "Unsupported file type.")
        return

    if not is_file_protected(file_path):
        window.write_event_value("-CRACK_DONE-", ("✔ No password required", None))
        return

    password, success = default_wordlist_crack(
        file_path,
        [wordlist_file],
        test_function,
        window,
        thread_limit=2
    )

    if success:
        window.write_event_value("-CRACK_DONE-", (f"✔ Password found: {password}", password))
    else:
        window.write_event_value("-CRACK_DONE-", ("✘ Password NOT found", None))

# =================================================
# MAIN FUNCTION: HYBRID GUI
# =================================================
def method_hybrid(file_path, username="guest"):
    """
    Hybrid GUI function:
    - Allows changing target file
    - Implement Elements for custom passwords
    - Generates custom wordlist in background
    - Uses default_wordlist_crack to test passwords
    - Shows progress and status
    - Logs the test attempt when execution begins
    """
    sg.theme("DarkBlue3")

    elements = []           # Stores implemented password elements
    running_gen = False     # Flag for generation
    running_crack = False   # Flag for cracking

    default_output = "custom_hybrid_wordlist.txt"
    progress_value = 0      # Progress bar simulation

    layout = [
        [sg.Text("Selected Target File:", font=("Arial", 12, "bold"))],
        [sg.Text(file_path, key="-FILE-", size=(60, 1))],
        [sg.Button("Change File", key="-CHANGE-")],
        [sg.HorizontalSeparator()],

        [sg.Text("Progress:", font=("Arial", 11))],
        [sg.ProgressBar(100, orientation="h", size=(50, 20), key="-PROG-", bar_color=("#4CE66F", "#CCCCCC"))],
        [sg.Text("", key="-STATUS-", size=(50, 1), text_color="#4CE66F")],
        [sg.HorizontalSeparator()],

        [sg.Text("Output Wordlist File:", font=("Arial", 11))],
        [sg.Input(default_output, key="-OUT-", size=(40,1)),
         sg.FileSaveAs("Browse", file_types=(("Text files","*.txt"),), default_extension=".txt")],
        [sg.HorizontalSeparator()],

        [sg.Button("Implement Elements", key="-IMP-"),
         sg.Push(),
         sg.Button("Execute", key="-EXEC-"),
         sg.Button("Cancel", key="-CANCEL-")]
    ]

    window = sg.Window("Hybrid Wordlist Generator", layout, finalize=True)

    while True:
        event, values = window.read(timeout=100)

        # --------------------------
        # Close or Cancel
        # --------------------------
        if event in (sg.WINDOW_CLOSED, "-CANCEL-"):
            break

        # --------------------------
        # Change target file
        # --------------------------
        if event == "-CHANGE-" and not (running_gen or running_crack):
            new_file = sg.popup_get_file(
                "Select target file",
                file_types=(("Allowed files", "*.zip;*.7z;*.pdf"),)
            )
            if new_file:
                file_path = new_file
                window["-FILE-"].update(file_path)

        # --------------------------
        # Implement Elements
        # --------------------------
        if event == "-IMP-" and not (running_gen or running_crack):
            result = implement_elements_popup()
            if result:
                elements = result
                sg.popup_ok(f"Implemented {len(elements)} elements successfully!")

        # --------------------------
        # Execute Button
        # --------------------------
        if event == "-EXEC-" and not (running_gen or running_crack):
            if not elements:
                sg.popup_error("Please implement elements first!")
                continue

            output_path = values["-OUT-"].strip()
            if not output_path:
                sg.popup_error("Please select an output file path!")
                continue

            # ---------------------------------------------------
            # LOG THE TEST ATTEMPT (ONCE, BEFORE EXECUTION)
            # ---------------------------------------------------
            add_test_log(
                username=username,
                method="hybrid",
                target_file=file_path
            )

            # --- Start generation ---
            running_gen = True
            window["-STATUS-"].update("Phase 1: Generating custom wordlist...")
            window["-PROG-"].update(0)

            threading.Thread(
                target=run_hybrid_generation,
                args=(elements, output_path, window),
                daemon=True
            ).start()

        # --------------------------
        # Event: Generation Done
        # --------------------------
        if event == "-GEN_DONE-":
            running_gen = False
            wordlist_file = values[event]
            window["-STATUS-"].update("Phase 2: Testing passwords...")
            window["-PROG-"].update(0)

            # --- Start cracking ---
            running_crack = True
            threading.Thread(
                target=run_default_crack,
                args=(file_path, wordlist_file, window),
                daemon=True
            ).start()

        # --------------------------
        # Event: Generation Error
        # --------------------------
        if event == "-GEN_ERROR-":
            running_gen = False
            window["-STATUS-"].update("")
            sg.popup_error(f"Custom wordlist generation failed:\n{values[event]}")

        # --------------------------
        # Event: Cracking Done
        # --------------------------
        if event == "-CRACK_DONE-":
            running_crack = False
            status_msg, password = values[event]
            window["-STATUS-"].update("Completed")
            window["-PROG-"].update(100)
            sg.popup_ok(status_msg)

        # --------------------------
        # Event: Cracking Error
        # --------------------------
        if event == "-CRACK_ERROR-":
            running_crack = False
            window["-STATUS-"].update("")
            sg.popup_error(f"Password cracking failed:\n{values[event]}")

        # --------------------------
        # Simulate smooth progress bar while running
        # --------------------------
        if running_gen or running_crack:
            progress_value = (progress_value + 1) % 101
            window["-PROG-"].update(progress_value)

    window.close()


# =================================================
# TEST RUN
# =================================================
if __name__ == "__main__":
    target_file = "C:/Users/ahmed/Desktop/Target/test.zip"
    method_hybrid(target_file, username="admin")
