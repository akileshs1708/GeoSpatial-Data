import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
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
if "district_data" not in st.session_state:
    st.session_state.district_data = None


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
    st.session_state.map = m
    return st_folium(
        st.session_state.map,
        width=1100,
        height=650,
        key=f"map_{st.session_state.selected_district}"
    )


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

    marker_cluster = MarkerCluster().add_to(m)

    for r in get_all(800):
        lon, lat = r["location"]["coordinates"]
        folium.Marker(
            [lat, lon],
            popup=r["name"],
            tooltip=f"{r['name']} ({lat:.4f}, {lon:.4f})"
        ).add_to(marker_cluster)

    show_map(m)


# ---------------- BY DISTRICT ----------------
elif menu == "View Restaurants by District":
    dname = st.selectbox("Choose District", list_districts(), key="district_selector")

    if st.button("Show Restaurants"):
        st.session_state.selected_district = dname
        st.session_state.district_data = inside_district(dname)

    if st.session_state.district_data and st.session_state.selected_district == dname:
        data = st.session_state.district_data
        m = base_map()

        # highlight district
        for d in districts.find():
            if d["district"] == dname:
                folium.GeoJson(
                    d["geometry"],
                    tooltip=d["district"],
                    style_function=lambda x: {
                        "fillColor": "#ff000020",
                        "color": "red",
                        "weight": 3
                    }
                ).add_to(m)

        # add markers with clustering + tooltip
        marker_cluster = MarkerCluster().add_to(m)

        for r in data:
            lon, lat = r["location"]["coordinates"]
            folium.Marker(
                [lat, lon],
                popup=r["name"],
                tooltip=f"{r['name']} ({lat:.4f}, {lon:.4f})"
            ).add_to(marker_cluster)

        st.success(f"{len(data)} restaurants in {dname}")
        show_map(m)

    else:
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

        folium.Marker(
            [lat, lon],
            icon=folium.Icon(color="red"),
            popup="You"
        ).add_to(m)

        marker_cluster = MarkerCluster().add_to(m)

        for r in results:
            rlon, rlat = r["location"]["coordinates"]
            folium.Marker(
                [rlat, rlon],
                popup=r["name"],
                tooltip=f"{r['name']} ({rlat:.4f}, {rlon:.4f})"
            ).add_to(marker_cluster)

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