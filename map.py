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
    R = 6371  # Earth radius in km
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
    folium.Marker([lat, lon], popup="Your Location", icon=folium.Icon(color="blue")).add_to(m)
    for _, row in df.iterrows():
        folium.Marker([row['latitude'], row['longitude']], 
                      popup=f"{row['name']} - €{row['fee_per_hour']}/h",
                      icon=folium.Icon(color="red")).add_to(m)
    return m

def render_map(lat, lon, max_dist, fee_range, ev_only):
    df = load_data()
    filtered = filter_data(df, lat, lon, max_dist, fee_range, ev_only)

    if filtered.empty:
        st.warning("No matching parking spots.")
        return

    map_obj = create_map(lat, lon, filtered)
    st_folium(map_obj, width=700, height=500)
