from motor.motor_asyncio import AsyncIOMotorClient
from core.config import MONGO_URL, DB_NAME

# If this file defines 'db', it would likely import:
# from motor.motor_asyncio import AsyncIOMotorClient
# from pymongo import MongoClient # if used for some specific legacy part
# import os
# from dotenv import load_dotenv
# # ... and then define db = AsyncIOMotorClient(...)[DB_NAME]

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]
