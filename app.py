import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# Load and clean data
df = pd.read_csv("geocoded_yards.csv")
df = df.dropna(subset=["Latitude", "Longitude"])

def find_nearest(lat, lon):
    distances = df.apply(lambda row: geodesic((lat, lon), (row['Latitude'], row['Longitude'])).miles, axis=1)
    idx = distances.idxmin()
    return df.loc[idx], distances[idx]

def get_coordinates(location_name):
    geolocator = Nominatim(user_agent="fuel_locator")
    try:
        location = geolocator.geocode(location_name, timeout=10)
        if location:
            return location.latitude, location.longitude
    except Exception:
        st.error("\u274c Geolocation lookup failed. Please try again later.")
    return None, None

# Page setup
st.set_page_config(page_title="Fuel Yard Locator", layout="wide")
st.markdown("""
    <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: -20px;">
        <img src="https://raw.githubusercontent.com/PheloM1/fuel-locator-app/main/assets/fuel_icons.png" width="60"/>
        <h1 style="margin-bottom: 0;">NJ Fuel Yard Locator</h1>
    </div>
    <p style="margin-top: 0.2rem; font-size: 1rem; color: gray;">Find your nearest maintenance fuel station across NJ</p>
""", unsafe_allow_html=True)

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
    phone = nearest_yard.get('YARD PHONE #', 'N/A')

    st.success(f"\u2705 Nearest Yard: {yard_name} ({distance:.2f} mi)")
    st.markdown(f"**Address:** {address}, {county}, NJ {zip_code}")
    st.markdown(f"**Phone:** {phone}")

    maps_url = f"https://www.google.com/maps/dir/?api=1&destination={address.replace(' ', '+')}+{county}+NJ+{zip_code}"
    st.markdown(f"[\ud83d\uddfa\ufe0f Open in Google Maps]({maps_url})", unsafe_allow_html=True)

    m = folium.Map(location=[lat, lon], zoom_start=10)
    folium.Marker([lat, lon], popup="Your Location", icon=folium.Icon(color='blue')).add_to(m)
    folium.Marker([nearest_yard['Latitude'], nearest_yard['Longitude']], popup=yard_name, icon=folium.Icon(color='green')).add_to(m)

    if st.checkbox("\ud83d\udccd Show all yards on map"):
        for _, row in df.iterrows():
            popup_html = f"""
            <b>{row['MAINTENANCE YARD']}</b><br>
            {row['MAILING ADDRESS']}, {row['COUNTY']}, NJ {row['ZIP CODE']}<br>
            <a href='https://www.google.com/maps/dir/?api=1&destination={row['MAILING ADDRESS'].replace(' ', '+')}+{row['COUNTY']}+NJ+{row['ZIP CODE']}' target='_blank'>\ud83d\udccd Directions</a>
            """
            folium.Marker(
                [row['Latitude'], row['Longitude']],
                popup=popup_html,
                icon=folium.Icon(color='gray')
            ).add_to(m)
    st_folium(m, width=700, height=500)

else:
    st.warning("Enter a location above or click the button to use your device’s GPS.")
    st.components.v1.html("""
    <div style="margin-top: 1em; text-align: center;">
        <a href="https://phelom1.github.io/fuel-locator-app/get-location.html" target="_blank" rel="noopener noreferrer">
            <button style="
                padding: 0.75em 1.5em;
                font-size: 16px;
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
            ">📍 Use My Location</button>
        </a>
    </div>
""", height=60)

