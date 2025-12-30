import FreeSimpleGUI as sg

from DefaultWordlistService_GUI import method_default_wordlist
from method_bruteforce import method_bruteforce
from Custom_Wordlist_Gui import method_Custom


def choose_testing_method(file_path,username):
    valid_extensions = (".zip", ".7z", ".pdf")

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

    layout = [
        [sg.Text("Selected File:", font=("Arial", 12, "bold"))],
        [sg.Text(file_path, key="-FILE-", text_color="white")],
        [sg.Button("Change File")],
        [sg.HorizontalSeparator()],

        [sg.Text("Choose Testing Method:", font=("Arial", 11))],
        [
            sg.Button("Bruteforce Test", size=(18, 2)),
            sg.Button("Dictionary Test", size=(18, 2)),
            sg.Button("Custom Test", size=(18, 2)),
        ],

        [sg.HorizontalSeparator()],
        [sg.Button("Exit")]
    ]

    window = sg.Window("Password Testing Menu", layout)

    while True:
        event, _ = window.read()

        if event in (sg.WINDOW_CLOSED, "Exit"):
            break

        elif event == "Change File":
            new_path = change_file()
            if new_path:
                file_path = new_path
                window["-FILE-"].update(file_path)

        elif event == "Bruteforce Test":
            method_bruteforce(file_path, username)

        elif event == "Dictionary Test":
            method_default_wordlist(file_path, username)

        elif event == "Custom Test":
            method_Custom(file_path,username)

    window.close()


if __name__ == "__main__":
    file_path = r"C:\Users\ahmed\Desktop\New folder (2)\Target\New folder (4).7z"
    choose_testing_method(file_path, username="admin")
