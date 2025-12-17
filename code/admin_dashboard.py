import FreeSimpleGUI as sg


def admin_dashboard():
    layout = [
        [sg.Text(f"Welcome ADMIN: ", font=("Arial", 14))],
        [sg.Button("Logout")]
    ]

    window = sg.Window("Admin Dashboard", layout, margins=(20, 20))

    while True:
        event, _ = window.read()
        if event in (sg.WINDOW_CLOSED, "Logout"):
            break

    window.close()
