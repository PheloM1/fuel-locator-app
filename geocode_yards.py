import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# Load Excel file
xls = pd.ExcelFile("maintence yard with phone numbers1.xlsx")
df = pd.concat([xls.parse(sheet) for sheet in xls.sheet_names], ignore_index=True)

# Detect header and clean it
df.columns = df.iloc[3]
df = df.iloc[4:].reset_index(drop=True)
df.columns = [str(col).strip() for col in df.columns]

# Keep only rows with valid addresses
df = df.dropna(subset=["MAILING ADDRESS", "MAINTENANCE YARD"])
df["ZIP"] = df["ZIP CODE"].astype(str).str.extract(r"(\d{5})")[0]
df["Full Address"] = df["MAILING ADDRESS"] + ", " + df["MAINTENANCE YARD"] + ", NJ " + df["ZIP"]

# Geocoder setup
geolocator = Nominatim(user_agent="fuel-yard-mac", timeout=10)
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

# Geocode rows
lat, lon = [], []
for address in df["Full Address"]:
    try:
        loc = geocode(address)
        if loc:
            lat.append(loc.latitude)
            lon.append(loc.longitude)
        else:
            lat.append(None)
            lon.append(None)
    except Exception as e:
        print(f"Failed to geocode: {address}\nReason: {e}")
        lat.append(None)
        lon.append(None)

df["Latitude"] = lat
df["Longitude"] = lon

# Save to CSV
df.to_csv("geocoded_yards.csv", index=False)
print("✅ Saved as geocoded_yards.csv")

