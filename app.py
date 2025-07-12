import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# Load geocoded data
df = pd.read_csv("geocoded_yards.csv")

# Rename columns to standard format
df.columns = [col.strip().upper() for col in df.columns]
df = df.rename(columns={"LATITUDE": "LAT", "LONGITUDE": "LON"})
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
    st.warning("Enter a location above or click the button to use your device’s GPS.")
    st.markdown("""
        <a href="#" onclick="
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;
                    const url = window.location.origin + window.location.pathname + `?lat=${lat}&lon=${lon}`;
                    window.open(url, '_blank');
                },
                function(error) {
                    alert('Could not retrieve location. Please allow GPS access.');
                }
            );
            return false;
        " style="
            display: inline-block;
            padding: 0.75em 1.5em;
            margin-top: 1em;
            font-size: 16px;
            font-weight: 600;
            color: white;
            background-color: #4A4A4A;
            border-radius: 5px;
            text-decoration: none;
        ">
        📍 Use My Location
        </a>
    """, unsafe_allow_html=True)
