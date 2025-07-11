import streamlit as st
import pandas as pd
from geopy.distance import geodesic
import streamlit.components.v1 as components
import pydeck as pdk

# Load CSV of geocoded fuel yards
@st.cache_data
def load_data():
    df = pd.read_csv("geocoded_yards.csv")
    return df.dropna(subset=["Latitude", "Longitude"])

df = load_data()

# Streamlit page config
st.set_page_config(page_title="Fuel Yard Finder", layout="centered")
st.title("⛽ Nearest Fuel Yard Finder")
st.markdown("Use your location to find the closest fuel yard with mapping and filters.")

# Sidebar filters
with st.sidebar:
    st.header("🔎 Filters")
    selected_county = st.selectbox("County", ["All"] + sorted(df["COUNTY"].dropna().unique()))
    selected_yard = st.selectbox("Maintenance Yard", ["All"] + sorted(df["MAINTENANCE YARD"].dropna().unique()))

# Apply filters
filtered_df = df.copy()
if selected_county != "All":
    filtered_df = filtered_df[filtered_df["COUNTY"] == selected_county]
if selected_yard != "All":
    filtered_df = filtered_df[filtered_df["MAINTENANCE YARD"] == selected_yard]

# GPS injection (hidden)
components.html("""
    <script>
    navigator.geolocation.getCurrentPosition(
        (position) => {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            const input = document.createElement("input");
            input.type = "hidden";

components.html("""
    <script>
components.html("""
    <script>
    if (!window.location.search.includes("lat")) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                window.location.search = `?lat=${lat}&lon=${lon}`;
            }
        );
    }
    </script>
""", height=0)
    if (!window.location.search.includes("lat")) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const lat = position.coords.latitude;
          const lon = position.coords.longitude;
          window.location.search = `?lat=${lat}&lon=${lon}`;
        }
      );
    }
    </script>
""", height=0)

df = load_data()
# Extract lat/lon from URL if available
query_params = st.experimental_get_query_params()
try:
    auto_lat = float(query_params.get("lat", [0.0])[0])
    auto_lon = float(query_params.get("lon", [0.0])[0])
except:
    auto_lat = 0.0
    auto_lon = 0.0

            input.name = "coords";
            input.value = lat + "," + lon;
            document.forms[0].appendChild(input);
            document.forms[0].submit();
        }
    );
    </script>
""", height=0)
with st.form("location_form"):
    user_lat = st.number_input("Latitude", format="%.6f", value=auto_lat)
    user_lon = st.number_input("Longitude", format="%.6f", value=auto_lon)

# Manual location fallback
st.markdown("### 📍 Your Location")
with st.form("location_form"):
    user_lat = st.number_input("Latitude", format="%.6f", value=0.0)
    user_lon = st.number_input("Longitude", format="%.6f", value=0.0)
    submitted = st.form_submit_button("Find Nearest Yard")

# Nearest location logic
if submitted and user_lat != 0.0 and user_lon != 0.0:
    user_location = (user_lat, user_lon)

    def calc_distance(row):
        return geodesic(user_location, (row["Latitude"], row["Longitude"])).miles

    filtered_df["Distance (miles)"] = filtered_df.apply(calc_distance, axis=1)
    nearest = filtered_df.sort_values("Distance (miles)").iloc[0]

    st.success("✅ Nearest Fuel Yard Found!")
    st.write(f"**Yard:** {nearest['MAINTENANCE YARD']}")
    st.write(f"**Address:** {nearest['MAILING ADDRESS']}, {nearest['ZIP CODE']}")
    st.write(f"**County:** {nearest['COUNTY']}, **Municipality:** {nearest['MUNICIPALITY']}")
    st.write(f"**Distance:** {nearest['Distance (miles)']:.2f} miles")

    # Map view
    mid_lat = (user_lat + nearest["Latitude"]) / 2
    mid_lon = (user_lon + nearest["Longitude"]) / 2
    zoom = 9 if nearest["Distance (miles)"] < 50 else 6

    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/streets-v12",
        initial_view_state=pdk.ViewState(
            latitude=mid_lat,
            longitude=mid_lon,
            zoom=zoom,
            pitch=30,
        ),
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=pd.DataFrame([{
                    "lat": user_lat, "lon": user_lon, "label": "You"
                }]),
                get_position='[lon, lat]',
                get_color='[0, 128, 255, 160]',
                get_radius=300,
            ),
            pdk.Layer(
                "ScatterplotLayer",
                data=pd.DataFrame([{
                    "lat": nearest["Latitude"],
                    "lon": nearest["Longitude"],
                    "label": nearest["MAINTENANCE YARD"]
                }]),
                get_position='[lon, lat]',
                get_color='[255, 0, 0, 160]',
                get_radius=300,
            )
        ],
        tooltip={"text": "{label}"}
    ))


