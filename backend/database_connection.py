from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load variables from .env file
load_dotenv()

# Get Mongo URI from env
MONGO_URI = os.getenv("MONGO_URI")

# Connect to MongoDB Atlas
client = MongoClient(MONGO_URI)

# Choose your database name (you already specified it in the URI)
db = client.get_database("chatbot_platform")

# Export collections
college_users_collection = db['college_users']
super_admins_collection = db['super_admins']
KM_documents_collection = db['KM_documents']
KM_URLs_collection = db['KM_URLs']
