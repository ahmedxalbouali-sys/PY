import FreeSimpleGUI as sg
import Select_target_file

# ========================================================
# ADMIN DASHBOARD WINDOW
# ========================================================
def admin_dashboard(username):
    """
    Admin dashboard interface.

    Options:
    1) Manage Users   -> Placeholder popup (to be implemented)
    2) Test Passwords -> Redirects to file selection/testing UI (same as normal user)
    """

    # Apply a theme for consistent look
    sg.theme("DarkBlue3")

    # -----------------------------
    # Layout of the dashboard window
    # -----------------------------
    layout = [
        # Title
        [sg.Text("Admin Dashboard", font=("Arial", 16, "bold"), justification="center")],
        [sg.HorizontalSeparator()],
        # Action buttons
        [sg.Button("Manage Users", size=(30, 2))],
        [sg.Button("Test Passwords", size=(30, 2))],

    ]

    # Create the window
    window = sg.Window(
        "Admin Dashboard",
        layout,
        element_padding=(10, 10),
        margins=(35, 20),
        finalize=True
    )

    # -----------------------------
    # Event loop
    # -----------------------------
    while True:
        event, values = window.read()

        # Exit on window close or logout
        if event in (sg.WINDOW_CLOSED, "Logout"):
            window.close()
            return

        # -----------------------------
        # Manage Users (placeholder)
        # -----------------------------
        elif event == "Manage Users":
            window.close() 
            from manage_users_ui import manage_users_ui
            manage_users_ui()
            return


        # -----------------------------
        # Test Passwords
        # -----------------------------
        elif event == "Test Passwords":
            window.close()  # Close dashboard
            # Call the file selection function (user-facing UI)
            file_path = Select_target_file.select_valid_file(username)
            # Optionally handle the selected file here
            return

# test the admin dashboard UI
if __name__ == "__main__":
    admin_dashboard(username="admin")
