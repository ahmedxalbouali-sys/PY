'''import FreeSimpleGUI as sg
import time
import os

# -------------------------------------------------------
# Temporary fake password tester
# ALWAYS returns: "testtest"
# -------------------------------------------------------
def fake_default_wordlist_crack(target_file, wordlist_path):
    return "testtest"



# -------------------------------------------------------
# MAIN FUNCTION: Default Wordlist Tester Window
# -------------------------------------------------------
def method_default_wordlist2(file_path):

    valid_ext = (".zip", ".7z", ".pdf")
    default_wordlist = "C:\\Users\\ahmed\\Desktop\\New folder (2)\\rockyou.txt"

    sg.theme("DarkBlue3")

    layout = [
        [sg.Text("Selected file:", font=("Arial", 11))],
        [sg.Text(file_path, key="-FILE-", text_color="yellow")],

        [sg.Button("Change file", key="-CHANGE-")],
        [sg.HorizontalSeparator()],

        [sg.Text("Ready", key="-STATUS-", font=("Arial", 11))],
        [sg.ProgressBar(1000, orientation="h", size=(40, 20), key="-PROG-")],

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

        # ---------------- CANCEL closes instantly ----------------
        if event in (sg.WINDOW_CLOSED, "-CANCEL-"):
            window.close()
            return None

        # ---------------- CHANGE FILE ----------------
        if event == "-CHANGE-" and not testing:
            new_file = sg.popup_get_file(
                "Choose file",
                file_types=(("Allowed", "*.zip;*.7z;*.pdf"),)
            )

            if new_file:
                if new_file.lower().endswith(valid_ext):
                    file_path = new_file
                    window["-FILE-"].update(file_path)
                else:
                    sg.popup_error("File must be ZIP / 7z / PDF.")

        # ---------------- BEGIN TESTING ----------------
        if event == "-BEGIN-" and not testing:
            testing = True

            window["-STATUS-"].update("Testing...")
            window["-RESULT-"].update("")
            window["-CHANGE-"].update(disabled=True)
            window["-BEGIN-"].update(disabled=True)

            password_found = False
            found_pass = None

            # Simulated test loop
            for i in range(1, 1001):

                event, _ = window.read(timeout=1)
                if event in ("-CANCEL-", sg.WINDOW_CLOSED):
                    window.close()
                    return None

                window["-PROG-"].update(i)
                time.sleep(0.002)

                # Fake password discovered at 600
                if i == 600:
                    found_pass = fake_default_wordlist_crack(file_path, default_wordlist)
                    password_found = True

                    # Fill progress bar to the end
                    window["-PROG-"].update(1000)

                    break

            # ---------------- AFTER LOOP ----------------
            window["-STATUS-"].update("Completed")

            if password_found:
                window["-RESULT-"].update(
                    f"✔ Password found: {found_pass}",
                    text_color="#4CE66F",            # soft green
                    background_color="#1A331E"       # dark greenish bg
                )
            else:
                window["-RESULT-"].update(
                    "✘ Password NOT found",
                    text_color="#FF6B6B",            # soft red
                    background_color="#331A1A"
                )

            # re-enable buttons
            window["-CHANGE-"].update(disabled=False)
            window["-BEGIN-"].update(disabled=False)

            testing = False

    window.close()

'''

# Example run
#file_path = "C:/Users/ahmed/Desktop/test.zip"
#method_default_wordlist(file_path)
