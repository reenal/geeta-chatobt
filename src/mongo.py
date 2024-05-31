from pymongo.mongo_client import MongoClient
import bcrypt

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