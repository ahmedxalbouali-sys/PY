import FreeSimpleGUI as sg
import bcrypt
from db.mongo import get_db
from register import create_user


# --------------------------------------------------------
# MANAGE USERS WINDOW
# --------------------------------------------------------
def manage_users_ui():
    """
    Admin UI to manage users.

    FEATURES:
    - Load users from MongoDB
    - Select a user from list
    - Register new user (popup)
    - Edit user (username, role, password)
    - Delete user (confirmation popup)
    """

    sg.theme("DarkBlue3")

    # ----------------------------------------------------
    # HELPER: LOAD USERS FROM DATABASE
    # ----------------------------------------------------
    def load_users():
        db = get_db()
        users = db.users.find({}, {"_id": 0, "username": 1, "role": 1})
        return [f"{u['username']} ({u['role']})" for u in users]

    # ----------------------------------------------------
    # INITIAL DATA LOAD
    # ----------------------------------------------------
    users_list = load_users()

    # ----------------------------------------------------
    # LAYOUT
    # ----------------------------------------------------
    layout = [
        [sg.Text("Manage Users", font=("Arial", 14, "bold"))],
        [sg.HorizontalSeparator()],

        [sg.Listbox(
            values=users_list,
            size=(40, 10),
            key="-USER_LIST-",
            enable_events=True
        )],

        [sg.HorizontalSeparator()],

        [
            sg.Button("Register New User"),
            sg.Button("Edit Selected User"),
            sg.Button("Delete Selected User"),
        ],

        [sg.HorizontalSeparator()],
        [sg.Button("Back")]
    ]

    window = sg.Window(
        "Manage Users",
        layout,
        finalize=True,
        element_padding=(8, 8),
        margins=(20, 20)
    )

    # ----------------------------------------------------
    # EVENT LOOP
    # ----------------------------------------------------
    while True:
        event, values = window.read(timeout=100)

        # Exit
        if event in (sg.WINDOW_CLOSED, "Back"):
            window.close()
            return

        # ------------------------------------------------
        # REGISTER USER POPUP
        # ------------------------------------------------
        elif event == "Register New User":
            reg_layout = [
                [sg.Text("Username"), sg.Input(key="-R_USER-")],
                [sg.Text("Password"), sg.Input(password_char="*", key="-R_PASS-")],
                [sg.Text("Role"), sg.Combo(["user", "admin"], default_value="user", key="-R_ROLE-")],
                [sg.Button("Create"), sg.Button("Cancel")]
            ]

            reg_win = sg.Window("Register User", reg_layout, modal=True)

            while True:
                ev, vals = reg_win.read()
                if ev in (sg.WINDOW_CLOSED, "Cancel"):
                    break

                if ev == "Create":
                    success, msg = create_user(
                        vals["-R_USER-"],
                        vals["-R_PASS-"],
                        vals["-R_ROLE-"]
                    )
                    sg.popup(msg)
                    if success:
                        break

            reg_win.close()
            window["-USER_LIST-"].update(load_users())

        # ------------------------------------------------
        # EDIT USER POPUP
        # ------------------------------------------------
        elif event == "Edit Selected User":
            if not values["-USER_LIST-"]:
                sg.popup("Please select a user first.")
                continue

            selected = values["-USER_LIST-"][0]
            old_username = selected.split(" ")[0]

            edit_layout = [
                [sg.Text("New Username"), sg.Input(old_username, key="-E_USER-")],
                [sg.Text("New Password"), sg.Input(password_char="*", key="-E_PASS-")],
                [sg.Text("Role"), sg.Combo(["user", "admin"], key="-E_ROLE-")],
                [sg.Button("Update"), sg.Button("Cancel")]
            ]

            edit_win = sg.Window("Edit User", edit_layout, modal=True)

            while True:
                ev, vals = edit_win.read()
                if ev in (sg.WINDOW_CLOSED, "Cancel"):
                    break

                if ev == "Update":
                    db = get_db()
                    update_data = {
                        "username": vals["-E_USER-"],
                        "role": vals["-E_ROLE-"]
                    }

                    if vals["-E_PASS-"]:
                        update_data["password"] = bcrypt.hashpw(
                            vals["-E_PASS-"].encode("utf-8"),
                            bcrypt.gensalt()
                        )

                    db.users.update_one(
                        {"username": old_username},
                        {"$set": update_data}
                    )

                    sg.popup("User updated successfully.")
                    break

            edit_win.close()
            window["-USER_LIST-"].update(load_users())

        # ------------------------------------------------
        # DELETE USER CONFIRMATION
        # ------------------------------------------------
        elif event == "Delete Selected User":
            if not values["-USER_LIST-"]:
                sg.popup("Please select a user first.")
                continue

            selected = values["-USER_LIST-"][0]
            username = selected.split(" ")[0]

            confirm = sg.popup_yes_no(
                f"Are you sure you want to delete user:\n\n{username} ?",
                title="Confirm Delete"
            )

            if confirm == "Yes":
                db = get_db()
                db.users.delete_one({"username": username})
                sg.popup("User deleted successfully.")
                window["-USER_LIST-"].update(load_users())

    window.close()


# --------------------------------------------------------
# TEST RUN
# --------------------------------------------------------
if __name__ == "__main__":
    manage_users_ui()