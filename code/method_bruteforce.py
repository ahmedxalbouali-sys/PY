import FreeSimpleGUI as sg
import threading

from bruteforce_engine import (
    brute_force_attack,
    DEFAULT_CHARSET,
    DEFAULT_MIN_LEN,
    DEFAULT_MAX_LEN,
    DEFAULT_THREADS
)

# Centralized logging service
from logging_service import add_test_log


# ==========================================================
# ADVANCED SETTINGS POPUP
# ==========================================================
def advanced_settings_popup(min_len, max_len, threads, mask):
    """
    Modal popup used ONLY to configure brute-force parameters.

    Returns:
        (min_len, max_len, threads, mask_string)
        or None if the user cancels.
    """

    layout = [
        [sg.Text("Advanced Bruteforce Settings", font=("Arial", 13, "bold"))],
        [sg.HorizontalSeparator()],

        [sg.Text("Minimum length:"), sg.Input(min_len, size=(6, 1), key="-MIN-")],
        [sg.Text("Maximum length:"), sg.Input(max_len, size=(6, 1), key="-MAX-")],
        [sg.Text("Threads:"), sg.Input(threads, size=(6, 1), key="-THREADS-")],

        [sg.HorizontalSeparator()],
        [sg.Text("Mask pattern (use | per position):")],
        [sg.Input(mask, size=(45, 1), key="-MASK-")],
        [sg.Text("Example: a|bc||9", font=("Arial", 9, "italic"))],

        [sg.Push(), sg.Button("Apply"), sg.Button("Cancel")]
    ]

    window = sg.Window("Advanced Settings", layout, modal=True)

    while True:
        event, values = window.read()

        if event in (sg.WINDOW_CLOSED, "Cancel"):
            window.close()
            return None

        if event == "Apply":
            try:
                result = (
                    int(values["-MIN-"]),
                    int(values["-MAX-"]),
                    int(values["-THREADS-"]),
                    values["-MASK-"]
                )
                window.close()
                return result
            except ValueError:
                sg.popup_error("Invalid numeric input")


# ==========================================================
# MAIN APPLICATION WINDOW
# ==========================================================
def method_bruteforce(file_path, username):

    sg.theme("DarkBlue3")

    # --------------------------------------------------
    # Runtime configuration (modifiable via popup)
    # --------------------------------------------------
    min_len = DEFAULT_MIN_LEN
    max_len = DEFAULT_MAX_LEN
    threads = DEFAULT_THREADS
    mask_string = ""

    # --------------------------------------------------
    # Shared state between GUI thread and engine thread
    # --------------------------------------------------
    tested = 0
    total = 1
    result = None
    running = False

    tested_lock = threading.Lock()
    stop_flag = threading.Event()

    # --------------------------------------------------
    # GUI layout
    # --------------------------------------------------
    layout = [
        [sg.Text("Target file:", font=("Arial", 11, "bold"))],
        [sg.Text(file_path, size=(70, 1), key="-FILE-")],
        [sg.Button("Change target file")],

        [sg.HorizontalSeparator()],

        [sg.Text("Status:"), sg.Text("Idle", key="-STATUS-")],
        [sg.ProgressBar(100, size=(45, 20), key="-PROG-")],
        [sg.Text("", key="-RESULT-", font=("Arial", 12, "bold"))],

        [
            sg.Button("Advanced Settings"),
            sg.Push(),
            sg.Button("Execute"),
            sg.Button("Cancel")
        ]
    ]

    window = sg.Window("Bruteforce Method", layout, finalize=True)

    # ======================================================
    # PROGRESS CALLBACK (ENGINE → GUI STATE)
    # ======================================================
    def progress_cb(done, total_count):
        """
        Called by the brute-force engine.
        Must be extremely fast and non-blocking.
        """
        nonlocal tested, total
        with tested_lock:
            tested = done
            total = total_count

    # ======================================================
    # ENGINE THREAD
    # ======================================================
    def run_engine():
        """
        Runs the brute-force engine in a background thread.
        The GUI thread never blocks on this.
        """
        nonlocal result, running

        result = brute_force_attack(
            file_path=file_path,
            min_len=min_len,
            max_len=max_len,
            charset=DEFAULT_CHARSET,
            table_string=mask_string,
            thread_count=threads,
            progress_callback=progress_cb,
            stop_flag=stop_flag
        )

        running = False

    # ======================================================
    # MAIN GUI EVENT LOOP
    # ======================================================
    while True:
        event, _ = window.read(timeout=100)

        # --------------------------
        # Exit / cancel
        # --------------------------
        if event in (sg.WINDOW_CLOSED, "Cancel"):
            stop_flag.set()
            break

        # --------------------------
        # Change target file
        # --------------------------
        if event == "Change target file" and not running:
            new_file = sg.popup_get_file("Select file")
            if new_file:
                file_path = new_file
                window["-FILE-"].update(file_path)

        # --------------------------
        # Advanced settings
        # --------------------------
        if event == "Advanced Settings" and not running:
            res = advanced_settings_popup(min_len, max_len, threads, mask_string)
            if res:
                min_len, max_len, threads, mask_string = res

        # --------------------------
        # Start brute-force attack
        # --------------------------
        if event == "Execute" and not running:
            add_test_log(
                username=username,
                method="bruteforce",
                target_file=file_path
            )

            tested = 0
            total = 1
            result = None
            running = True
            stop_flag.clear()

            window["-STATUS-"].update("Running...")
            window["-RESULT-"].update("")

            threading.Thread(target=run_engine, daemon=True).start()

        # --------------------------
        # Live progress update
        # --------------------------
        if running:
            with tested_lock:
                percent = int((tested / max(total, 1)) * 100)

            window["-PROG-"].update(percent)
            window["-STATUS-"].update(f"Testing {tested} / {total}")

        # --------------------------
        # Final result display
        # --------------------------
        else:
            if result:
                window["-RESULT-"].update(
                    f"✔ Password FOUND: {result}",
                    text_color="limegreen"
                )
            elif tested > 0:
                window["-RESULT-"].update(
                    "✘ Password NOT found",
                    text_color="red"
                )

    window.close()


# =================================================
# TEST RUN
# =================================================
if __name__ == "__main__":
    method_bruteforce(
        r"C:/Users/ahmed/Desktop/New folder (2)/Target/Rapport_23_24_VF_protected.pdf",
        username="admin"
    )
