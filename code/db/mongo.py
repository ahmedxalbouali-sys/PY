from pymongo import MongoClient

# URI used to connect to the MongoDB server
MONGO_URI = "mongodb://localhost:27017"

# Name of the database we will use for this project
DB_NAME = "password_tool"


# Function: get_db()
def get_db():
    """
    Connect to MongoDB and return the database instance.
    RETURNS:
    db : Database object
        A MongoDB database instance connected to 'password_tool'
    """

    client = MongoClient(MONGO_URI)

    db = client[DB_NAME]

    return db


# test the connection
#db = get_db()
#print("Connected to database:", db.name)