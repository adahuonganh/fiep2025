import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from math import radians, sin, cos, sqrt, atan2
from geopy.geocoders import Nominatim
import requests
from datetime import datetime

@st.cache_data
def load_data():
    return pd.read_csv("parking_data.csv")

def render_map():
    df = load_data()

    def geocode_address(address):
        loc = Nominatim(user_agent="parking_finder").geocode(address)
        return (loc.latitude, loc.longitude) if loc else (None, None)

    def haversine(lat1, lon1, lat2, lon2):
        R = 6371
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat, dlon = lat2 - lat1, lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
        return R * 2 * atan2(sqrt(a), sqrt(1-a))

    def get_route(start_lon, start_lat, end_lon, end_lat):
        try:
            url = f"http://router.project-osrm.org/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}?overview=full&geometries=geojson"
            res = requests.get(url).json()
            if res['code'] == 'Ok':
                r = res['routes'][0]
                coords = [(lat, lon) for lon, lat in r['geometry']['coordinates']]
                return coords, r['distance'] / 1000, r['duration'] / 60
        except Exception as e:
            st.error(f"Routing error: {e}")
        return None, None, None

    def filter_data(df, lat, lon, max_dist, fee_range, ev_only):
        df = df.dropna(subset=['latitude', 'longitude'])
        if lat and lon:
            df['distance'] = df.apply(lambda r: haversine(lat, lon, r['latitude'], r['longitude']), axis=1)
            df = df[df['distance'] <= max_dist]
        df = df[df['fee_per_hour'].between(*fee_range)]
        if ev_only:
            df = df[df['ev_charging'] > 0]
        try:
            now = datetime.now().hour + datetime.now().minute / 60
            df = df[(df['opening_time'] <= now) & (df['closing_time'] >= now)]
        except:
            pass
        return df.sort_values('distance')

    def create_map(lat, lon, df, show_routes):
        m = folium.Map(location=[lat, lon], zoom_start=14)
        folium.Marker([lat, lon], popup=f"Your Location<br>Lat: {lat}<br>Lon: {lon}",
                      icon=folium.Icon(color="blue", icon="user", prefix="fa")).add_to(m)
        for _, row in df.iterrows():
            route, dist, dur = (None, None, None)
            if show_routes:
                route, dist, dur = get_route(lon, lat, row['longitude'], row['latitude'])

            popup = f"""
            <div style="width:250px">
                <h4>{row['name']}</h4>
                <b>Address:</b> {row['address']}<br>
                <b>Price:</b> €{row['fee_per_hour']:.1f}/h<br>
                <b>Distance:</b> {row.get('distance', 'N/A'):.1f} km<br>
                {f"<b>Route Distance:</b> {dist:.1f} km<br>" if dist else ""}
                {f"<b>Estimated Time:</b> {dur:.0f} min<br>" if dur else ""}
                <b>Spots:</b> {row['total_spots']}<br>
                <b>EV Charging:</b> {row['ev_charging']}<br>
                <a href="https://www.google.com/maps/dir/?api=1&origin={lat},{lon}&destination={row['latitude']},{row['longitude']}&travelmode=driving" target="_blank">🚗 Navigate</a>
            </div>
            """
            if route:
                folium.PolyLine(route, color='#4285F4', weight=3, opacity=0.7).add_to(m)
            folium.CircleMarker([row['latitude'], row['longitude']],
                                radius=6 + row['fee_per_hour'],
                                popup=folium.Popup(popup, max_width=300),
                                color='#FF5722', fill_color='#FF9800',
                                fill=True, fill_opacity=0.7).add_to(m)
        return m

    st.title("🚗 Smart Parking Finder")
    st.markdown("Find the perfect parking spot based on your location, budget, and preferences.")

    with st.sidebar:
        st.header("📍 Your Location")
        method = st.radio("Select method:", ["Drop pin on map", "Enter address", "Enter coordinates"])
        lat, lon = None, None

        if method == "Drop pin on map":
            lat, lon = 50.1109, 8.6821
            st.info("Drop a pin after closing the sidebar.")
        elif method == "Enter address":
            addr = st.text_input("Address or postal code:")
            if addr:
                lat, lon = geocode_address(addr)
                if lat: st.success(f"Found: {lat}, {lon}")
                else: st.error("Could not find location.")
        else:
            lat = st.number_input("Latitude", value=50.1109)
            lon = st.number_input("Longitude", value=8.6821)

        st.header("⚙️ Filters")
        max_dist = st.slider("Max distance (km)", 0.1, 20.0, 2.0, 0.1)
        fee = st.slider("Fee range (€/h)", 0.0, 10.0, (0.0, 5.0), 0.1)
        ev = st.checkbox("Only EV charging")

    if not lat or not lon:
        lat, lon = 50.1109, 8.6821

    filtered = filter_data(df, lat, lon, max_dist, fee, ev)

    if "selected_parking" in st.session_state:
        sel = st.session_state.selected_parking
        match = filtered[(filtered['name'] == sel['name']) & (filtered['address'] == sel['address'])]
        if match.empty:
            del st.session_state.selected_parking

    if "selected_parking" in st.session_state:
        selected_row = st.session_state.selected_parking.to_frame().T
    else:
        selected_row = filtered.iloc[[0]] if not filtered.empty else pd.DataFrame()

    st.subheader(f"🗺️ Found {len(filtered)} parking spots")

    if method == "Drop pin on map":
        pin_map = folium.Map(location=[lat, lon], zoom_start=14)
        folium.Marker([lat, lon], icon=folium.Icon(color="blue", icon="user", prefix="fa"), draggable=True).add_to(pin_map)
        data = st_folium(pin_map, key="pin_map", width=700, height=500)
        if data.get("last_clicked"):
            lat, lon = data["last_clicked"]["lat"], data["last_clicked"]["lng"]
            filtered = filter_data(df, lat, lon, max_dist, fee, ev)
            selected_row = filtered.iloc[[0]] if not filtered.empty else pd.DataFrame()
            st.success(f"Location set: {lat}, {lon}")

    if not selected_row.empty:
        map_obj = create_map(lat, lon, selected_row, show_routes=True)
        st_folium(map_obj, width=700, height=500)

    if not filtered.empty:
        st.subheader("📋 Matching Parking Spots")
        per_page = 5
        pages = (len(filtered) - 1) // per_page + 1
        page = st.number_input("Page", 1, pages, 1) if pages > 1 else 1
        start, end = (page-1)*per_page, page*per_page

        for idx, row in filtered.iloc[start:end].iterrows():
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{row['name']}**")
                    st.caption(f"{row['address']}")
                    st.caption(f"Distance: {row.get('distance', 'N/A'):.1f} km | Price: €{row['fee_per_hour']:.1f}/h")
                    st.caption(f"Location: {row['latitude']}, {row['longitude']}")
                with col2:
                    gmaps_link = f"https://www.google.com/maps/dir/?api=1&origin={lat},{lon}&destination={row['latitude']},{row['longitude']}&travelmode=driving"
                    st.markdown(f"[Navigate]({gmaps_link})", unsafe_allow_html=True)
                    if st.button("Select", key=f"select_{idx}"):
                        st.session_state.selected_parking = row
                        st.experimental_rerun()

        if pages > 1:
            st.caption(f"Page {page} of {pages}")
    else:
        st.warning("No parking spots match your criteria.")

    st.session_state.filtered_df = filtered
    st.session_state.user_location = (lat, lon)
