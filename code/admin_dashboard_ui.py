import FreeSimpleGUI as sg
import Select_target_file
from admin_logs_viewer import admin_logs_viewer
from manage_users_ui import manage_users_ui

# ========================================================
# ADMIN DASHBOARD WINDOW
# ========================================================
def admin_dashboard(username):
    """
    Admin dashboard interface.

    Behavior:
    - Manage Users  -> Opens popup, dashboard stays open
    - View Logs     -> Opens popup, dashboard stays open
    - Test Passwords-> Closes dashboard and continues workflow
    """

    # Consistent UI theme
    sg.theme("DarkBlue3")

    # -----------------------------
    # Dashboard layout
    # -----------------------------
    layout = [
        [sg.Text("Admin Dashboard", font=("Arial", 16, "bold"), justification="center")],
        [sg.HorizontalSeparator()],

        [sg.Button("Manage Users", size=(30, 2))],
        [sg.Button("Test Passwords", size=(30, 2))],
        [sg.Button("View Logs", size=(30, 2))],
    ]

    # -----------------------------
    # Create window
    # -----------------------------
    window = sg.Window(
        "Admin Dashboard",
        layout,
        element_padding=(10, 10),
        margins=(35, 20),
        finalize=True
    )

    # ====================================================
    # Event loop
    # ====================================================
    while True:
        event, _ = window.read()

        # -----------------------------
        # Exit dashboard
        # -----------------------------
        if event == sg.WINDOW_CLOSED:
            break

        # -----------------------------
        # Manage Users (POPUP)
        # Dashboard stays open
        # -----------------------------
        elif event == "Manage Users":
            manage_users_ui()

        # -----------------------------
        # Test Passwords (FLOW CHANGE)
        # Dashboard closes
        # -----------------------------
        elif event == "Test Passwords":
            window.close()
            Select_target_file.select_valid_file(username)
            return  # stop dashboard execution

        # -----------------------------
        # View Logs (POPUP)
        # Dashboard stays open
        # -----------------------------
        elif event == "View Logs":
            admin_logs_viewer()

    # -----------------------------
    # Cleanup
    # -----------------------------
    window.close()


# ========================================================
# TEST RUN
# ========================================================
if __name__ == "__main__":
    admin_dashboard(username="admin")
