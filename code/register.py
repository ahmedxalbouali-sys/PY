import bcrypt
from db.mongo import get_db


def create_user(username: str, password: str, role: str = "user"):
    """
    Creates a new user (or admin) in the MongoDB database.
    PARAMETERS:
    username : str
        The username chosen by the user
    password : str
        The plaintext password (will be hashed before storage)
    role : str (default = "user")
        - "user"  -> normal user
        - "admin" -> administrator
    RETURNS:
    tuple (bool, str)
        - True / False depending on success
        - A human-readable message explaining the result
    """

    # 1. Connect to the MongoDB database
    db = get_db()
    users = db.users

    # 2. Check if the username already exists
    if users.find_one({"username": username}):
        return False, "User already exists"

    # 3. Hash the password securely
    hashed_pw = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    )

    # 4. Create the user document and store it
    user_doc = {
        "username": username,   # login identifier
        "password": hashed_pw,  # hashed password (NOT plaintext)
        "role": role            # "user" or "admin"
    }
    users.insert_one(user_doc)

    # 6. Return success message
    return True, "User created successfully"

# Example usage
#success, message = create_user("user1", "testtest", role="user")
#print(message)
