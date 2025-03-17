import pymongo
import os
from dotenv import load_dotenv
load_dotenv()
PORT = int(os.environ["port"])
MONGO_URL = os.environ["mongo_url"]
# MongoDB connection
client = pymongo.MongoClient(MONGO_URL, PORT)
db = client['ddConnect']
time_data_collection = db['time_data']
users_collection = db['users']

