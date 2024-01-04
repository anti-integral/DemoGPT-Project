import pymongo
from decouple import config

mongoURI = config("MONGOURI")
client = pymongo.MongoClient(mongoURI)
db = client["demogpt"]
UserCollection = db["users"]
userchathistory = db["chat_history"]

# def create(data):
#     data = dict(data)
#     response = collection
