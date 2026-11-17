import pymongo
from pymongo import MongoClient
from app.config import settings

client = MongoClient(settings.DATABASE_URL)
print("Connected to MongoDB...")

db = client[settings.MONGO_INITDB_DATABASE]
User = db.users
TokenBlacklist = db.token_blacklist

User.create_index([("email", pymongo.ASCENDING)], unique=True)
TokenBlacklist.create_index("expires_at", expireAfterSeconds=0)