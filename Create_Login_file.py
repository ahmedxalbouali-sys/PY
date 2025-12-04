import hashlib
import json

def create_credentials_file(username, password, filename="credentials.json"):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    data = {
        "username": username,
        "password_hash": hashed_password
    }

    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

    print(f"Credentials saved to {filename}")

# Example usage:
create_credentials_file("admin", "admin123")
