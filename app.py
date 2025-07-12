import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic
from urllib.parse import urlencode

st.set_page_config(page_title="Fuel Locator", layout="wide")
st.title("🚛 NJ Fuel Yard Locator")

# Read geocoded data
@st.cache_data
def load_data():
    df = pd.read_csv("geocoded_yards.csv")
    return df.dropna(subset=["Latitude", "Longitude"])

data = load_data()

# Read location from query params
query = st.query_params
lat = query.get("lat")
lon = query.get("lon")

if lat and lon:
    try:
        user_location = (float(lat), float(lon))

        # Calculate distances
        data["Distance (mi)"] = data.apply(
            lambda row: geodesic(user_location, (row["Latitude"], row["Longitude"])).miles,
            axis=1
        )

        nearest = data.sort_values("Distance (mi)").iloc[0]

        st.success(f"Nearest Yard: {nearest['MAINTENANCE YARD']} ({nearest['Distance (mi)']:.1f} mi)")

        # Show map
        m = folium.Map(location=user_location, zoom_start=10)
        folium.Marker(user_location, tooltip="You Are Here", icon=folium.Icon(color='blue')).add_to(m)
        folium.Marker([
            nearest["Latitude"], nearest["Longitude"]
        ], tooltip=nearest["MAINTENANCE YARD"], icon=folium.Icon(color='red')).add_to(m)
        st_folium(m, width=700, height=500)
    except Exception as e:
        st.error("Invalid location provided in URL.")
else:
    st.warning("Requesting your location... please allow access in your browser.")

    # Button to trigger location script
    if st.button("📍 Use My Location"):
        st.components.v1.html("""
        <script>
          navigator.geolocation.getCurrentPosition(
            function(pos) {
              const lat = pos.coords.latitude;
              const lon = pos.coords.longitude;
              const query = new URLSearchParams({lat: lat, lon: lon});
              window.location.search = query.toString();
            },
            function(err) {
              alert("Error fetching location: " + err.message);
            }
          );
        </script>
        """, height=0)
