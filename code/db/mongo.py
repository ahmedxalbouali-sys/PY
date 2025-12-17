from pymongo import MongoClient

# MongoDB connection settings
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "password_tool"


def get_db():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    return db
#db = get_db()
#print("Connected to database:", db.name)