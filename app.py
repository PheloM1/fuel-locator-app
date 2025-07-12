import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# Load geocoded data
df = pd.read_csv("geocoded_yards.csv")

df = df.dropna(subset=["LAT", "LON"])

def find_nearest(lat, lon):
    distances = df.apply(lambda row: geodesic((lat, lon), (row['LAT'], row['LON'])).miles, axis=1)
    idx = distances.idxmin()
    return df.loc[idx], distances[idx]

def get_coordinates(location_name):
    geolocator = Nominatim(user_agent="fuel_locator")
    location = geolocator.geocode(location_name)
    if location:
        return location.latitude, location.longitude
    return None, None

st.set_page_config(page_title="Fuel Yard Locator", layout="wide")
st.title("🚛 NJ Fuel Yard Locator")

st.header("📍 Enter a location or use your GPS")
location_input = st.text_input("Type your location (e.g., city or ZIP code):")

lat, lon = None, None

query_params = st.query_params
if "lat" in query_params and "lon" in query_params:
    lat = float(query_params["lat"])
    lon = float(query_params["lon"])
elif location_input:
    lat, lon = get_coordinates(location_input)

if lat is not None and lon is not None:
    nearest_yard, distance = find_nearest(lat, lon)

    yard_name = nearest_yard['MAINTENANCE YARD']
    address = nearest_yard['MAILING ADDRESS']
    zip_code = str(nearest_yard['ZIP CODE'])
    county = nearest_yard['COUNTY']
    phone = nearest_yard['YARD PHONE #'] if 'YARD PHONE #' in nearest_yard else "N/A"

    st.success(f"✅ Nearest Yard: {yard_name} ({distance:.2f} mi)")
    st.markdown(f"**Address:** {address}, {county}, NJ {zip_code}")
    st.markdown(f"**Phone:** {phone}")

    maps_url = f"https://www.google.com/maps/dir/?api=1&destination={address.replace(' ', '+')}+{county}+NJ+{zip_code}"
    st.markdown(f"[🗺️ Open in Google Maps]({maps_url})", unsafe_allow_html=True)

    m = folium.Map(location=[lat, lon], zoom_start=10)
    folium.Marker([lat, lon], popup="Your Location", icon=folium.Icon(color='blue')).add_to(m)
    folium.Marker([nearest_yard['LAT'], nearest_yard['LON']], popup=yard_name, icon=folium.Icon(color='green')).add_to(m)
    st_folium(m, width=700, height=500)
else:
    st.warning("Requesting your location... please allow access in your browser.")
    st.components.v1.html("""
        <script>
        window.addEventListener('load', () => {
            if (!window.location.search.includes("lat")) {
                navigator.geolocation.getCurrentPosition(function(pos) {
                    const lat = pos.coords.latitude;
                    const lon = pos.coords.longitude;
                    const newUrl = window.location.href.split('?')[0] + `?lat=${lat}&lon=${lon}`;
                    window.location.replace(newUrl);
                });
            }
        });
        </script>
    """, height=0)
