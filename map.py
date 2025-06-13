import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from math import radians, sin, cos, sqrt, atan2
import requests
from datetime import datetime

@st.cache_data
def load_data():
    return pd.read_csv("parking_data.csv", encoding="latin1")

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

def filter_data(df, lat, lon, max_dist, fee_range, ev_only, sort_method):
    df = df.dropna(subset=['latitude', 'longitude'])
    df['distance'] = df.apply(lambda r: haversine(lat, lon, r['latitude'], r['longitude']), axis=1)
    df = df[df['distance'] <= max_dist]
    df = df[df['fee_per_hour'].between(*fee_range)]
    if ev_only:
        df = df[df['ev_charging'] > 0]

    df = df.sort_values('distance' if sort_method == "Closest Distance" else 'fee_per_hour')
    return df

def create_map(lat, lon, df):
    m = folium.Map(location=[lat, lon], zoom_start=14)
    folium.Marker([lat, lon], popup="Your Location", icon=folium.Icon(color="blue")).add_to(m)

    for _, row in df.iterrows():
        route, dist, dur = get_route(lon, lat, row['longitude'], row['latitude'])

        popup = f"""
        <div style="width:250px">
            <h4>{row['name']}</h4>
            <b>Address:</b> {row['address']}<br>
            <b>Price:</b> €{row['fee_per_hour']:.1f}/h<br>
            <b>Distance:</b> {row['distance']:.1f} km<br>
            <b>Spots:</b> {row['total_spots']}<br>
            <b>EV Charging:</b> {row['ev_charging']}<br>
            {f"<b>Route Distance:</b> {dist:.1f} km<br>" if dist else ""}
            {f"<b>Estimated Time:</b> {dur:.0f} min<br>" if dur else ""}
            <a href="https://www.google.com/maps/dir/?api=1&origin={lat},{lon}&destination={row['latitude']},{row['longitude']}&travelmode=driving" target="_blank">🚗 Navigate</a>
        </div>
        """
        folium.CircleMarker([row['latitude'], row['longitude']],
                            radius=6 + row['fee_per_hour'],
                            popup=folium.Popup(popup, max_width=300),
                            color='#FF5722', fill_color='#FF9800',
                            fill=True, fill_opacity=0.7).add_to(m)

    return m

def render_map(lat, lon, max_dist, fee_range, ev_only, sort_method, page):
    df = load_data()
    filtered = filter_data(df, lat, lon, max_dist, fee_range, ev_only, sort_method)

    if filtered.empty:
        st.warning("No matching parking spots.")
        return

    start_idx = (page - 1) * 10
    end_idx = start_idx + 10
    total_pages = (len(filtered) - 1) // 10 + 1

    map_obj = create_map(lat, lon, filtered.iloc[start_idx:end_idx])
    st_folium(map_obj, width=700, height=500)

    st.subheader("📍 Available Parking Spots")
    for _, row in filtered.iloc[start_idx:end_idx].iterrows():
        st.markdown(f"**🚗 {row['name']}** - €{row['fee_per_hour']}/h ({row['distance']:.2f} km)")
        st.markdown(f"[🗺️ Open in Google Maps](https://www.google.com/maps/dir/?api=1&origin={lat},{lon}&destination={row['latitude']},{row['longitude']}&travelmode=driving)")

    if st.button("⬅️ Previous", disabled=page == 1):
        st.session_state.page -= 1
        st.rerun()
    
    if st.button("➡️ Next", disabled=page >= total_pages):
        st.session_state.page += 1
        st.rerun()
