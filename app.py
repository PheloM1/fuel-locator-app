import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# Load geocoded data
df = pd.read_csv("geocoded_yards.csv")
df = df.dropna(subset=["Latitude", "Longitude"])

def find_nearest(lat, lon):
    distances = df.apply(lambda row: geodesic((lat, lon), (row['Latitude'], row['Longitude'])).miles, axis=1)
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
query_params = st.experimental_get_query_params()  # ✅ FIXED HERE
if "lat" in query_params and "lon" in query_params:
    lat = float(query_params["lat"][0])
    lon = float(query_params["lon"][0])
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
    folium.Marker([nearest_yard['Latitude'], nearest_yard['Longitude']], popup=yard_name, icon=folium.Icon(color='green')).add_to(m)
    st_folium(m, width=700, height=500)

else:
    st.warning("Enter a location above or click the button to use your device’s GPS.")

    st.markdown("""
        <script>
        function getLocationAndRedirect() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(function(position) {
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;
                    const newUrl = window.location.origin + window.location.pathname + "?lat=" + lat + "&lon=" + lon;
                    window.top.location.href = newUrl;
                }, function(error) {
                    alert("Location access denied or unavailable.");
                });
            } else {
                alert("Geolocation is not supported by this browser.");
            }
        }
        </script>

        <button onclick="getLocationAndRedirect()" style="
            margin-top: 1em;
            padding: 0.75em 1.5em;
            font-size: 16px;
            background-color: #4A4A4A;
            color: white;
            border: none;
            border-radius: 6px;
        ">📍 Use My Location</button>
    """, unsafe_allow_html=True)
