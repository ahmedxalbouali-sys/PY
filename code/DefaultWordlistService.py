import FreeSimpleGUI as sg
import time
import os

from testpass import (
    test_zip, test_7z, test_pdf,
    is_zip_protected, is_7z_protected, is_pdf_protected
)



# -------------------------------------------------------
# Detect correct testing function based on file extension
# -------------------------------------------------------
def get_test_function(file_path):
    ext = file_path.lower()
    if ext.endswith(".zip"):
        return test_zip
    elif ext.endswith(".7z"):
        return test_7z
    elif ext.endswith(".pdf"):
        return test_pdf
    return None
# -------------------------------------------------------
# Detect if the file is protected or not
# -------------------------------------------------------
def is_file_protected(file_path):
    ext = file_path.lower()
    if ext.endswith(".zip"):
        return is_zip_protected(file_path)
    elif ext.endswith(".7z"):
        return is_7z_protected(file_path)
    elif ext.endswith(".pdf"):
        return is_pdf_protected(file_path)
    return False


# -------------------------------------------------------
# Wordlist selection popup (MULTI wordlists, ORDERED)
# -------------------------------------------------------
def select_wordlist_popup(current_wordlists):

    #THESE PATHS NEEDS TO BE CHANGED LATER WITH ABSOLUTE PATH
    rockyou_path = "C:/Users/nourb/OneDrive/Bureau/CyberEng Learning/uniprojects/PY/wordlists/rockyou.txt"
    crackstation_path = "C:/Users/nourb/OneDrive/Bureau/CyberEng Learning/uniprojects/PY/wordlists/crackstation.txt"

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
                selected.append(rockyou_path)
            if values["-CRACK-"]:
                selected.append(crackstation_path)
            if values["-OTHER-"] and values["-OTHER_PATH-"]:
                selected.append(values["-OTHER_PATH-"])

            if not selected:
                sg.popup_error("Select at least one wordlist.")
                continue

            window.close()
            return selected


# -------------------------------------------------------
# Wordlist cracking logic (MULTI wordlists)
# -------------------------------------------------------
def default_wordlist_crack(file_path, wordlists, test_function, window):
    try:
        for wl_path in wordlists:
            with open(wl_path, "r", encoding="utf-8", errors="ignore") as wl:
                passwords = wl.readlines()
                total = len(passwords)

                for i, line in enumerate(passwords, start=1):
                    password = line.strip()
                    if not password:
                        continue

                    window["-PROG-"].update(int((i / total) * 1000))
                    window.refresh()
                    time.sleep(0.002)

                    if test_function(file_path, password):
                        return password, True

                    event, _ = window.read(timeout=1)
                    if event in ("-CANCEL-", sg.WINDOW_CLOSED):
                        return None, False

        return None, False

    except:
        return None, False


# -------------------------------------------------------
# MAIN FUNCTION
# -------------------------------------------------------
def method_default_wordlist(file_path):

    valid_ext = (".zip", ".7z", ".pdf")
    #THIS PATH NEEDS TO BE CHANGED LATER TO THE ABSOLUTE PATH
    #default_wordlists = ["C:/Users/nourb/OneDrive/Bureau/CyberEng Learning/uniprojects/PY/wordlists/rockyou.txt"]
    default_wordlists = ["C:/Users/ahmed/Desktop/New folder (2)/code/wordlists/rockyou.txt"]

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
        [sg.ProgressBar(1000, orientation="h", size=(40, 20), key="-PROG-", bar_color=("#4CE66F", "#CCCCCC"))],


        [sg.Text("", key="-RESULT-", font=("Arial", 12, "bold"),
                 size=(45, 1), justification="center")],

        [sg.Push(),
         sg.Button("Begin", key="-BEGIN-", size=(8, 1)),
         sg.Button("Cancel", key="-CANCEL-", size=(8, 1))]
    ]

    window = sg.Window(
        "Default wordlist tester",
        layout,
        finalize=True,
        element_padding=(5, 7),
        margins=(10, 10)
    )

    testing = False

    while True:
        event, values = window.read(timeout=10)

        if event in (sg.WINDOW_CLOSED, "-CANCEL-"):
            window.close()
            return None

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

        if event == "-BEGIN-" and not testing:
            testing = True

            window["-STATUS-"].update("Testing...")
            window["-RESULT-"].update("")
            window["-CHANGE-"].update(disabled=True)
            window["-BEGIN-"].update(disabled=True)
            window["-SELECTED-"].update(disabled=True)
            window["-PROG-"].update(0)

            test_function = get_test_function(file_path)

            if not test_function:
                window["-STATUS-"].update("Unsupported file")
                testing = False
                continue

            # 🔒 NEW: check if file is protected
            if not is_file_protected(file_path):
                window["-STATUS-"].update("File is NOT password protected")
                window["-RESULT-"].update(
                    "✔ No password required",
                    text_color="#4CE66F",
                    background_color="#1A331E"
                )
                window["-CHANGE-"].update(disabled=False)
                window["-BEGIN-"].update(disabled=False)
                window["-SELECTED-"].update(disabled=False)
                testing = False
                continue

            password, success = default_wordlist_crack(
                file_path,
                default_wordlists,
                test_function,
                window
            )

            window["-STATUS-"].update("Completed")

            if success:
                window["-RESULT-"].update(
                    f"✔ Password found: {password}",
                    text_color="#4CE66F",
                    background_color="#1A331E"
                )
            else:
                window["-RESULT-"].update(
                    "✘ Password NOT found",
                    text_color="#FF6B6B",
                    background_color="#331A1A"
                )

            window["-CHANGE-"].update(disabled=False)
            window["-BEGIN-"].update(disabled=False)
            window["-SELECTED-"].update(disabled=False)
            testing = False

    window.close()

# -------------------------------------------------------
# test default wordlist service
# -------------------------------------------------------   
#file_path = "C:\\Users\\ahmed\\Desktop\\New folder (2)\\Target\\New folder (4).7z"
#method_default_wordlist(file_path)