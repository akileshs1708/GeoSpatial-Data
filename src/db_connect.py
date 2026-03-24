from pymongo import MongoClient

MONGO_URI = "mongodb+srv://spatial_db:1234@cluster0.kknpbrg.mongodb.net/"

client = MongoClient(MONGO_URI)
db = client["tamilnadu_spatial"]

restaurants = db["restaurants"]
districts = db["districts"]
print(client.list_database_names())