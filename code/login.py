import bcrypt
from db.mongo import get_db


def login_user(username: str, password: str):
    """
    Verify login credentials.
    Returns:
        (True, role) if success
        (False, error_message) if failure
    """
    db = get_db()
    users = db.users

    user = users.find_one({"username": username})

    if not user:
        return False, "User not found"

    stored_hash = user["password"]

    # Check password
    if bcrypt.checkpw(password.encode(), stored_hash):
        return True, user["role"]

    return False, "Invalid password"

# Correct login
success, result = login_user("admin1", "admin123")
print(success, result)

# Wrong password
success, result = login_user("admin1", "wrongpass")
print(success, result)

# Unknown user
success, result = login_user("unknown", "1234")
print(success, result)