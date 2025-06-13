import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from math import radians, sin, cos, sqrt, atan2

@st.cache_data
def load_data():
    return pd.read_csv("parking_data.csv", encoding="latin1")

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1-a))

def filter_data(df, lat, lon, max_dist, fee_range, ev_only):
    df = df.dropna(subset=['latitude', 'longitude'])
    df['distance'] = df.apply(lambda r: haversine(lat, lon, r['latitude'], r['longitude']), axis=1)
    df = df[df['distance'] <= max_dist]
    df = df[df['fee_per_hour'].between(*fee_range)]
    if ev_only:
        df = df[df['ev_charging'] > 0]
    return df.sort_values('distance')

def create_map(lat, lon, df):
    m = folium.Map(location=[lat, lon], zoom_start=14)
    marker = folium.Marker([lat, lon], popup="Your Location", draggable=True, icon=folium.Icon(color="blue"))
    marker.add_to(m)

    for _, row in df.iterrows():
        folium.Marker([row['latitude'], row['longitude']], 
                      popup=f"{row['name']} - €{row['fee_per_hour']}/h",
                      icon=folium.Icon(color="red")).add_to(m)
    return m

def render_map(lat, lon, max_dist, fee_range, ev_only):
    df = load_data()
    filtered = filter_data(df, lat, lon, max_dist, fee_range, ev_only)

    # Create map
    map_obj = create_map(lat, lon, filtered)
    data = st_folium(map_obj, width=700, height=500)

    # Update location when pin moves
    if data.get("last_clicked"):
        lat = data["last_clicked"]["lat"]
        lon = data["last_clicked"]["lng"]
        filtered = filter_data(df, lat, lon, max_dist, fee_range, ev_only)
        st.success(f"New location set: {lat:.6f}, {lon:.6f}")

    if filtered.empty:
        st.warning("No matching parking spots.")
        return

    # Show list of matching parking spots under the map
    st.subheader("📍 Available Parking Spots")
    for _, row in filtered.iterrows():
        st.markdown(f"**🚗 {row['name']}** - €{row['fee_per_hour']}/h ({row['distance']:.2f} km)")
        st.markdown(f"[🗺️ Open in Google Maps](https://www.google.com/maps/search/?api=1&query={row['latitude']},{row['longitude']})")

    # Ensure only ONE map displays
    map_obj = create_map(lat, lon, filtered)
    st_folium(map_obj, width=700, height=500)
