import FreeSimpleGUI as sg
import os
import choose_testing_method_Interface



# --- File selection function ---
def select_valid_file():
    valid_extensions = (".zip", ".7z", ".pdf")

    layout = [
        [sg.Text("Select a file (ZIP, 7z, or PDF):")],
        [
            sg.Input(key="-FILE-", enable_events=True),
            sg.FileBrowse("Browse", file_types=(("Allowed Files", "*.zip;*.7z;*.pdf"),))
        ],
        [sg.Button("Submit"), sg.Button("Cancel")]
    ]

    window = sg.Window("File Selection", layout, finalize=True)

    while True:
        event, values = window.read()

        # User closes window
        if event in (sg.WINDOW_CLOSED, "Cancel"):
            window.close()
            return None

        if event == "Submit":
            file_path = values["-FILE-"]

            # No file
            if not file_path:
                sg.popup_error("Please select a file first.")
                continue

            # Check extension
            if not file_path.lower().endswith(valid_extensions):
                sg.popup_error("Invalid file type! Only ZIP, 7z, and PDF are allowed.")
                continue

            # File accepted
            window.close()
            choose_testing_method_Interface.choose_testing_method(file_path)
            return file_path



#--- Example usage ---        

#selected = select_valid_file()
#if selected:
#    print("User selected:", selected)
#else:
#    print("User cancelled.")