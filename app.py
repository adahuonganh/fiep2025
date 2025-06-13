import streamlit as st
from geopy.geocoders import Nominatim
from map import render_map
from diagram import render
from fuel_dashboard import render_fuel_dashboard  # Import Fuel Dashboard function

st.set_page_config(
    page_title="ParkSmart All-in-One",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for location tracking
if "user_lat" not in st.session_state:
    st.session_state.user_lat = 50.1270332
if "user_lon" not in st.session_state:
    st.session_state.user_lon = 8.6644491

st.sidebar.header("📍 Choose Your Location")
location_method = st.sidebar.radio("Select method:", ["Enter address/postal code", "Enter coordinates"])

if location_method == "Enter address/postal code":
    address_input = st.sidebar.text_input("Enter address or postal code:")
    if address_input:
        geolocator = Nominatim(user_agent="parking_finder")
        location = geolocator.geocode(address_input)
        if location:
            st.session_state.user_lat = location.latitude
            st.session_state.user_lon = location.longitude
            st.sidebar.success(f"Found location: {st.session_state.user_lat:.6f}, {st.session_state.user_lon:.6f}")
            st.rerun()  # Force app to rerun for updates
        else:
            st.sidebar.error("Could not find location.")

else:
    lat = st.sidebar.number_input("Latitude", value=st.session_state.user_lat, format="%.6f", key="lat_input")
    lon = st.sidebar.number_input("Longitude", value=st.session_state.user_lon, format="%.6f", key="lon_input")

    if lat != st.session_state.user_lat or lon != st.session_state.user_lon:
        st.session_state.user_lat = lat
        st.session_state.user_lon = lon
        st.rerun()  # Ensure full recalculation when location changes

st.sidebar.header("⚙️ Filters")
max_dist = st.sidebar.slider("Max distance (km)", 0.1, 20.0, 10.0, 0.1)
fee_range = st.sidebar.slider("Fee range (€/h)", 0.0, 20.0, (0.0, 5.0), 0.1)
ev_only = st.sidebar.checkbox("Only EV charging spots")

# Add the Fuel Price Dashboard tab
tabs = st.tabs(["Map View", "Compare Parkings", "Fuel Prices", "Raw Data"])

with tabs[0]:
    render_map(st.session_state.user_lat, st.session_state.user_lon, max_dist, fee_range, ev_only)

with tabs[1]:
    render(st.session_state.user_lat, st.session_state.user_lon, max_dist, fee_range, ev_only)

with tabs[2]:
    render_fuel_dashboard()  # Call the Fuel Price Dashboard

with tabs[3]:
    st.header("📝 Raw Parking Data")
    st.warning("Data integration needs to be adjusted for consistency.")
