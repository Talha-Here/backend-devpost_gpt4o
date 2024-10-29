from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# Retrieve the MongoDB URI from .env file
mongo_uri = os.getenv("MONGO_URI")

# Pass the URI string directly to MongoClient
client = MongoClient(mongo_uri)

# Test the connection by listing databases
print(client.list_database_names())
