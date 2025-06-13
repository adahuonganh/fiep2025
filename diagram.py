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
        df = pd.read_csv("parking_data.csv", encoding="latin1")

        df['open_time'] = df['open_time'].astype(str).str.zfill(2).replace("24", "00")
        df['close_time'] = df['close_time'].astype(str).str.zfill(2).replace("24", "23")
        df['open_time'] = pd.to_datetime(df['open_time'] + ":00", format="%H:%M").dt.time
        df['close_time'] = pd.to_datetime(df['close_time'] + ":59", format="%H:%M").dt.time

        df['ev_charging'] = pd.to_numeric(df['ev_charging'].replace('-', -1), errors='coerce').fillna(0)
        df['open_weekend'] = df['open_weekend'].astype(bool)
        df['cashless_payment'] = df['cashless_payment'].astype(bool)

        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

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

    # Fee per Hour
    st.markdown("### 💰 Fee per Hour")
    fig, ax = plt.subplots()
    sns.barplot(x=top5['name'], y=top5['fee_per_hour'], ax=ax, palette="Oranges_r")
    ax.set_ylabel("€/hour")
    ax.set_title("Fee per Hour")
    plt.xticks(rotation=45)
    st.pyplot(fig)

    # Travel Distance
    st.markdown("### 🚗 Travel Distance")
    fig, ax = plt.subplots()
    sns.barplot(x=top5['name'], y=top5['distance'], ax=ax, palette="Blues_d")
    ax.set_ylabel("Distance (km)")
    ax.set_title("Travel Distance")
    plt.xticks(rotation=45)
    st.pyplot(fig)

    # Spots Available
    st.markdown("### 🅿️ Total Spot Availability")
    fig, ax = plt.subplots()
    sns.barplot(x=top5['name'], y=top5['total_spots'], ax=ax, palette="Greens_d")
    ax.set_ylabel("Spots")
    ax.set_title("Total Spot Availability")
    plt.xticks(rotation=45)
    st.pyplot(fig)

def render(lat, lon, max_dist, fee_range, ev_only):
    df = load_data()
    filtered_df = filter_df(df, (lat, lon), max_dist, fee_range, ev_only)

    if filtered_df.empty:
        st.warning("No data available.")
        return

    show_comparison_charts(filtered_df)
