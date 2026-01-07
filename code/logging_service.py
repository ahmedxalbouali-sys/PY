"""
logging_service.py
==================

Centralized logging module for the password testing tool.

This module is responsible for:
- Writing logs when a user ATTEMPTS a test
- Providing a simple API usable by all testing methods

Each log entry stores:
- username
- timestamp
- testing method
- target file path
"""

from datetime import datetime
from db.mongo import get_db


# -------------------------------------------------------
# INTERNAL: get logs collection
# -------------------------------------------------------
def _get_logs_collection():
    """
    Get the MongoDB 'logs' collection.

    RETURNS:
        collection : pymongo.collection.Collection
    """
    db = get_db()
    return db["logs"]


# -------------------------------------------------------
# PUBLIC: add a log entry
# -------------------------------------------------------
def add_test_log(username, method, target_file):
    if not username or not method or not target_file:
        # We silently ignore invalid logs to avoid crashing tests
        return

    log_entry = {
        "username": username,
        "timestamp": datetime.utcnow(),  # UTC for consistency
        "method": method,
        "target_file": target_file
    }

    try:
        collection = _get_logs_collection()
        collection.insert_one(log_entry)
    except Exception as e:
        # Logging must NEVER crash the app
        print("LOGGING ERROR:", e)
