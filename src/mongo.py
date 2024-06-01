from pymongo.mongo_client import MongoClient
import bcrypt
from src.registration import *
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection
mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri)

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Access the database and collection
db = client["user_database"]
users_collection = db["users"]


db = client["chat_with_gita_db"]  # Database name
collection = db["questions_responses"]  # Collection name


def store_in_mongodb(question, response):
    document = {
        "question": question,
        "response": response
    }
    collection.insert_one(document)