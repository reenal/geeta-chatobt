from pymongo.mongo_client import MongoClient
import bcrypt
from src.registration import *
import os
from dotenv import load_dotenv
from src.logger import *

load_dotenv()

# MongoDB connection
mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri)

try:
    logging.info('Connecting to mongodb server')
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
    logging.info('connected successfully to mogodb server')
except Exception as e:
    logging.error('error while connecting mogodb')
    print(e)



db = client["chat_with_gita_db"]  # Database name
collection = db["questions_responses"]  # Collection name


def store_in_mongodb(question, response):
    document = {
        "question": question,
        "response": response
    }
    collection.insert_one(document)
    
