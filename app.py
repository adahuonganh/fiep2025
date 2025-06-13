import streamlit as st
from geopy.geocoders import Nominatim
from map import render_map
from diagram import render

st.set_page_config(
    page_title="ParkSmart All-in-One",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.sidebar.header("📍 Choose Your Location")
DEFAULT_LAT, DEFAULT_LON = 50.1270332, 8.6644491  # Default location
lat = st.sidebar.number_input("Latitude", value=DEFAULT_LAT, format="%.6f")
lon = st.sidebar.number_input("Longitude", value=DEFAULT_LON, format="%.6f")

st.sidebar.header("⚙️ Filters")
max_dist = st.sidebar.slider("Max distance (km)", 0.1, 20.0, 10.0, 0.1)
fee_range = st.sidebar.slider("Fee range (€/h)", 0.0, 20.0, (0.0, 5.0), 0.1)
ev_only = st.sidebar.checkbox("Only EV charging spots")

tabs = st.tabs(["Map View", "Compare Parkings", "Raw Data"])

with tabs[0]:
    render_map(lat, lon, max_dist, fee_range, ev_only)

with tabs[1]:
    render(lat, lon, max_dist, fee_range, ev_only)

with tabs[2]:
    st.header("📝 Raw Parking Data")
    st.warning("Data integration needs to be adjusted for consistency.")
