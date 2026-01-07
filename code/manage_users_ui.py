import FreeSimpleGUI as sg
import bcrypt

# MongoDB connection helper
from db.mongo import get_db

# User creation logic (registration)
from register import create_user


# --------------------------------------------------------
# MANAGE USERS WINDOW
# --------------------------------------------------------
def manage_users_ui():
    """
    Graphical admin interface to manage application users.

    FEATURES:
    - Display users from MongoDB
    - Register new users
    - Edit existing users (username, role, optional password)
    - Delete users with confirmation
    """

    # Set GUI theme
    sg.theme("DarkBlue3")

    # ----------------------------------------------------
    # HELPER FUNCTION: LOAD USERS FROM DATABASE
    # ----------------------------------------------------
    def load_users():
        """
        Fetch all users from MongoDB and format them
        for display inside the Listbox.
        """
        db = get_db()

        # Only fetch username and role (hide _id)
        users = db.users.find({}, {"_id": 0, "username": 1, "role": 1})

        # Convert DB records to display strings
        return [f"{u['username']} ({u['role']})" for u in users]

    # ----------------------------------------------------
    # INITIAL USER LOAD
    # ----------------------------------------------------
    users_list = load_users()

    # ----------------------------------------------------
    # WINDOW LAYOUT
    # ----------------------------------------------------
    layout = [
        [sg.Text("Manage Users", font=("Arial", 14, "bold"))],
        [sg.HorizontalSeparator()],

        # Listbox showing all users
        [sg.Listbox(
            values=users_list,
            size=(40, 10),
            key="-USER_LIST-",
            enable_events=True
        )],

        [sg.HorizontalSeparator()],

        # Action buttons
        [
            sg.Button("Register New User"),
            sg.Button("Edit Selected User"),
            sg.Button("Delete Selected User"),
        ]
    ]

    # Create the main window
    window = sg.Window(
        "Manage Users",
        layout,
        finalize=True,
        element_padding=(8, 8),
        margins=(20, 20)
    )

    # ----------------------------------------------------
    # MAIN EVENT LOOP
    # ----------------------------------------------------
    while True:
        event, values = window.read(timeout=100)

        # -----------------------------
        # Exit application
        # -----------------------------
        if event == sg.WINDOW_CLOSED:
            window.close()
            return

        # =================================================
        # REGISTER NEW USER
        # =================================================
        if event == "Register New User":

            # Registration form layout
            reg_layout = [
                [sg.Text("Username"), sg.Input(key="-R_USER-")],
                [sg.Text("Password"), sg.Input(password_char="*", key="-R_PASS-")],
                [sg.Text("Role"),
                 sg.Combo(["user", "admin"], default_value="user", key="-R_ROLE-")],
                [sg.Button("Create"), sg.Button("Cancel")]
            ]

            # Modal window blocks interaction with main window
            reg_win = sg.Window("Register User", reg_layout, modal=True)

            while True:
                ev, vals = reg_win.read()

                # Close or cancel registration
                if ev in (sg.WINDOW_CLOSED, "Cancel"):
                    break

                # Attempt to create user
                if ev == "Create":
                    success, msg = create_user(
                        vals["-R_USER-"],
                        vals["-R_PASS-"],
                        vals["-R_ROLE-"]
                    )

                    # Show success or error message
                    sg.popup(msg)

                    if success:
                        break

            reg_win.close()

            # Refresh user list after registration
            window["-USER_LIST-"].update(load_users())

        # =================================================
        # EDIT SELECTED USER
        # =================================================
        if event == "Edit Selected User":

            # Ensure a user is selected
            if not values["-USER_LIST-"]:
                sg.popup("Please select a user first.")
                continue

            # Extract username from display string
            selected = values["-USER_LIST-"][0]
            old_username = selected.split(" ")[0]

            db = get_db()
            user = db.users.find_one({"username": old_username})

            # User may have been deleted externally
            if not user:
                sg.popup_error("User no longer exists.")
                window["-USER_LIST-"].update(load_users())
                continue

            # Edit form layout
            edit_layout = [
                [sg.Text("New Username"),
                 sg.Input(user["username"], key="-E_USER-")],
                [sg.Text("New Password"),
                 sg.Input(password_char="*", key="-E_PASS-")],
                [sg.Text("Role"),
                 sg.Combo(["user", "admin"],
                          default_value=user["role"],
                          key="-E_ROLE-")],
                [sg.Button("Update"), sg.Button("Cancel")]
            ]

            edit_win = sg.Window("Edit User", edit_layout, modal=True)

            while True:
                ev, vals = edit_win.read()

                if ev in (sg.WINDOW_CLOSED, "Cancel"):
                    break

                if ev == "Update":

                    # Username must not be empty
                    if not vals["-E_USER-"].strip():
                        sg.popup_error("Username cannot be empty.")
                        continue

                    # Data to update
                    update_data = {
                        "username": vals["-E_USER-"].strip(),
                        "role": vals["-E_ROLE-"]
                    }

                    # Only hash and update password if provided
                    if vals["-E_PASS-"]:
                        update_data["password"] = bcrypt.hashpw(
                            vals["-E_PASS-"].encode("utf-8"),
                            bcrypt.gensalt()
                        )

                    # Apply update in MongoDB
                    db.users.update_one(
                        {"username": old_username},
                        {"$set": update_data}
                    )

                    sg.popup("User updated successfully.")
                    break

            edit_win.close()

            # Refresh list after update
            window["-USER_LIST-"].update(load_users())

        # =================================================
        # DELETE SELECTED USER
        # =================================================
        if event == "Delete Selected User":

            # Ensure a user is selected
            if not values["-USER_LIST-"]:
                sg.popup("Please select a user first.")
                continue

            selected = values["-USER_LIST-"][0]
            username = selected.split(" ")[0]

            # Confirmation dialog
            confirm = sg.popup_yes_no(
                f"Are you sure you want to delete user:\n\n{username} ?",
                title="Confirm Delete"
            )

            if confirm == "Yes":
                db = get_db()
                db.users.delete_one({"username": username})

                sg.popup("User deleted successfully.")

                # Refresh list after deletion
                window["-USER_LIST-"].update(load_users())

    window.close()


# --------------------------------------------------------
# TEST RUN (direct execution)
# --------------------------------------------------------
if __name__ == "__main__":
    manage_users_ui()
