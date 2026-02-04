import folium
from db_connect import restaurants

m = folium.Map(location=[11.0, 78.0], zoom_start=7)

for r in restaurants.find().limit(500):
    coords = r["location"]["coordinates"]
    folium.Marker(
        location=[coords[1], coords[0]],
        popup=r["name"]
    ).add_to(m)

m.save("tamilnadu_restaurants_map.html")
print("Map created!")