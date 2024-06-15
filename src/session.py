from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

# MongoDB connection
mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri)


# MongoDB connection string

DATABASE_NAME = 'user_data'
COLLECTION_NAME = 'user_session'

def create_user_session(username, login_time):
    client = MongoClient(mongo_uri)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]
    
    session = {
        "username": username,
        "login_time": login_time,
        "logout_time": None,
        "actions": []
    }
    
    result = collection.insert_one(session)
    client.close()
    
    print(f"New session created with the following id: {result.inserted_id}")
    return result.inserted_id

def log_action(session_id, action_type, details):
    client = MongoClient(mongo_uri)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]
    
    action = {
        "type": action_type,
        "timestamp": datetime.now(),
        "details": details
    }
    
    collection.update_one(
        { "_id": ObjectId(session_id) },
        { "$push": { "actions": action } }
    )
    
    client.close()
    
    print(f"Action logged for session id: {session_id}")

def end_user_session(session_id, logout_time):
    client = MongoClient(mongo_uri)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]
    
    collection.update_one(
        { "_id": ObjectId(session_id) },
        { "$set": { "logout_time": logout_time } }
    )
    
    client.close()
    
    print(f"Session ended for session id: {session_id}")


