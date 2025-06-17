import streamlit as st
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from map import parking_finder_tab
from diagram import insights_tab
from fuel_price import fuel_tab

# Initialize session state
def init_session_state():
    if "user_lat" not in st.session_state:
        st.session_state.user_lat = 50.1270332
    if "user_lon" not in st.session_state:
        st.session_state.user_lon = 8.6644491
    if "page" not in st.session_state:
        st.session_state.page = 1

# Common location selection sidebar
def location_sidebar():
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

def main():
    st.set_page_config(
        page_title="SmartPark",
        page_icon="🚗",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    init_session_state()
    location_sidebar()
    
    st.markdown('<h1 class="main-header">🚗 SmartPark</h1>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Parking Finder", "Insights", "Fuel Prices"])
    
    with tab1:
        parking_finder_tab()
    
    with tab2:
        insights_tab()
    
    with tab3:
        fuel_tab()

if __name__ == "__main__":
    main()
