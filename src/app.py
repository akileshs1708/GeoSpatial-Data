import streamlit as st
import folium
from streamlit_folium import st_folium
from queries import *
from db_connect import districts

st.set_page_config(layout="wide")
st.title("Tamil Nadu Spatial Restaurants Explorer")

# ---------------- SESSION STATE ----------------
if "map" not in st.session_state:
    st.session_state.map = None
if "clicked" not in st.session_state:
    st.session_state.clicked = None
if "selected_district" not in st.session_state:
    st.session_state.selected_district = None

# ---------------- Helpers ----------------
def base_map():
    m = folium.Map(location=[11.0, 78.0], zoom_start=7)
    for d in districts.find():
        folium.GeoJson(
            d["geometry"],
            tooltip=d["district"],
            style_function=lambda x: {
                "fillColor": "#00000000",
                "color": "blue",
                "weight": 1
            }
        ).add_to(m)
    return m

def show_map(m):
    # Store the map in session state
    st.session_state.map = m
    # Display the map
    return st_folium(st.session_state.map, width=1100, height=650, key=f"map_{st.session_state.selected_district}")

# ---------------- Sidebar Menu ----------------
menu = st.sidebar.selectbox("Menu", [
    "Home - All Restaurants",
    "View Restaurants by District",
    "Nearest Restaurants (Click Map)",
    "Add New Restaurant",
    "District Statistics"
])

# ---------------- HOME ----------------
if menu == "Home - All Restaurants":
    m = base_map()
    for r in get_all(800):
        lon, lat = r["location"]["coordinates"]
        folium.Marker([lat, lon], popup=r["name"]).add_to(m)
    show_map(m)

# ---------------- BY DISTRICT ----------------
elif menu == "View Restaurants by District":
    dname = st.selectbox("Choose District", list_districts(), key="district_selector")
    
    # Use a unique key for the button to prevent re-rendering issues
    if st.button("Show Restaurants", key="show_district_btn"):
        st.session_state.selected_district = dname
        data = inside_district(dname)
        m = base_map()
        
        # Highlight the selected district
        for d in districts.find():
            if d["district"] == dname:
                folium.GeoJson(
                    d["geometry"],
                    tooltip=d["district"],
                    style_function=lambda x: {
                        "fillColor": "#ff000020",  # Light red fill for selected district
                        "color": "red",
                        "weight": 3
                    }
                ).add_to(m)
            else:
                folium.GeoJson(
                    d["geometry"],
                    tooltip=d["district"],
                    style_function=lambda x: {
                        "fillColor": "#00000000",
                        "color": "blue",
                        "weight": 1
                    }
                ).add_to(m)
        
        # Add markers for restaurants
        for r in data:
            lon, lat = r["location"]["coordinates"]
            folium.Marker([lat, lon], popup=r["name"]).add_to(m)
        
        st.session_state.map = m
        st.success(f"{len(data)} restaurants in {dname}")
    
    # Always show the map - either the one from session state or create a new one
    if st.session_state.map and st.session_state.selected_district == dname:
        # Show the stored map if it exists and matches the selected district
        show_map(st.session_state.map)
    else:
        # Otherwise show the base map
        show_map(base_map())

# ---------------- NEAREST ----------------
elif menu == "Nearest Restaurants (Click Map)":
    st.info("Click on map")

    map_data = st_folium(base_map(), width=1100, height=650)

    if map_data and map_data.get("last_clicked"):
        st.session_state.clicked = map_data["last_clicked"]

    if st.session_state.clicked:
        lat = st.session_state.clicked["lat"]
        lon = st.session_state.clicked["lng"]

        results = nearest(lon, lat, 5000)

        m = folium.Map(location=[lat, lon], zoom_start=13)
        folium.Marker([lat, lon],
                      icon=folium.Icon(color="red"),
                      popup="You").add_to(m)

        for r in results:
            rlon, rlat = r["location"]["coordinates"]
            folium.Marker([rlat, rlon], popup=r["name"]).add_to(m)

        show_map(m)

# ---------------- ADD RESTAURANT ----------------
elif menu == "Add New Restaurant":
    st.info("Click map to choose location")

    map_data = st_folium(base_map(), width=1100, height=650)

    if map_data and map_data.get("last_clicked"):
        st.session_state.clicked = map_data["last_clicked"]

    if st.session_state.clicked:
        lat = st.number_input("Latitude", value=st.session_state.clicked["lat"])
        lon = st.number_input("Longitude", value=st.session_state.clicked["lng"])
        name = st.text_input("Restaurant Name")

        if st.button("Add"):
            add_restaurant(name, lon, lat)
            st.success("Added successfully!")

# ---------------- STATS ----------------
elif menu == "District Statistics":
    counts = count_per_district()
    st.bar_chart(counts)