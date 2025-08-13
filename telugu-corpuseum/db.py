from pymongo import MongoClient
import os

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb+srv://Leema:587356.Krelm@cluster0.edot8qp.mongodb.net/TeluguCorpuseum")
client = MongoClient(MONGODB_URI)
db = client["TeluguCorpuseum"]
