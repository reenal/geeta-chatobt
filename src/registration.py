import streamlit as st
import bcrypt
from pymongo.mongo_client import MongoClient
from src.registration import *

# MongoDB connection
uri = "mongodb+srv://parth:parth123@cluster0.1ngdui1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri)

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Access the database and collection
db = client["user_database"]
users_collection = db["users"]

# Function to hash passwords
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Function to verify passwords
def verify_password(hashed_password, plain_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

# Registration
def register_user(email, password,name,gender,age):
    hashed_password = hash_password(password)
    user = {
        "email": email,
        "password": hashed_password,
        "name":name,
        'age':age,
        'gender':gender
        
    }
    if users_collection.find_one({"email": email}):
        return "email already exists"
    users_collection.insert_one(user)
    return "User registered successfully"

# Login
def login_user(email, password):
    user = users_collection.find_one({"email": email})
    if user and verify_password(user["password"], password):
        return True
    return False
