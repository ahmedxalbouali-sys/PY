import FreeSimpleGUI as sg

# Module responsible for selecting a valid target file (ZIP / 7z / PDF)
import Select_target_file

# Backend authentication logic (checks MongoDB / credentials)
from login import login_user

# Admin dashboard interface
from admin_dashboard import admin_dashboard


def login_window():
    """
    Displays the login window.
    
    - Asks user for username and password
    - Sends credentials to backend for verification
    - Redirects user based on role:
        • admin  -> admin dashboard
        • user   -> Select target file interface
    """

    sg.theme("DarkBlue3")

    # 2. Define window layout
    # Layout is built top → bottom
    layout = [

        # Username label + input field
        [sg.Text("Username")],
        [sg.Input(key="-USER-")],

        # Password label + masked input field
        [sg.Text("Password")],
        [sg.Input(key="-PASS-", password_char="*")],

        # Status message (errors / feedback)
        [sg.Text("", key="-STATUS-", text_color="#FF6B6B", font=("Arial", 11, "bold"))],

# Action buttons 
[
    sg.Push(),
    sg.Button("Login", size=(10, 1)),
    sg.Button("Exit", size=(10, 1)),
    sg.Push()
]

    ]

    # 3. Create the window
    window = sg.Window(
        title="Login",
        layout=layout,
        element_padding=(5, 0),
        margins=(15, 5)
    )

    # 4. Event loop (GUI stays alive)
    while True:
        event, values = window.read()

        # Exit conditions 
        if event in (sg.WINDOW_CLOSED, "Exit"):
            break

        # Login button pressed
        if event == "Login":

            # Retrieve user inputs
            username = values["-USER-"].strip()
            password = values["-PASS-"]

            # empty fields
            if not username or not password:
                window["-STATUS-"].update("Fill all fields")
                continue


            # 5. Authenticate userg
            # login_user returns:
            #   (True, "admin")  -> admin login
            #   (True, "user")   -> normal user
            #   (False, error_message)
            success, result = login_user(username, password)

            # 6. Handle authentication result
            if success:
                # Close login window 
                window.close()
                # Role-based redirection
                if result == "admin":
                    admin_dashboard()
                else:
                    target_file = Select_target_file.select_valid_file()
                break  

            else:
                # Display backend error message
                window["-STATUS-"].update(result)


    window.close()


# Run login window directly 
login_window()
