from pymongo import MongoClient

MONGO_URI = "mongodb+srv://23pd33_db_user:123@cluster0.vm3go43.mongodb.net/"

client = MongoClient(MONGO_URI)
db = client["tamilnadu_spatial"]

restaurants = db["restaurants"]
districts = db["districts"]