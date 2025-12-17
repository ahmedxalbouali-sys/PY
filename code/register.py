import bcrypt
from db.mongo import get_db


def create_user(username: str, password: str, role: str = "user"):
    """
    Create a user or admin in MongoDB
    """
    db = get_db()
    users = db.users

    # Check if user already exists
    if users.find_one({"username": username}):
        return False, "User already exists"

    # Hash password
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    user_doc = {
        "username": username,
        "password": hashed_pw,
        "role": role  # "user" or "admin"
    }

    users.insert_one(user_doc)
    return True, "User created"
# Example usage
 
#success, message = create_user("user1", "testtest", role="user")
#print(message)
