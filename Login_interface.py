import FreeSimpleGUI as sg
import json
import hashlib

# --- Load credentials ---
def load_credentials(filename="credentials.json"):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        sg.popup_error("Credentials file not found!")
        return None

# --- Hash helper ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# --- Temporary dashboard (after login) ---
def temporary_dashboard(username):
    layout = [
        [sg.Text(f"Welcome, {username}! (temporary dashboard)")],
        [sg.Button("Logout")]
    ]
    window = sg.Window("Dashboard", layout, finalize=True)
    while True:
        event, _ = window.read()
        if event in (sg.WIN_CLOSED, "Logout"):
            break
    window.close()

# --- Login interface function ---
def run_login_interface(credentials_file="credentials.json"):
    creds = load_credentials(credentials_file)
    if creds is None:
        return False

    layout = [
        [sg.Text("Username:"), sg.Input(key="-USER-")],
        [sg.Text("Password:"), sg.Input(key="-PASS-", password_char="*")],
        [sg.Button("Login"), sg.Button("Exit")]
    ]

    window = sg.Window("Login", layout, finalize=True)

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "Exit"):
            window.close()
            return False

        if event == "Login":
            user_input = values["-USER-"]
            pass_input = values["-PASS-"]
            entered_hash = hash_password(pass_input)

            if user_input == creds.get("username") and entered_hash == creds.get("password_hash"):
                sg.popup("Login successful!")
                window.close()
                temporary_dashboard(user_input)
                return True
            else:
                sg.popup_error("Invalid username or password")

# --- Example usage ---
run_login_interface()
