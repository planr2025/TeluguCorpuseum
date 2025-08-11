import streamlit as st
import hashlib

# Simple file-based user storage (replace with DB in production)
USER_DB = "users.txt"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def save_user(username, password):
    with open(USER_DB, "a") as f:
        f.write(f"{username}:{hash_password(password)}\n")

def validate_user(username, password):
    try:
        with open(USER_DB, "r") as f:
            users = f.readlines()
        hashed = hash_password(password)
        for user in users:
            u, p = user.strip().split(":")
            if u == username and p == hashed:
                return True
        return False
    except FileNotFoundError:
        return False

def user_exists(username):
    try:
        with open(USER_DB, "r") as f:
            users = f.readlines()
        for user in users:
            u, _ = user.strip().split(":")
            if u == username:
                return True
        return False
    except FileNotFoundError:
        return False
