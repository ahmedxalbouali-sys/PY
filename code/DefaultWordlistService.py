import FreeSimpleGUI as sg
import time
import os
import threading

from testpass import (
    test_zip, test_7z, test_pdf,
    is_zip_protected, is_7z_protected, is_pdf_protected
)


from word_list_temporary_files import split_wordlist_into_temp_files


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
# Wordlist selection popup (UNCHANGED)
# -------------------------------------------------------
def select_wordlist_popup(current_wordlists):

    rockyou_path = "H:/CyberEng Learning/uniprojects/PY/wordlists/rockyou.txt"
    crackstation_path = "H:/CyberEng Learning/uniprojects/PY/wordlists/crackstation.txt"

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
# MULTI-THREADED WORDLIST CRACK (SAFE MERGE)
# -------------------------------------------------------
def default_wordlist_crack(file_path, wordlists, test_function, window, thread_limit=4):
    try:
        for wl_path in wordlists:

            temp_lists = split_wordlist_into_temp_files(
                wl_path, num_temp_files=thread_limit
            )

            stop_flag = threading.Event()
            result = {"password": None}

            total = sum(
                sum(1 for _ in open(p, "r", encoding="utf-8", errors="ignore"))
                for p in temp_lists
            )

            tested = 0

            # ----------------------------
            # worker thread
            # ----------------------------
            def worker(temp_file):
                with open(temp_file, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        if stop_flag.is_set():
                            return

                        password = line.strip()
                        if not password:
                            continue

                        # DEBUG proof thread is running
                        print(f"[{threading.current_thread().name}] {password}")

                        if test_function(file_path, password):
                            result["password"] = password
                            stop_flag.set()
                            window.write_event_value("-FOUND-", password)
                            return

                        window.write_event_value("-PROGRESS-", 1)

            # start threads
            for temp_file in temp_lists:
                threading.Thread(
                    target=worker,
                    args=(temp_file,),
                    daemon=True
                ).start()

            # ----------------------------
            # GUI-controlled wait loop
            # ----------------------------
            while not stop_flag.is_set() and tested < total:
                event, value = window.read(timeout=50)

                if event in (sg.WINDOW_CLOSED, "-CANCEL-"):
                    stop_flag.set()
                    return None, False

                if event == "-PROGRESS-":
                    tested += 1
                    window["-PROG-"].update(int((tested / total) * 1000))

                if event == "-FOUND-":
                    stop_flag.set()
                    return value, True

            # cleanup temp files
            for temp in temp_lists:
                try:
                    os.remove(temp)
                except:
                    pass

        return None, False

    except Exception as e:
        print("ERROR:", e)
        return None, False


# -------------------------------------------------------
# MAIN FUNCTION (UI UNCHANGED)
# -------------------------------------------------------
def method_default_wordlist(file_path):

    valid_ext = (".zip", ".7z", ".pdf")
    default_wordlists = ["H:/CyberEng Learning/uniprojects/PY/wordlists/rockyou.txt"]

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
        [sg.ProgressBar(1000, orientation="h", size=(40, 20),
                        key="-PROG-", bar_color=("#4CE66F", "#CCCCCC"))],
        [sg.Text("", key="-RESULT-", font=("Arial", 12, "bold"),
                 size=(45, 1), justification="center")],
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

        if event == "-BEGIN-" and not testing:
            testing = True

            window["-STATUS-"].update("Testing...")
            window["-RESULT-"].update("")
            window["-PROG-"].update(0)

            test_function = get_test_function(file_path)

            if not test_function:
                testing = False
                continue

            if not is_file_protected(file_path):
                window["-RESULT-"].update("✔ No password required", text_color="#4CE66F")
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
                window["-RESULT-"].update(
                    f"✔ Password found: {password}",
                    text_color="#4CE66F"
                )
            else:
                window["-RESULT-"].update(
                    "✘ Password NOT found",
                    text_color="#FF6B6B"
                )

            testing = False

    window.close()
