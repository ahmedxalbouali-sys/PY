import FreeSimpleGUI as sg



# --------------------------------------------------------
# MANAGE USERS WINDOW (UI ONLY)
# --------------------------------------------------------
def manage_users_ui():
    """
    Display the Manage Users interface for administrators.

    CURRENT STATE:
    - Shows a list of users (dummy data)
    - Allows selecting a user
    - Buttons are placeholders (no backend logic yet)
    - Back button returns to Admin Dashboard

    FUTURE:
    - Users loaded from MongoDB
    - Register / Edit / Delete will be implemented
    """

    sg.theme("DarkBlue3")

    # ----------------------------------------------------
    # TEMPORARY USER DATA (PLACEHOLDER)
    # Will later be replaced by MongoDB data
    # ----------------------------------------------------
    users = [
        "admin (admin)",
        "ahmed (user)",
        "nour (user)",
        "mohamed (user)",
    ]

    # ----------------------------------------------------
    # LAYOUT
    # ----------------------------------------------------
    layout = [
        [sg.Text("Manage Users", font=("Arial", 14, "bold"))],
        [sg.HorizontalSeparator()],

        [sg.Text("Users list:", font=("Arial", 11))],

        [
            sg.Listbox(
                values=users,
                size=(40, 10),
                key="-USER_LIST-",
                enable_events=True
            )
        ],

        [sg.HorizontalSeparator()],

        [
            sg.Button("Register New User", size=(20, 1)),
            sg.Button("Edit Selected User", size=(20, 1)),
            sg.Button("Delete Selected User", size=(20, 1)),
        ],

        [sg.HorizontalSeparator()],

        [
            sg.Push(),
            sg.Button("Back", size=(12, 1))
        ]
    ]

    window = sg.Window(
        "Manage Users",
        layout,
        element_padding=(8, 8),
        margins=(20, 20),
        finalize=True
    )

    # ----------------------------------------------------
    # EVENT LOOP
    # ----------------------------------------------------
    while True:
        event, values = window.read()

        # Close window
        if event in (sg.WINDOW_CLOSED, "Back"):
            window.close()
            #from admin_dashboard_ui import admin_dashboard
            #admin_dashboard()
            return

        # Placeholder actions (no logic yet)
        elif event == "Register New User":
            sg.popup("Register User page not implemented yet.")

        elif event == "Edit Selected User":
            if not values["-USER_LIST-"]:
                sg.popup("Please select a user first.")
            else:
                sg.popup("Edit User page not implemented yet.")

        elif event == "Delete Selected User":
            if not values["-USER_LIST-"]:
                sg.popup("Please select a user first.")
            else:
                sg.popup("Delete User functionality not implemented yet.")


# --------------------------------------------------------
# TEST RUN (OPTIONAL)
# --------------------------------------------------------

manage_users_ui()
