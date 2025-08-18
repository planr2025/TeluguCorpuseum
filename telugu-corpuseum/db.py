from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()  # looks in same folder as db.py

MONGODB_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGODB_URI)
db = client["TeluguCorpuseum"]
