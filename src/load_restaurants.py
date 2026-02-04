import json
from db_connect import restaurants

with open("../data/restaurants.geojson", encoding="utf-8") as f:
    data = json.load(f)

for feature in data["features"]:
    restaurants.insert_one({
        "name": feature["properties"].get("name", "Unknown"),
        "location": feature["geometry"]
    })

restaurants.create_index([("location", "2dsphere")])
print("Restaurants loaded with 2dsphere index.")