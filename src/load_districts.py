import json
from db_connect import districts

with open("../data/tamil_nadu_geo.json") as f:
    districts = json.load(f)

for feature in districts["features"]:
    districts.insert_one({
        "district": feature["properties"]["district"],
        "geometry": feature["geometry"]
    })

districts.create_index([("geometry", "2dsphere")])
print("Districts loaded with 2dsphere index.")