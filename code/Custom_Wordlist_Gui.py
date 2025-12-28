import FreeSimpleGUI as sg
import threading
import os

# import your friend's generator
from Creating_custom_word_list import generate_custom_wordlist


def run_generation(user_inputs, output_path, window):
    try:
        generate_custom_wordlist(user_inputs, output_file=output_path)
        window.write_event_value(
            "-DONE-",
            f"Wordlist generated successfully!\n\nSaved to:\n{output_path}"
        )
    except Exception as e:
        window.write_event_value("-ERROR-", str(e))


def custom_wordlist_gui():

    sg.theme("DarkBlue3")

    layout = [
        [sg.Text("Custom Wordlist Generator", font=("Arial", 14, "bold"))],

        [sg.Text("Enter known information (one per line):")],
        [
            sg.Multiline(
                key="-INPUTS-",
                size=(45, 8),
                tooltip="Names, dates, locations, usernames, etc."
            )
        ],

        [sg.HorizontalSeparator()],

        [sg.Text("Output file:")],
        [
            sg.Input("custom_generated_wordlist.txt", key="-OUT-", size=(35, 1)),
            sg.FileSaveAs(
                "Browse",
                file_types=(("Text files", "*.txt"),),
                default_extension=".txt"
            )
        ],

        [sg.HorizontalSeparator()],

        [sg.Text("", key="-STATUS-", size=(45, 1), text_color="#4CE66F")],

        [
            sg.Push(),
            sg.Button("Generate", key="-GEN-", size=(10, 1)),
            sg.Button("Exit", size=(8, 1))
        ]
    ]

    window = sg.Window(
        "Wordlist Generator",
        layout,
        finalize=True
    )

    running = False

    while True:
        event, values = window.read(timeout=100)

        if event in (sg.WINDOW_CLOSED, "Exit"):
            break

        if event == "-GEN-" and not running:
            raw_inputs = values["-INPUTS-"].strip()
            output_path = values["-OUT-"].strip()

            if not raw_inputs:
                sg.popup_error("Please enter at least one keyword.")
                continue

            if not output_path:
                sg.popup_error("Please choose an output file.")
                continue

            user_inputs = [
                line.strip()
                for line in raw_inputs.splitlines()
                if line.strip()
            ]

            window["-STATUS-"].update("Generating wordlist...")
            running = True

            threading.Thread(
                target=run_generation,
                args=(user_inputs, output_path, window),
                daemon=True
            ).start()

        if event == "-DONE-":
            running = False
            window["-STATUS-"].update("")
            sg.popup_ok(event)

        if event == "-ERROR-":
            running = False
            window["-STATUS-"].update("")
            sg.popup_error(f"Generation failed:\n{event}")

    window.close()


#if __name__ == "__main__":
 #   custom_wordlist_gui()
