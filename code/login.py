import bcrypt
from db.mongo import get_db


def login_user(username: str, password: str):
    """
    Authenticate a user against the MongoDB database.
    PARAMETERS:
    username : str
        The username entered by the user in the login form.
    password : str
        The plain-text password entered by the user.
    RETURNS:
        (True, role)            -> if authentication succeeds
        (False, error_message)  -> if authentication fails
    """

    # 1. Get database connection
    db = get_db()
    users = db.users

    # 2. Search for the user by username
    user = users.find_one({"username": username})
    # the user does not exist
    if not user:
        return False, "User not found"

    # 3. Extract the stored hashed password
    stored_hash = user["password"]

    # 4. Verify the provided password
    if bcrypt.checkpw(password.encode("utf-8"), stored_hash):
        # Authentication successful Return True and role 
        return True, user["role"]
    
    # Authentication failed
    return False, "Invalid password"

# Example usage

# Correct login
#success, result = login_user("admin1", "admin123")
#print(success, result)

# Wrong password
#success, result = login_user("admin1", "wrongpass")
#print(success, result)

# Unknown user
#success, result = login_user("unknown", "1234")
#print(success, result)