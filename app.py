import streamlit as st
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from map import render_map
from diagram import render
from fuel_dashboard import render_fuel_dashboard

st.set_page_config(
    page_title="ParkSmart All-in-One",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "user_lat" not in st.session_state:
    st.session_state.user_lat = 50.1270332
if "user_lon" not in st.session_state:
    st.session_state.user_lon = 8.6644491
if "page" not in st.session_state:
    st.session_state.page = 1

# --- Sidebar: Location Selection ---
st.sidebar.header("📍 Choose Your Location")
location_method = st.sidebar.radio("Select method:", ["Use coordinates", "Enter address/postal code"], index=0)

if location_method == "Use coordinates":
    with st.sidebar.form("coord_form"):
        lat = st.number_input("Latitude", value=st.session_state.user_lat, format="%.6f", key="lat_input")
        lon = st.number_input("Longitude", value=st.session_state.user_lon, format="%.6f", key="lon_input")
        submitted = st.form_submit_button("Update Location")
        if submitted:
            if (lat != st.session_state.user_lat) or (lon != st.session_state.user_lon):
                st.session_state.user_lat = lat
                st.session_state.user_lon = lon
                st.session_state.page = 1
                st.rerun()

elif location_method == "Enter address/postal code":
    with st.sidebar.form("address_form"):
        address_input = st.text_input("Enter address or postal code:")
        submitted = st.form_submit_button("Search")
        if submitted and address_input:
            try:
                geolocator = Nominatim(user_agent="parking_finder")
                geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
                location = geocode(address_input)
                if location:
                    st.session_state.user_lat = location.latitude
                    st.session_state.user_lon = location.longitude
                    st.session_state.page = 1
                    st.sidebar.success(f"Found location: {location.latitude:.6f}, {location.longitude:.6f}")
                    st.rerun()
                else:
                    st.sidebar.error("Could not find location.")
            except Exception as e:
                st.sidebar.error(f"Geocoding error: {e}")

# --- Sidebar: Filters ---
st.sidebar.header("⚙️ Filters")
with st.sidebar.form("filter_form"):
    max_dist = st.slider("Max distance (km)", 0.1, 20.0, 10.0, 0.1)
    fee_range = st.slider("Fee range (€/h)", 0.0, 20.0, (0.0, 5.0), 0.1)
    ev_only = st.checkbox("Only EV charging spots")
    sort_method = st.radio("Sort parking spots by:", ["Closest Distance", "Lowest Fee"])
    filter_submitted = st.form_submit_button("Apply Filters")
    if filter_submitted:
        st.session_state.page = 1
        st.rerun()

# --- Main Tabs ---
tabs = st.tabs(["Map View", "Compare Parkings", "Fuel Prices"])

with tabs[0]:
    render_map(
        st.session_state.user_lat,
        st.session_state.user_lon,
        max_dist,
        fee_range,
        ev_only,
        sort_method,
        st.session_state.page
    )

with tabs[1]:
    render(
        st.session_state.user_lat,
        st.session_state.user_lon,
        max_dist,
        fee_range,
        ev_only
    )

with tabs[2]:
    render_fuel_dashboard()
