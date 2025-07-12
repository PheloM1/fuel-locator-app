import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import streamlit.components.v1 as components

# Custom CSS for mobile optimization
st.markdown("""
    <style>
        html, body, [class*="css"]  {
            font-size: 18px;
        }
        a, button, .stButton>button {
            font-size: 18px !important;
            padding: 0.75em 1.5em;
        }
        .element-container:has(.folium-map) {
            overflow-x: hidden !important;
        }
    </style>
""", unsafe_allow_html=True)

# Load yard data
df = pd.read_csv("geocoded_yards.csv")
df = df.dropna(subset=["Latitude", "Longitude"])

# Set page title
st.set_page_config(page_title="NJ Fuel Yard Locator", page_icon="🚛", layout="wide")
st.title("🚛 NJ Fuel Yard Locator")

# Location input section
st.subheader("📍 Enter a location or use your GPS")
address = st.text_input("Type your location (e.g., city or ZIP code):")

if address:
    try:
        geolocator = Nominatim(user_agent="fuel-locator-app")
        location = geolocator.geocode(address)
        if location:
            user_lat = location.latitude
            user_lon = location.longitude
        else:
            st.error("Location not found. Try something else.")
            st.stop()
    except:
        st.error("Geocoding failed. Try again later.")
        st.stop()
else:
    query_params = st.query_params
    user_lat = query_params.get("lat", None)
    user_lon = query_params.get("lon", None)

# Try converting lat/lon to float
try:
    if isinstance(user_lat, list):
        user_lat = float(user_lat[0])
    else:
        user_lat = float(user_lat)
    if isinstance(user_lon, list):
        user_lon = float(user_lon[0])
    else:
        user_lon = float(user_lon)

    user_location = (user_lat, user_lon)
    df["Distance (mi)"] = df.apply(
        lambda row: geodesic(user_location, (row["Latitude"], row["Longitude"])).miles,
        axis=1
    )

    nearest = df.nsmallest(1, "Distance (mi)").iloc[0]

    # Map setup
    m = folium.Map(location=user_location, zoom_start=10)
    folium.Marker(user_location, tooltip="📍You are here", icon=folium.Icon(color="blue")).add_to(m)
    folium.Marker([
        nearest["Latitude"], nearest["Longitude"]
    ], tooltip=f"🚚 {nearest['MAINTENANCE YARD']}", icon=folium.Icon(color="green")).add_to(m)

    st.subheader(f"✅ Nearest Yard: {nearest['MAINTENANCE YARD']} ({nearest['Distance (mi)']:.2f} mi)")
    st.write(f"📍 Address: {nearest['MAILING ADDRESS']}, {nearest['MUNICIPALITY']}, NJ {int(nearest['ZIP CODE'])}")
    st.write(f"📞 Phone: {nearest['YARD PHONE #']}")

    # Google Maps directions link
    dest_lat = nearest['Latitude']
    dest_lon = nearest['Longitude']
    maps_url = f"https://www.google.com/maps/dir/?api=1&origin=My+Location&destination={dest_lat},{dest_lon}&travelmode=driving"
    st.markdown(f"[🗺️ Open in Google Maps for Directions]({maps_url})", unsafe_allow_html=True)

    st_folium(m, height=400, use_container_width=True)

except Exception:
    st.warning("Requesting your location... please allow access in your browser.")

    # Inject JS to scroll up and build a clickable link
    components.html(f"""
    <script>
    window.scrollTo(0, 0);
    navigator.geolocation.getCurrentPosition(
      function(pos) {{
        const lat = pos.coords.latitude;
        const lon = pos.coords.longitude;
        const url = "https://fuel-locator-app-ykfxqnemvduapp8ybqyertm.streamlit.app/?lat=" + lat + "&lon=" + lon;
        const link = document.createElement("a");
        link.href = url;
        link.innerText = "👉 Click here to open with your GPS location";
        link.target = "_blank";
        link.style.fontSize = "20px";
        link.style.fontWeight = "bold";
        link.style.display = "block";
        link.style.marginTop = "20px";
        document.body.appendChild(link);
      }},
      function(err) {{
        document.body.innerText = "Could not access your location. Please enable it.";
      }}
    );
    </script>
    """, height=100)
