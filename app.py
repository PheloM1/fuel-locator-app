import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic
import streamlit.components.v1 as components

st.set_page_config(page_title="Fuel Yard Locator", layout="wide")

# Inject JavaScript to get GPS coordinates via iframe-safe components.html
components.html("""
<script>
console.log("JavaScript loaded from iframe");

if (!window.location.search.includes("lat")) {
    navigator.geolocation.getCurrentPosition(
        function(position) {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            console.log("Got location:", lat, lon);
            const newUrl = window.location.origin + window.location.pathname + `?lat=${lat}&lon=${lon}`;
            window.location.replace(newUrl);
        },
        function(error) {
            console.error("Geolocation error:", error);
        }
    );
} else {
    console.log("URL already has coordinates:", window.location.search);
}
</script>
""", height=0)

# Load data
df = pd.read_csv("geocoded_yards.csv")
df = df.dropna(subset=["Latitude", "Longitude"])

# Get query parameters
params = st.query_params
lat = params.get("lat")
lon = params.get("lon")

if lat and lon:
    try:
        user_location = (float(lat), float(lon))
        st.success(f"\ud83d\udccd Location detected: {user_location}")

        # Calculate distances
        df["Distance (miles)"] = df.apply(
            lambda row: geodesic(user_location, (row["Latitude"], row["Longitude"])).miles,
            axis=1
        )

        # Nearest yard
        nearest = df.sort_values("Distance (miles)").iloc[0]

        st.subheader(f"Nearest Yard: {nearest['MAINTENANCE YARD']}")
        st.write(f"Distance: {nearest['Distance (miles)']:.2f} miles")
        st.write(f"County: {nearest['COUNTY']}")
        st.write(f"Address: {nearest['MAILING ADDRESS']}, NJ {nearest['ZIP CODE']}")
        st.write(f"Phone: {nearest['YARD PHONE #']}")

        # Map
        m = folium.Map(location=user_location, zoom_start=9)
        folium.Marker(user_location, tooltip="You", icon=folium.Icon(color="blue")).add_to(m)
        folium.Marker((nearest["Latitude"], nearest["Longitude"]), tooltip=nearest["MAINTENANCE YARD"], icon=folium.Icon(color="red")).add_to(m)
        st_folium(m, width=700, height=500)

    except:
        st.error("Could not parse your coordinates.")
else:
    st.warning("Requesting your location... please allow access in your browser.")
