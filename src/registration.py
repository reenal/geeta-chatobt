import streamlit as st
import bcrypt
from pymongo.mongo_client import MongoClient
from src.registration import *

from dotenv import load_dotenv
from src.logger import *

load_dotenv()

# MongoDB connection
mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri)

# Access the database and collection
db = client["user_database"]
users_collection = db["users"]

# Function to hash passwords
def hash_password(password):
    try:
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        logging.info("Password hashed successfully.")
        return hashed
    except Exception as e:
        logging.error(f"Error hashing password: {e}")
        raise

# Function to verify passwords
def verify_password(hashed_password, plain_password):
    try:
        result = bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)
        logging.info("Password verified successfully.")
        return result
    except Exception as e:
        logging.error(f"Error verifying password: {e}")
        raise

# Registration
def register_user(email, password, name, age, gender):
    try:
        if users_collection.find_one({"email": email}):
            logging.warning("Attempted to register with an existing email: %s", email)
            return "Email already exists"
        
        hashed_password = hash_password(password)
        user = {
            "email": email,
            "password": hashed_password,
            "name": name,
            "age": age,
            "gender": gender
        }
        users_collection.insert_one(user)
        logging.info("User registered successfully: %s", email)
        return "User registered successfully"
    except Exception as e:
        logging.error(f"Error registering user: {e}")
        return "Registration failed due to an internal error"

# Login
def login_user(email, password):
    try:
        user = users_collection.find_one({"email": email})
        if user and verify_password(user["password"], password):
            logging.info("User logged in successfully: %s", email)
            return user
        logging.warning("Failed login attempt for email: %s", email)
        return False
    except Exception as e:
        logging.error(f"Error logging in user: {e}")
        return False
    return user

def find_info(email):
    document = {
        'email':email
    }
    result = users_collection.find_one(document)
    print(result)
    
    return result