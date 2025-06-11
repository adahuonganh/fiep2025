import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import time

# Set page config first
st.set_page_config(page_title="ParkSmart", layout="wide")

# Load data function
@st.cache_data
def load_data():
    DATA_URL = "https://raw.githubusercontent.com/adahuonganh/fiep2025/main/parking_data.csv"
    try:
        return pd.read_csv(DATA_URL)
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return None

# Geocoding functions
@st.cache_resource
def setup_geocoder():
    return Nominatim(user_agent="fiep2025_parking_app", timeout=10)

def geocode_with_retry(address, max_retries=3):
    geolocator = setup_geocoder()
    for _ in range(max_retries):
        try:
            location = geolocator.geocode(address)
            if location:
                return (location.latitude, location.longitude)
        except (GeocoderTimedOut, GeocoderUnavailable):
            time.sleep(1)
    return (None, None)

# Main page
def main_page():
    st.title("ParkSmart - Find your parking place")
    st.markdown("""
    Geocodes addresses from your GitHub repository's CSV file.
    """)

    df = load_data()

    if df is not None:
        st.subheader("Raw Data")
        st.write(df)

        if st.button("Geocode Addresses"):
            st.info("Geocoding... This may take a while due to API limits.")
            df[["latitude", "longitude"]] = df["Address"].apply(
                lambda x: pd.Series(geocode_with_retry(x)))
            
            st.subheader("Geocoded Data")
            st.write(df)

            st.subheader("Map View")
            st.map(df.dropna(subset=["latitude", "longitude"]))

            st.download_button(
                label="Download Geocoded Data (CSV)",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="geocoded_parking_data.csv",
                mime="text/csv"
            )

# Page navigation
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Main Page", "Interactive Map", "Data Analysis"])

    if page == "Main Page":
        main_page()
    elif page == "Interactive Map":
        from map import render_map
        render_map()
    elif page == "Data Analysis":
        from diagram import render
        render()

if __name__ == "__main__":
    main()
