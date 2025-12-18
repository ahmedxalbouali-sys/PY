import FreeSimpleGUI as sg
import os
import choose_testing_method_Interface



# File selection function 
def select_valid_file():
    """
    Displays a file selection window.

    - Allows user to browse and select a file
    - Accepts only ZIP, 7z, or PDF files
    - Returns: 
    ---> the selected file path if valid
    ---> None if the user cancels
    """
    valid_extensions = (".zip", ".7z", ".pdf")
    # charging the layout with necessary UI components
    layout = [
        [sg.Text("Select a file (ZIP, 7z, or PDF):")],
        [
            # saves file path in key -FILE-
            sg.Input(key="-FILE-", enable_events=True),
            # browse button
            sg.FileBrowse("Browse", file_types=(("Allowed Files", ".zip;.7z;*.pdf"),))
        ],
        [sg.Button("Submit"), sg.Button("Cancel")]
    ]
    # charging UI : the select file interface, using layout
    window = sg.Window("File Selection", layout, finalize=True)

    while True:
        # collection of events and values from the window
        event, values = window.read()

        # User closes window
        if event in (sg.WINDOW_CLOSED, "Cancel"):
            window.close()
            return None

        if event == "Submit":
            #we retrieve the selected file path using its key using values dict
            file_path = values["-FILE-"]

            # No file
            if not file_path:
                sg.popup_error("Please select a file first.")
                continue

            # Check extension
            if not file_path.lower().endswith(valid_extensions):
                sg.popup_error("Invalid file type! Only ZIP, 7z, and PDF are allowed.")
                continue

            # File accepted => call the testing method with that file
            window.close()
            choose_testing_method_Interface.choose_testing_method(file_path)
            return file_path



#--- Example usage ---        

selected = select_valid_file()
if selected:
    print("User selected:", selected)
else:
    print("User cancelled.")
