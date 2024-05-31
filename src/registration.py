import streamlit as st
import bcrypt
from mongo import *


# Function to hash passwords
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Function to verify passwords
def verify_password(hashed_password, plain_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

# Registration
def register_user(username, password):
    hashed_password = hash_password(password)
    user = {
        "username": username,
        "password": hashed_password
    }
    if users_collection.find_one({"username": username}):
        return "Username already exists"
    users_collection.insert_one(user)
    return "User registered successfully"

# Login
def login_user(username, password):
    user = users_collection.find_one({"username": username})
    if user and verify_password(user["password"], password):
        return True
    return False



