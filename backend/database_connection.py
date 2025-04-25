from pymongo import MongoClient
 
# MongoDB URI - fallback to local if not provided
MONGO_URI = "mongodb://localhost:27017/chatbot_platform"
client = MongoClient(MONGO_URI)
db = client.get_database()
 
# Export collections
college_users_collection = db['college_users']
super_admins_collection = db['super_admins']
KM_documents_collection = db['KM_documents']
KM_URLs_collection = db['KM_URLs']
 