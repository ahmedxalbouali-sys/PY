import FreeSimpleGUI as sg
import os

# ----------------------------
# Placeholder method functions
# ----------------------------
def method_bruteforce(file_path):
    sg.popup("Bruteforce method activated!", f"Target file: {file_path}")

def method_default_wordlist(file_path):
    sg.popup("Default wordlist method activated!", f"Target file: {file_path}")

def method_custom_wordlist(file_path):
    sg.popup("Custom wordlist method activated!", f"Target file: {file_path}")



# --------------------------------------------
# The MAIN function you asked for
# Accepts: file_path (string)
# Opens GUI: lets user change file and pick method
# --------------------------------------------
def choose_testing_method(file_path):

    valid_extensions = (".zip", ".7z", ".pdf")

    # --- Internal function to re-select a new file ---
    def change_file():
        new_file = sg.popup_get_file(
            "Select another file",
            file_types=(("Allowed Files", "*.zip;*.7z;*.pdf"),)
        )

        if new_file and new_file.lower().endswith(valid_extensions):
            return new_file
        else:
            sg.popup_error("Invalid file. Must be ZIP / 7z / PDF.")
            return None

    # --- Main layout ---
    layout = [
        [sg.Text("Selected File:", font=("Arial", 12, "bold"))],
        [sg.Text(file_path, key="-FILE-", text_color="yellow")],
        [sg.Button("Change File")],
        [sg.HorizontalSeparator()],

        [sg.Text("Choose Testing Method:", font=("Arial", 11))],
        [
            sg.Button("Test with brute force ", size=(18, 2)),
            sg.Button("Test with default wordlist", size=(18, 2)),
            sg.Button("Test with custom wordlist", size=(18, 2)),
        ],

        [sg.HorizontalSeparator()],
        [sg.Button("Exit")]
    ]

    window = sg.Window("Password Testing Menu", layout, finalize=True)

    while True:
        event, values = window.read()

        if event in (sg.WINDOW_CLOSED, "Exit"):
            break

        # ----- Change selected file -----
        elif event == "Change File":
            new_path = change_file()
            if new_path:
                file_path = new_path
                window["-FILE-"].update(file_path)

        # ----- Method Buttons -----
        elif event == "Test with brute force ":
            method_bruteforce(file_path)

        elif event == "Test with default wordlist":
            method_default_wordlist(file_path)

        elif event == "Test with custom wordlist":
            method_custom_wordlist(file_path)

    window.close()

#file_path = "C:/Users/ahmed/Desktop/test.zip"
#choose_testing_method(file_path)
