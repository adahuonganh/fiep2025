import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from math import radians, sin, cos, sqrt, atan2
from datetime import datetime
import pytz
from geopy.geocoders import Nominatim

TIMEZONE = 'Europe/Berlin'

def haversine(lat1, lon1, lat2, lon2):
    try:
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlon, dlat = lon2 - lon1, lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
        return 6371 * 2 * atan2(sqrt(a), sqrt(1-a))
    except:
        return float('inf')

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data/parking_data.csv")

        df['open_time'] = df['open_time'].astype(str).str.zfill(2).replace("24", "00")
        df['close_time'] = df['close_time'].astype(str).str.zfill(2).replace("24", "23")

        df['open_time'] = pd.to_datetime(df['open_time'] + ":00", format="%H:%M").dt.time
        df['close_time'] = pd.to_datetime(df['close_time'] + ":59", format="%H:%M").dt.time

        df['ev_charging'] = df['ev_charging'].replace('-', -1)
        df['ev_charging'] = pd.to_numeric(df['ev_charging'], errors='coerce').fillna(0)

        df['open_weekend'] = df['open_weekend'].astype(bool)
        df['cashless_payment'] = df['cashless_payment'].astype(bool)

        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

def geocode_address(address):
    loc = Nominatim(user_agent="parking_finder_compare").geocode(address)
    return (loc.latitude, loc.longitude) if loc else (None, None)

def filter_df(df, user_location, max_dist, fee_range, ev_only):
    if df.empty:
        return df

    now = datetime.now(pytz.timezone(TIMEZONE))
    current_time = now.time()
    current_day = now.strftime("%A")

    df['distance'] = df.apply(lambda r: haversine(user_location[0], user_location[1], r['latitude'], r['longitude']), axis=1)
    df = df[df['distance'] <= max_dist]
    df = df[df['fee_per_hour'].between(fee_range[0], fee_range[1])]

    df = df[df['open_time'] <= current_time]
    df = df[df['close_time'] >= current_time]

    if current_day in ['Saturday', 'Sunday']:
        df = df[df['open_weekend'] == True]

    if ev_only:
        df = df[df['ev_charging'] > 0]

    return df.sort_values('distance').reset_index(drop=True)

def show_comparison_charts(filtered_df):
    if filtered_df.empty:
        st.warning("No data to display.")
        return

    top5 = filtered_df.head(5)
    st.subheader("📊 Compare Top 5 Parking Options")

    tabs = st.tabs(["Fee", "Travel Time", "Spots Available"])

    with tabs[0]:
        fig, ax = plt.subplots()
        sns.barplot(x=top5['name'], y=top5['fee_per_hour'], ax=ax, palette="Oranges_r")
        ax.set_ylabel("€/hour")
        ax.set_title("Fee per Hour")
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        st.pyplot(fig)

    with tabs[1]:
        fig, ax = plt.subplots()
        sns.barplot(x=top5['name'], y=top5['distance'], ax=ax, palette="Blues_d")
        ax.set_ylabel("Distance (km)")
        ax.set_title("Travel Distance")
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        st.pyplot(fig)

    with tabs[2]:
        fig, ax = plt.subplots()
        sns.barplot(x=top5['name'], y=top5['total_spots'], ax=ax, palette="Greens_d")
        ax.set_ylabel("Spots")
        ax.set_title("Total Spot Availability")
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        st.pyplot(fig)

def main():
    st.title("📈 Parking Spot Comparison")

    df = load_data()

    # Sidebar to match map.py
    st.sidebar.header("📍 Your Location")
    method = st.sidebar.radio("Select method:", ["Drop pin on map", "Enter address", "Enter coordinates"])
    lat, lon = None, None

    if method == "Drop pin on map":
        lat, lon = 50.1109, 8.6821
        st.sidebar.info("Drop a pin after closing the sidebar.")
    elif method == "Enter address":
        addr = st.sidebar.text_input("Address or postal code:")
        if addr:
            lat, lon = geocode_address(addr)
            if lat:
                st.sidebar.success(f"Found: {lat:.6f}, {lon:.6f}")
            else:
                st.sidebar.error("Could not find location.")
    else:
        lat = st.sidebar.number_input("Latitude", value=50.1109, format="%.6f")
        lon = st.sidebar.number_input("Longitude", value=8.6821, format="%.6f")

    st.sidebar.header("⚙️ Filters")
    max_dist = st.sidebar.slider("Max distance (km)", 0.1, 20.0, 2.0, 0.1)
    fee_min, fee_max = st.sidebar.slider("Fee range (€/h)", 0.0, 10.0, (0.0, 5.0), 0.1)
    ev_only = st.sidebar.checkbox("Only EV charging spots")

    if lat is None or lon is None:
        lat, lon = 50.1109, 8.6821

    user_location = (lat, lon)
    filtered = filter_df(df, user_location, max_dist, (fee_min, fee_max), ev_only)

    st.success(f"Filtered {len(filtered)} parking spots.")
    show_comparison_charts(filtered)

if __name__ == "__main__":
    main()
