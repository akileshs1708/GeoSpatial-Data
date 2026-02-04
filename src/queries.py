from db_connect import restaurants, districts

def add_restaurant(name, lon, lat):
    restaurants.insert_one({
        "name": name,
        "location": {"type": "Point", "coordinates": [lon, lat]}
    })

def get_all(limit=200):
    return list(restaurants.find().limit(limit))

def nearest(lon, lat, dist=5000):
    return list(restaurants.find({
        "location": {
            "$near": {
                "$geometry": {"type": "Point", "coordinates": [lon, lat]},
                "$maxDistance": dist
            }
        }
    }))

def inside_district(dname):
    d = districts.find_one({"district": dname})
    return list(restaurants.find({
        "location": {
            "$geoWithin": {"$geometry": d["geometry"]}
        }
    }))

def count_per_district():
    result = {}
    for d in districts.find():
        c = restaurants.count_documents({
            "location": {
                "$geoWithin": {"$geometry": d["geometry"]}
            }
        })
        result[d["district"]] = c
    return result

def list_districts():
    return [d["district"] for d in districts.find()]