import FreeSimpleGUI as sg
import Select_target_file


# --------------------------------------------------------
# ADMIN DASHBOARD WINDOW
# --------------------------------------------------------
def admin_dashboard():
    """
    Displays the admin dashboard interface.

    The admin has two available actions:
    1) Manage Users   -> Placeholder page (not implemented yet)
    2) Test Passwords -> Redirects to the same file selection flow as normal users
    """

    # Apply a consistent application theme
    sg.theme("DarkBlue3")

    # Define the dashboard layout
    layout = [
        # Title
        [sg.Text("Admin Dashboard", font=("Arial", 14, "bold"), justification="center")],

        # Visual separation
        [sg.HorizontalSeparator()],

        # Instruction text
        [sg.Text("Choose an action:", font=("Arial", 12))],

        # Admin actions
        [sg.Button("Manage Users", size=(30, 2))],
        [sg.Button("Test Passwords", size=(30, 2))],
    ]

    # Create the dashboard window
    window = sg.Window(
        "Admin Dashboard",
        layout,
        element_padding=(10, 10),
        margins=(30, 20),
        finalize=True
    )

    # Event loop: waits for admin interaction
    while True:
        event, values = window.read()

        # Handle window close (X button)
        if event in (sg.WINDOW_CLOSED,):
            break

        # Admin chooses to manage users (feature not ready yet)
        elif event == "Manage Users":
            sg.popup(
                "Manage Users page is not yet implemented.",
                title="Coming Soon"
            )

        # Admin chooses to test passwords
        elif event == "Test Passwords":
            window.close()
            file_path = Select_target_file.select_valid_file()
            break

    window.close()



# TEST THE ADMIN DASHBOARD
    admin_dashboard()
