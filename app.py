import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import time

# Set up the app
st.title("📍 Parking Data Geocoder")
st.markdown("""
Geocodes addresses from your GitHub repository's CSV file.
""")

# Load data directly from GitHub
DATA_URL = "https://raw.githubusercontent.com/adahuonganh/fiep2025/main/parking_data.csv"

@st.cache_data  # Cache to avoid reloading on every interaction
def load_data():
    try:
        return pd.read_csv(DATA_URL)
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return None

df = load_data()

if df is not None:
    st.subheader("Raw Data")
    st.write(df)

    # Initialize geocoder (cached)
    @st.cache_resource
    def setup_geocoder():
        return Nominatim(user_agent="fiep2025_parking_app", timeout=10)

    geolocator = setup_geocoder()

    # Geocoding function with retries
    def geocode_with_retry(address, max_retries=3):
        for _ in range(max_retries):
            try:
                location = geolocator.geocode(address)
                if location:
                    return (location.latitude, location.longitude)
            except (GeocoderTimedOut, GeocoderUnavailable):
                time.sleep(1)
        return (None, None)

    # Button to trigger geocoding
    if st.button("Geocode Addresses"):
        st.info("Geocoding... This may take a while due to API limits.")
        df[["latitude", "longitude"]] = df["Address"].apply(
            lambda x: pd.Series(geocode_with_retry(x)))
        
        st.subheader("Geocoded Data")
        st.write(df)

        # Show map
        st.subheader("Map View")
        st.map(df.dropna(subset=["latitude", "longitude"]))

        # Download results
        st.download_button(
            label="Download Geocoded Data (CSV)",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="geocoded_parking_data.csv",
            mime="text/csv"
        )
