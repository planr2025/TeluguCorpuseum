import os, sys, hashlib

# Go 2 levels up: TeluguCorpuseum → telugu-corpuseum
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from db import db  # now should work
from db import db  # now it should work
# Reference to MongoDB users collection
users_collection = db["users"]

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def save_user(username, password):
    """Save a new user to MongoDB."""
    hashed = hash_password(password)
    users_collection.insert_one({
        "username": username,
        "password": hashed
    })

def validate_user(username, password):
    """Check if username/password match in MongoDB."""
    hashed = hash_password(password)
    user = users_collection.find_one({"username": username, "password": hashed})
    return user is not None

def user_exists(username):
    """Check if username already exists in MongoDB."""
    return users_collection.find_one({"username": username}) is not None
