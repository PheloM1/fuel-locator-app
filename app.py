import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from geopy.distance import geodesic

# Check if GPS is available in query params
query_params = st.query_params
lat = query_params.get("lat")
lon = query_params.get("lon")

# Inject JavaScript if location is not yet present
if not lat or not lon:
    components.html("""
        <script>
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                const url = new URL(window.location);
                url.searchParams.set('lat', lat);
                url.searchParams.set('lon', lon);
                window.location.replace(url);
            }
        );
        </script>
    """, height=0)
    st.warning("📍 Requesting your location... please allow access in your browser.")
    st.stop()

# Proceed only when lat/lon are available
df = pd.read_csv("geocoded_yards.csv")
df = df.dropna(subset=["Latitude", "Longitude"])

st.title("🚛 Nearest Fuel Yard Finder")

with st.form("location_form"):
    user_lat = st.text_input("Your Latitude", value=lat)
    user_lon = st.text_input("Your Longitude", value=lon)
    submitted = st.form_submit_button("Find Nearest Yard")

if submitted and user_lat and user_lon:
    try:
        user_coords = (float(user_lat), float(user_lon))

        df["Distance (miles)"] = df.apply(
            lambda row: geodesic(user_coords, (row["Latitude"], row["Longitude"])).miles,
            axis=1
        )

        nearest = df.sort_values("Distance (miles)").iloc[0]

        st.success(f"📍 Nearest yard: {nearest['MAINTENANCE YARD']} ({nearest['Distance (miles)']:.2f} miles)")
        st.write(f"**County:** {nearest['COUNTY']}")
        st.write(f"**Address:** {nearest['MAILING ADDRESS']}, {nearest['ZIP CODE']}")
        st.write(f"**Phone:** {nearest['YARD PHONE #']}")
        st.write(f"**Supervisor:** {nearest['CREW SUPERVISOR']}")

        st.map(pd.DataFrame({
            'lat': [user_coords[0], nearest['Latitude']],
            'lon': [user_coords[1], nearest['Longitude']]
        }))

    except ValueError:
        st.error("❗ Invalid coordinates. Please enter valid numbers.")

