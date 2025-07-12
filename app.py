import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic

st.set_page_config(page_title="Fuel Locator", layout="wide")
st.title("🚛 NJ Fuel Yard Locator")

@st.cache_data
def load_data():
    df = pd.read_csv("geocoded_yards.csv")
    return df.dropna(subset=["Latitude", "Longitude"])

data = load_data()

query = st.query_params
lat = query.get("lat")
lon = query.get("lon")

if lat and lon:
    try:
        user_location = (float(lat[0]), float(lon[0]))
        data["Distance (mi)"] = data.apply(
            lambda row: geodesic(user_location, (row["Latitude"], row["Longitude"])).miles,
            axis=1
        )
        nearest = data.sort_values("Distance (mi)").iloc[0]
        st.success(f"Nearest Yard: {nearest['MAINTENANCE YARD']} ({nearest['Distance (mi)']:.1f} mi)")

        m = folium.Map(location=user_location, zoom_start=10)
        folium.Marker(user_location, tooltip="You Are Here", icon=folium.Icon(color='blue')).add_to(m)
        folium.Marker([
            nearest["Latitude"], nearest["Longitude"]
        ], tooltip=nearest["MAINTENANCE YARD"], icon=folium.Icon(color='red')).add_to(m)
        st_folium(m, width=700, height=500)
    except:
        st.error("Invalid coordinates provided.")
else:
    st.warning("Click the button to get your location and open the GPS-enabled app link.")

    st.components.v1.html("""
    <script>
      function openWithLocation() {
        navigator.geolocation.getCurrentPosition(
          function(pos) {
            const lat = pos.coords.latitude;
            const lon = pos.coords.longitude;
            const base = window.location.origin + window.location.pathname;
            const url = `${base}?lat=${lat}&lon=${lon}`;
            document.getElementById("link-out").innerHTML = `<a href="${url}" target="_blank">Open App with My Location</a>`;
          },
          function(err) {
            alert("Failed to get location: " + err.message);
          }
        );
      }
    </script>
    <button onclick="openWithLocation()">📍 Use My Location</button>
    <p id="link-out"></p>
    """, height=100)
