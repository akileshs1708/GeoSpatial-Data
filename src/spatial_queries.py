from db_connect import restaurants

chennai = [80.2707, 13.0827]

for r in restaurants.find({
    "location": {
        "$near": {
            "$geometry": {"type": "Point", "coordinates": chennai},
            "$maxDistance": 5000
        }
    }
}):
    print(r["name"])

from db_connect import restaurants, districts

district = districts.find_one({"district": "Chennai"})

for r in restaurants.find({
    "location": {
        "$geoWithin": {
            "$geometry": district["geometry"]
        }
    }
}):
    print(r["name"])

for d in districts.find():
    count = restaurants.count_documents({
        "location": {
            "$geoWithin": {
                "$geometry": d["geometry"]
            }
        }
    })
    print(d["district"], count)