import FreeSimpleGUI as sg
import threading
import os

from Creating_custom_word_list import generate_custom_wordlist
from DefaultWordlistService import (
    default_wordlist_crack,
    get_test_function,
    is_file_protected
)

# Centralized logging service
from logging_service import add_test_log

# =================================================
# POPUP: INPUT MULTIPLE PASSWORD ELEMENTS
# =================================================
def implement_elements_popup():
    """
    Modal popup that allows the user to input password elements.
    Each line represents one element (name, date, keyword, etc.).

    Returns:
        list[str] : cleaned elements
        None      : if user cancels
    """
    layout = [
        [sg.Text("Enter password elements (one per line):", font=("Arial", 12, "bold"))],
        [sg.Multiline(
            key="-ELEMENTS-",
            size=(45, 10),
            tooltip="Names, dates, usernames, patterns, etc."
        )],
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

            elements = [
                line.strip()
                for line in raw_inputs.splitlines()
                if line.strip()
            ]

            window.close()
            return elements

# =================================================
# THREAD: GENERATE CUSTOM WORDLIST
# =================================================
def run_Custom_generation(elements, output_path, window):
    """
    Background thread responsible for generating the custom wordlist.
    Only communicates completion or error via window.write_event_value().
    """
    try:
        generate_custom_wordlist(elements, output_file=output_path)
        window.write_event_value("-GEN_DONE-", output_path)
    except Exception as e:
        window.write_event_value("-GEN_ERROR-", str(e))

# =================================================
# THREAD: RUN PASSWORD CRACKING
# =================================================
def run_default_crack(file_path, wordlist_file, window):
    """
    Background thread that runs the cracking engine using the generated wordlist.
    DOES NOT call window.read() inside the thread.
    Progress and results are sent via window.write_event_value().
    """
    test_function = get_test_function(file_path)

    if not test_function:
        window.write_event_value("-CRACK_ERROR-", "Unsupported file type.")
        return

    if not is_file_protected(file_path):
        window.write_event_value("-CRACK_DONE-", ("✔ No password required", None))
        return

    # Run cracking engine
    password, success = default_wordlist_crack(
        file_path,
        [wordlist_file],
        test_function,
        window,
        thread_limit=2
    )

    # Treat any returned password as success
    if password:
        success = True

    if success:
        window.write_event_value("-CRACK_DONE-", (f"✔ Password FOUND: {password}", password))
    else:
        window.write_event_value("-CRACK_DONE-", ("✘ Password NOT found", None))

# =================================================
# MAIN GUI FUNCTION: Custom METHOD
# =================================================
def method_Custom(file_path, username="guest"):
    """
    Custom password testing workflow.

    Steps:
    1. User defines password elements
    2. Custom wordlist is generated automatically
    3. File is tested using the generated list
    4. Wordlist is deleted after completion
    """

    sg.theme("DarkBlue3")

    # --------------------------
    # Runtime state variables
    # --------------------------
    elements = []                 # User-defined elements
    running_gen = False           # Generation thread active flag
    running_crack = False         # Cracking thread active flag
    generated_wordlist = None     # Path to generated temporary wordlist
    default_output = "custom_Custom_wordlist.txt"
    progress_value = 0

    # --------------------------
    # GUI Layout
    # --------------------------
    layout = [
        [sg.Text("Selected Target File:", font=("Arial", 12, "bold"))],
        [sg.Text(file_path, key="-FILE-", size=(60, 1), text_color="white")],
        [sg.Button("Change File", key="-CHANGE-")],
        [sg.HorizontalSeparator()],
        [sg.Input(default_output, key="-OUT-", visible=False, disabled=True)],
        [sg.Text("Progress:", font=("Arial", 11))],
        [sg.ProgressBar(
            100,
            orientation="h",
            size=(50, 20),
            key="-PROG-",
            bar_color=("#4CE66F", "#CCCCCC")
        )],
        [sg.Text(
            "Status: Idle",
            key="-STATUS-",
            size=(50, 1),
            text_color="#FFD700",
            font=("Arial", 11, "bold")
        )],
        [sg.HorizontalSeparator()],
        [
            sg.Button("Implement Elements", key="-IMP-"),
            sg.Push(),
            sg.Button("Execute", key="-EXEC-"),
            sg.Button("Cancel", key="-CANCEL-")
        ]
    ]

    window = sg.Window("Custom Wordlist Generator", layout, finalize=True)

    # =================================================
    # EVENT LOOP (MAIN THREAD)
    # =================================================
    while True:
        event, values = window.read(timeout=100)

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
        # Implement elements
        # --------------------------
        if event == "-IMP-" and not (running_gen or running_crack):
            result = implement_elements_popup()
            if result:
                elements = result
                sg.popup_ok(f"Implemented {len(elements)} elements successfully!")

        # --------------------------
        # Execute custom test
        # --------------------------
        if event == "-EXEC-" and not (running_gen or running_crack):
            if not elements:
                sg.popup_error("Please implement elements first!")
                continue

            output_path = values["-OUT-"].strip()
            generated_wordlist = output_path

            add_test_log(
                username=username,
                method="Custom",
                target_file=file_path
            )

            running_gen = True
            progress_value = 0
            window["-STATUS-"].update("Phase 1: Generating custom wordlist...", text_color="#00BFFF")
            window["-PROG-"].update(progress_value)

            threading.Thread(
                target=run_Custom_generation,
                args=(elements, output_path, window),
                daemon=True
            ).start()

        # --------------------------
        # Handle generation finished
        # --------------------------
        if event == "-GEN_DONE-":
            running_gen = False
            running_crack = True
            window["-STATUS-"].update("Phase 2: Testing passwords...", text_color="#FFA500")
            threading.Thread(
                target=run_default_crack,
                args=(file_path, values[event], window),
                daemon=True
            ).start()

        # --------------------------
        # Handle generation error
        # --------------------------
        if event == "-GEN_ERROR-":
            running_gen = False
            window["-STATUS-"].update("Generation failed", text_color="red")
            sg.popup_error(values[event])

        # --------------------------
        # Handle cracking finished
        # --------------------------
        if event == "-CRACK_DONE-":
            running_crack = False
            status_msg, password = values[event]

            window["-STATUS-"].update("Completed", text_color="#32CD32")
            window["-PROG-"].update(100)

            if generated_wordlist and os.path.exists(generated_wordlist):
                try:
                    os.remove(generated_wordlist)
                except Exception:
                    pass

            if password:
                sg.popup_ok(f"✅ Password FOUND: {password}", title="Result")
            else:
                sg.popup_ok("❌ Password NOT found", title="Result")

        # --------------------------
        # Handle cracking error
        # --------------------------
        if event == "-CRACK_ERROR-":
            running_crack = False
            if generated_wordlist and os.path.exists(generated_wordlist):
                try:
                    os.remove(generated_wordlist)
                except Exception:
                    pass
            window["-STATUS-"].update("Cracking failed", text_color="red")
            sg.popup_error(values[event])

        # --------------------------
        # Animate progress bar
        # --------------------------
        if running_gen or running_crack:
            progress_value = (progress_value + 2) % 101
            window["-PROG-"].update(progress_value)

    window.close()


# =================================================
# TEST RUN
# =================================================
if __name__ == "__main__":
    target_file = r"C:/Users/ahmed/Desktop/New folder (2)/Target/rockyou.zip"
    method_Custom(target_file, username="admin")
