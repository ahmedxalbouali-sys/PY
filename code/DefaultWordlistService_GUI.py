import FreeSimpleGUI as sg
import os

from DefaultWordlistService import (
    default_wordlist_crack,
    get_test_function,
    is_file_protected
)

# NEW: centralized logging service
from logging_service import add_test_log


# -------------------------------------------------------
# Wordlist selection popup
# -------------------------------------------------------
def select_wordlist_popup(current_wordlists):
    """
    Popup allowing the user to select which wordlists
    will be used for the default wordlist attack.
    """

    rockyou_path = r"C:\Users\ahmed\Desktop\New folder (2)\wordlists\rockyou.txt"
    crackstation_path = r"C:\Users\ahmed\Desktop\New folder (2)\wordlists\crackstation.txt.txt"

    layout = [
        [sg.Text("Selected wordlists (tested top → bottom)", font=("Arial", 12, "bold"))],
        [sg.Checkbox("RockYou", key="-ROCK-", default=(rockyou_path in current_wordlists))],
        [sg.Checkbox("CrackStation", key="-CRACK-", default=(crackstation_path in current_wordlists))],
        [
            sg.Checkbox("Other", key="-OTHER-"),
            sg.Input(key="-OTHER_PATH-", size=(25, 1), disabled=True),
            sg.FileBrowse("Browse", file_types=(("Wordlists", "*.txt"),))
        ],
        [sg.HorizontalSeparator()],
        [sg.Push(), sg.Button("Confirm"), sg.Button("Cancel")]
    ]

    window = sg.Window("Wordlist selection", layout, modal=True)

    while True:
        event, values = window.read()

        if event in (sg.WINDOW_CLOSED, "Cancel"):
            window.close()
            return current_wordlists

        window["-OTHER_PATH-"].update(disabled=not values["-OTHER-"])

        if event == "Confirm":
            selected = []

            if values["-ROCK-"]:
                if not os.path.exists(rockyou_path):
                    sg.popup_error(f"Wordlist does not exist:\n{rockyou_path}")
                    continue
                selected.append(rockyou_path)

            if values["-CRACK-"]:
                if not os.path.exists(crackstation_path):
                    sg.popup_error(f"Wordlist does not exist:\n{crackstation_path}")
                    continue
                selected.append(crackstation_path)

            if values["-OTHER-"] and values["-OTHER_PATH-"]:
                other_path = values["-OTHER_PATH-"]
                if not os.path.exists(other_path):
                    sg.popup_error(f"Wordlist does not exist:\n{other_path}")
                    continue
                selected.append(other_path)

            if not selected:
                sg.popup_error("Select at least one wordlist.")
                continue

            window.close()
            return selected


# -------------------------------------------------------
# MAIN GUI FUNCTION — DEFAULT WORDLIST METHOD
# -------------------------------------------------------
def method_default_wordlist(file_path, username):
    """
    GUI entry point for the default wordlist password testing method.

    This function:
    - Allows wordlist selection
    - Handles UI interaction
    - Starts the cracking process
    - Logs the test attempt when execution begins
    """

    valid_ext = (".zip", ".7z", ".pdf")
    default_wordlists = [
        r"C:\Users\ahmed\Desktop\New folder (2)\wordlists\rockyou.txt"
    ]

    sg.theme("DarkBlue3")

    layout = [
        [sg.Text("Selected file:", font=("Arial", 11))],
        [sg.Text(file_path, key="-FILE-", text_color="white")],
        [sg.Button("Change file", key="-CHANGE-")],
        [sg.HorizontalSeparator()],
        [
            sg.Text("Wordlists: rockyou.txt", font=("Arial", 11), key="-WL_LABEL-"),
            sg.Push(),
            sg.Button("Change wordlist", key="-SELECTED-")
        ],
        [sg.Text("Testing ... ", key="-STATUS-", font=("Arial", 11))],
        [sg.ProgressBar(
            1000,
            orientation="h",
            size=(40, 20),
            key="-PROG-",
            bar_color=("#4CE66F", "#CCCCCC")
        )],
        [sg.Text(
            "",
            key="-RESULT-",
            font=("Arial", 12, "bold"),
            size=(45, 1),
            justification="center"
        )],
        [sg.Push(),
         sg.Button("Begin", key="-BEGIN-", size=(8, 1)),
         sg.Button("Cancel", key="-CANCEL-", size=(8, 1))]
    ]

    window = sg.Window("Default wordlist tester", layout, finalize=True)

    testing = False

    while True:
        event, values = window.read(timeout=10)

        if event in (sg.WINDOW_CLOSED, "-CANCEL-"):
            break

        if event == "-CHANGE-" and not testing:
            new_file = sg.popup_get_file(
                "Choose file",
                file_types=(("Allowed", "*.zip;*.7z;*.pdf"),)
            )
            if new_file and new_file.lower().endswith(valid_ext):
                file_path = new_file
                window["-FILE-"].update(file_path)

        if event == "-SELECTED-" and not testing:
            default_wordlists = select_wordlist_popup(default_wordlists)
            window["-WL_LABEL-"].update(
                "Wordlists: " + ", ".join(os.path.basename(w) for w in default_wordlists)
            )

        # ---------------------------------------------------
        # EXECUTE DEFAULT WORDLIST TEST
        # ---------------------------------------------------
        if event == "-BEGIN-" and not testing:
            # Validate wordlists existence
            missing_files = [wl for wl in default_wordlists if not os.path.exists(wl)]
            if missing_files:
                sg.popup_error(
                    "Wordlist file(s) do not exist:\n" + "\n".join(missing_files)
                )
                continue

            # ---------------------------------------------------
            # LOG THE TEST ATTEMPT (ONCE, BEFORE EXECUTION)
            # ---------------------------------------------------
            add_test_log(
                username=username,
                method="default_wordlist",
                target_file=file_path
            )

            testing = True
            window["-STATUS-"].update("Testing...")
            window["-RESULT-"].update("")
            window["-PROG-"].update(0)

            test_function = get_test_function(file_path)

            if not test_function:
                testing = False
                continue

            if not is_file_protected(file_path):
                window["-RESULT-"].update("✔ No password required")
                testing = False
                continue

            password, success = default_wordlist_crack(
                file_path,
                default_wordlists,
                test_function,
                window,
                thread_limit=2
            )

            window["-STATUS-"].update("Completed")

            if success:
                window["-RESULT-"].update(f"✔ Password found: {password}")
            else:
                window["-RESULT-"].update("✘ Password NOT found")

            testing = False

    window.close()


# -------------------------------------------------------
# TEST RUN
# -------------------------------------------------------
if __name__ == "__main__":
    target_file = r"C:\Users\ahmed\Desktop\New folder (2)\Target\New folder (4).7z"
    method_default_wordlist(target_file, username="admin")
