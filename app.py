import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from map import parking_finder_tab
from diagram import insights_tab
from fuel_dashboard import fuel_tab

st.set_page_config(
    page_title="SmartPark",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_data():
    df = pd.read_csv("parking_data.csv", encoding="utf-8")
    return df.rename(columns={"latitude": "lat", "longitude": "lon"})

# Initialize session state
def init_session_state():
    if "user_lat" not in st.session_state:
        st.session_state.user_lat = 50.1270332
    if "user_lon" not in st.session_state:
        st.session_state.user_lon = 8.6644491
    if "page" not in st.session_state:
        st.session_state.page = 1
    if "selected_city" not in st.session_state:
        st.session_state.selected_city = None

# Map city names to central coordinates
CITY_COORDS = {
    "Berlin": (52.5200, 13.4050),
    "Frankfurt am Main": (50.1109, 8.6821),
    "Hamburg": (53.5511, 9.9937),
    "München": (48.1351, 11.5820),
    "Köln": (50.9375, 6.9603),
}

# Sidebar for location selection
def location_sidebar(df):
    cities = sorted([c for c in df['city'].dropna().unique() if c in CITY_COORDS])
    st.sidebar.header("📍 Choose Your City")
    selected_city = st.sidebar.selectbox("City:", cities, index=0)
    st.session_state.selected_city = selected_city

    st.sidebar.header("📍 Choose Your Location")
    location_method = st.sidebar.radio("Select method:", ["City center", "Use coordinates", "Enter address/postal code"], index=0)

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

    elif location_method == "City center":
        if st.sidebar.button("🔍 Use city center location"):
            lat_lon = CITY_COORDS.get(selected_city)
            if lat_lon:
                lat, lon = lat_lon
                st.session_state.user_lat = lat
                st.session_state.user_lon = lon
                st.session_state.page = 1
                st.sidebar.success(f"Using city center: {lat:.6f}, {lon:.6f}")
                st.rerun()
            else:
                st.sidebar.error(f"No coordinates defined for '{selected_city}'.")

def filter_city(df):
    # Always filter by selected city for all tabs
    if "selected_city" in st.session_state and st.session_state.selected_city:
        return df[df['city'] == st.session_state.selected_city].reset_index(drop=True)
    return df

# Main app
def main():
    init_session_state()
    df = load_data()
    location_sidebar(df)
    city_df = filter_city(df)

    st.markdown('<h1 class="main-header">🚗 SmartPark</h1>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Parking Finder", "Insights", "Fuel Prices"])

    with tab1:
        parking_finder_tab(df)  # Use df directly, do NOT reload or filter by city here
    with tab2:
        insights_tab(df)  # Use df directly, do NOT reload or filter by city here
    with tab3:
        fuel_tab()

if __name__ == "__main__":
    main()
