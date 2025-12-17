import FreeSimpleGUI as sg
import Select_target_file
from login import login_user
from admin_dashboard import admin_dashboard


def login_window():
    sg.theme("DarkBlue3")

    layout = [
        [sg.Text("Username")],
        [sg.Input(key="-USER-")],

        [sg.Text("Password")],
        [sg.Input(key="-PASS-", password_char="*")],

        [sg.Text("", key="-STATUS-", text_color="red")],

        [sg.Button("Login", size=(10, 1)),
         sg.Button("Exit", size=(10, 1))]
    ]

    window = sg.Window(
        "Login",
        layout,
        element_padding=(5, 8),
        margins=(20, 20)
    )

    while True:
        event, values = window.read()

        if event in (sg.WINDOW_CLOSED, "Exit"):
            break

        if event == "Login":
            username = values["-USER-"].strip()
            password = values["-PASS-"]

            if not username or not password:
                window["-STATUS-"].update("Fill all fields")
                continue

            success, result = login_user(username, password)

            if success:
                window.close()

                # ROLE REDIRECTION
                if result == "admin":
                    admin_dashboard(username)
                else:
                    selected = Select_target_file.select_valid_file()

                break
            else:
                window["-STATUS-"].update(result)

    window.close()
# Uncomment below to run the login window directly
login_window()        