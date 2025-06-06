import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import time

# Set up the app title and description
st.title("🚗 Parking Data Geocoding App")
st.markdown("""
This app geocodes parking data addresses using OpenStreetMap's Nominatim.
Upload a CSV file or use the sample data from the repository.
""")

# Initialize geocoder with retries and caching
@st.cache_resource
def setup_geocoder():
    return Nominatim(user_agent="fiep2025_parking_app", timeout=10)

geolocator = setup_geocoder()

# Geocoding function with error handling
def geocode_with_retry(address, max_retries=3):
    for _ in range(max_retries):
        try:
            location = geolocator.geocode(address)
            if location:
                return (location.latitude, location.longitude)
        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            st.warning(f"Geocoding timed out for '{address}'. Retrying...")
            time.sleep(1)
    return (None, None)

# Load data (from uploaded file or GitHub)
def load_data():
    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
    if uploaded_file:
        return pd.read_csv(uploaded_file)
    else:
        # Fallback: Load sample data from GitHub
        try:
            url = "https://raw.githubusercontent.com/adahuonganh/fiep2025/main/data/parking_data.csv"
            return pd.read_csv(url)
        except:
            st.error("No file uploaded and sample data not found in the repository.")
            return None

# Main app logic
df = load_data()

if df is not None:
    st.subheader("Data Preview")
    st.write(df.head())

    if st.button("Geocode Addresses"):
        st.info("Geocoding in progress... This may take a while due to rate limits.")
        df["latitude"], df["longitude"] = zip(*df["Address"].apply(geocode_with_retry))
        
        st.subheader("Geocoded Data")
        st.write(df)

        # Display map
        st.subheader("Map View")
        st.map(df.dropna(subset=["latitude", "longitude"]))

        # Download button
        st.download_button(
            label="Download Geocoded Data (CSV)",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="geocoded_parking_data.csv",
            mime="text/csv"
        )
