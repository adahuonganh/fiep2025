import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests
from math import radians, sin, cos, sqrt, atan2
import plotly.express as px
import random

@st.cache_data
def load_parking_data():
    df = st.session_state.get("filtered_df", load_parking_data())
    # Ensure consistent column names
    df = df.rename(columns={
        'latitude': 'lat',
        'longitude': 'lon'
    })
    return df

def get_fun_fact():
    facts = [
        "🚗 The average car spends 95% of its time parked!",
        "🌱 One electric car can save 1.5 tons of CO2 per year compared to gasoline cars.",
        "🚴‍♀️ Cycling just 10km per week can save 1,600kg of CO2 annually.",
        "🏙️ Smart parking systems can reduce urban traffic by up to 30%.",
        "⚡ Germany has over 60,000 public EV charging points.",
        "🚊 Public transport in German cities is 5x more efficient than private cars."
    ]
    return random.choice(facts)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
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
            return coords, r['distance']/1000, r['duration']/60
    except Exception as e:
        st.error(f"Routing error: {e}")
    return None, None, None

def filter_data(df, lat, lon, max_dist, fee_range, ev_only, open_weekend, cashless_payment):
    # Make a copy of the DataFrame
    df = df.copy()
    
    # Clean boolean columns
    for col in ['open_weekend', 'open_holidays', 'ev_charging', 'cashless_payment']:
        if col in df.columns:
            df[col] = df[col].fillna(False).astype(bool)
    
    # Calculate distances
    df['distance'] = df.apply(
        lambda r: haversine(lat, lon, r['lat'], r['lon']), 
        axis=1
    )
    
    # Apply filters
    df = df[df['distance'] <= max_dist]
    df = df[df['fee_per_hour'].between(*fee_range)]
    if ev_only: 
        df = df[df['ev_charging']]
    if open_weekend: 
        df = df[df['open_weekend']]
    if cashless_payment: 
        df = df[df['cashless_payment']]
    
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
        folium.CircleMarker(
            [row['lat'], row['lon']],
            radius=6 + row['fee_per_hour'],
            popup=folium.Popup(popup, max_width=300),
            color='#FF5722',
            fill_color='#FF9800',
            fill=True,
            fill_opacity=0.7
        ).add_to(m)
    return m

def parking_finder_tab():
    df = load_parking_data()
    
    st.sidebar.header("⚙️ Filters")
    with st.sidebar.form("filter_form"):
        max_dist = st.slider("Max distance (km)", 0.1, 20.0, 10.0, 0.1)
        fee_range = st.slider("Fee range (€/h)", 0.0, 20.0, (0.0, 5.0), 0.1)
        ev_only = st.checkbox("EV charging spots")
        open_weekend = st.checkbox("Open on weekends")
        cashless_payment = st.checkbox("Cashless payment")
        sort_method = st.radio("Sort parking spots by:", ["Closest Distance", "Lowest Fee"])
        filter_submitted = st.form_submit_button("Apply Filters")
        
        if filter_submitted:
            st.session_state.max_dist = max_dist
            st.session_state.fee_range = fee_range
            st.session_state.ev_only = ev_only
            st.session_state.open_weekend = open_weekend
            st.session_state.cashless_payment = cashless_payment
            st.session_state.page = 1
            st.rerun()

    # Show fun fact above the map
    st.markdown(
        f"""
        <div style="
            padding: 0.5rem 1rem;
            background-color: var(--secondary-background-color);
            color: var(--text-color);
            border-radius: 0.5rem;
            border-left: 4px solid #4e8cff;
            margin: 1rem 0;
            font-size: 1.1rem;
            box-shadow: 0 1px 3px rgba(240,242,246,1);
        ">
            💡 <strong>Did you know?</strong><br>
            {get_fun_fact()}
        </div>
        """, 
        unsafe_allow_html=True
    )   
    
    filtered = filter_data(
        df,
        st.session_state.user_lat,
        st.session_state.user_lon,
        max_dist,
        fee_range,
        ev_only,
        open_weekend,
        cashless_payment
    )

    # Display map
    map_obj = create_map(st.session_state.user_lat, st.session_state.user_lon, filtered)
    st_folium(map_obj, width=700, height=500)

    # Statistics row below the map
    if not filtered.empty:
        avg_fee = filtered['fee_per_hour'].mean()
        total_spots = filtered['total_spots'].sum()
        avg_distance = filtered['distance'].mean()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 1.1rem; font-weight: 500; color: var(--system-label);">Average Fee</div>
                <div style="font-size: 1.5rem; font-weight: 600; color: var(--system-blue);">€{avg_fee:.2f}/hour</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 1.1rem; font-weight: 500; color: var(--system-label);">Total Spots</div>
                <div style="font-size: 1.5rem; font-weight: 600; color: var(--system-blue);">{total_spots:,}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 1.1rem; font-weight: 500; color: var(--system-label);">Avg Distance</div>
                <div style="font-size: 1.5rem; font-weight: 600; color: var(--system-green);">{avg_distance:.1f} km</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("No matching parking spots found.")

    # Apply sorting
    if not filtered.empty:
        if sort_method == "Closest Distance":
            filtered = filtered.sort_values('distance')
        elif sort_method == "Lowest Fee":
            filtered = filtered.sort_values('fee_per_hour')
        filtered = filtered.reset_index(drop=True)

    # Pagination
    if 'page' not in st.session_state:
        st.session_state.page = 1
    start_idx = (st.session_state.page - 1) * 10
    end_idx = start_idx + 10
    total_pages = (len(filtered) - 1) // 10 + 1

    # Display parking spots list
    st.subheader("📍 Available Parking Spots")
    for _, row in filtered.iloc[start_idx:end_idx].iterrows():
        with st.expander(f"🚗 {row['name']} - €{row['fee_per_hour']}/h ({row['distance']:.2f} km)"):
            col1, col2 = st.columns([1, 1])
            with col1:
                st.markdown(f"**📍 Address:** {row['address']}")
                st.markdown(f"**💰 Price:** €{row['fee_per_hour']}/hour")
                st.markdown(f"**📏 Distance:** {row['distance']:.2f} km")
                st.markdown(f"**🅿️ Total Spots:** {row['total_spots']}")
            with col2:
                st.markdown(f"**⚡ EV Charging:** {'✅ Yes' if row['ev_charging'] else '❌ No'}")
                st.markdown(f"**📅 Open Weekends:** {'✅ Yes' if row['open_weekend'] else '❌ No'}")
                st.markdown(f"**💳 Cashless Payment:** {'✅ Yes' if row['cashless_payment'] else '❌ No'}")
                if 'opening_hours' in row:
                    st.markdown(f"**🕒 Hours:** {row['opening_hours']}")
            st.markdown(
                f"[🗺️ Open in Google Maps](https://www.google.com/maps/dir/?api=1&origin={st.session_state.user_lat},{st.session_state.user_lon}&destination={row['lat']},{row['lon']}&travelmode=driving)",
                unsafe_allow_html=True
            )

    # Pagination controls
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅️ Previous", disabled=st.session_state.page == 1):
            st.session_state.page -= 1
            st.rerun()
    with col2:
        st.markdown(f"**Page {st.session_state.page} of {total_pages}**", unsafe_allow_html=True)
    with col3:
        if st.button("➡️ Next", disabled=st.session_state.page >= total_pages):
            st.session_state.page += 1
            st.rerun()

def main():
    st.title("🚗 Parking Finder App")
    
    # Initialize session state for user location if not exists
    if 'user_lat' not in st.session_state or 'user_lon' not in st.session_state:
        st.session_state.user_lat = 52.5200  # Default Berlin coordinates
        st.session_state.user_lon = 13.4050
    
    parking_finder_tab()

if __name__ == "__main__":
    main()
