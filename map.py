import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests
from math import radians, sin, cos, sqrt, atan2

@st.cache_data
def load_parking_data():
    df = pd.read_csv("parking_data.csv")
    df = df.rename(columns={'latitude': 'lat', 'longitude': 'lon'})
    for col in ['open_weekend', 'open_holidays', 'ev_charging', 'cashless_payment']:
        if col in df.columns:
            df[col] = df[col].fillna(False).astype(bool)
    df['available_spots'] = df.apply(lambda x: random.randint(1, x['total_spots']), axis=1)
    df['opening_hours'] = df.apply(lambda x: f"{x['open_time']} - {x['close_time']}", axis=1)
    return df

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
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

def filter_data(df, lat, lon, max_dist, fee_range, ev_only, open_weekend, cashless_payment):
    df = df.dropna(subset=['lat', 'lon'])
    df['distance'] = df.apply(lambda r: haversine(lat, lon, r['lat'], r['lon']), axis=1)
    df = df[df['distance'] <= max_dist]
    df = df[df['fee_per_hour'].between(*fee_range)]
    if ev_only: df = df[df['ev_charging'] == True]
    if open_weekend: df = df[df['open_weekend'] == True]
    if cashless_payment: df = df[df['cashless_payment'] == True]
    return df

def create_map(lat, lon, df):
    m = folium.Map(location=[lat, lon], zoom_start=14)
    folium.Marker([lat, lon], popup="Your Location", icon=folium.Icon(color="blue")).add_to(m)

    for _, row in df.iterrows():
        route, dist, dur = get_route(lon, lat, row['lon'], row['lat'])
        popup = f"""
        <div style="width:250px">
            <h4>{row['name']}</h4>
            <b>Address:</b> {row['address']}<br>
            <b>Price:</b> €{row['fee_per_hour']:.1f}/h<br>
            <b>Distance:</b> {row['distance']:.1f} km<br>
            <b>Spots:</b> {row['total_spots']}<br>
            <b>EV Charging:</b> {'Yes' if row['ev_charging'] else 'No'}<br>
            {f"<b>Route Distance:</b> {dist:.1f} km<br>" if dist else ""}
            {f"<b>Estimated Time:</b> {dur:.0f} min<br>" if dur else ""}
            <a href="https://www.google.com/maps/dir/?api=1&origin={lat},{lon}&destination={row['lat']},{row['lon']}&travelmode=driving" target="_blank">🚗 Navigate</a>
        </div>
        """
        folium.CircleMarker([row['lat'], row['lon']],
                          radius=6 + row['fee_per_hour'],
                          popup=folium.Popup(popup, max_width=300),
                          color='#FF5722', fill_color='#FF9800',
                          fill=True, fill_opacity=0.7).add_to(m)
    return m

def parking_finder_tab():
    df = load_parking_data()
    
    st.sidebar.header("⚙️ Filters")
    with st.sidebar.form("filter_form"):
        max_dist = st.slider("Max distance (km)", 0.1, 20.0, 10.0, 0.1)
        fee_range = st.slider("Fee range (€/h)", 0.0, 20.0, (0.0, 5.0), 0.1)
        ev_only = st.checkbox("Only EV charging spots")
        open_weekend = st.checkbox("Only open on weekends")
        cashless_payment = st.checkbox("Only cashless payment")
        sort_method = st.radio("Sort parking spots by:", ["Closest Distance", "Lowest Fee"])
        filter_submitted = st.form_submit_button("Apply Filters")
        if filter_submitted:
            st.session_state.page = 1
            st.rerun()

    filtered = filter_data(df, st.session_state.user_lat, st.session_state.user_lon, 
                         max_dist, fee_range, ev_only, open_weekend, cashless_payment)

    if filtered.empty:
        st.warning("No matching parking spots.")
        return

    start_idx = (st.session_state.page - 1) * 10
    end_idx = start_idx + 10
    total_pages = (len(filtered) - 1) // 10 + 1

    map_obj = create_map(st.session_state.user_lat, st.session_state.user_lon, filtered.iloc[start_idx:end_idx])
    st_folium(map_obj, width=700, height=500)

    st.subheader("📍 Available Parking Spots")
    for _, row in filtered.iloc[start_idx:end_idx].iterrows():
        with st.expander(f"🚗 {row['name']} - €{row['fee_per_hour']}/h ({row['distance']:.2f} km)"):
            st.markdown(f"**Address:** {row['address']}")
            st.markdown(f"**Price:** €{row['fee_per_hour']}/hour")
            st.markdown(f"**Distance:** {row['distance']:.2f} km")
            st.markdown(f"**Total Spots:** {row['total_spots']}")
            st.markdown(f"**Available Now:** {row['available_spots']}")
            st.markdown(f"**EV Charging:** {'Yes' if row['ev_charging'] else 'No'}")
            st.markdown(f"**Open on Weekends:** {'Yes' if row['open_weekend'] else 'No'}")
            st.markdown(f"**Cashless Payment:** {'Yes' if row['cashless_payment'] else 'No'}")
            st.markdown(f"[🗺️ Open in Google Maps](https://www.google.com/maps/dir/?api=1&origin={st.session_state.user_lat},{st.session_state.user_lon}&destination={row['lat']},{row['lon']}&travelmode=driving)")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅️ Previous", disabled=st.session_state.page == 1):
            st.session_state.page -= 1
            st.rerun()
    with col3:
        if st.button("➡️ Next", disabled=st.session_state.page >= total_pages):
            st.session_state.page += 1
            st.rerun()
    with col2:
        st.markdown(f"**Page {st.session_state.page} of {total_pages}**", unsafe_allow_html=True)
