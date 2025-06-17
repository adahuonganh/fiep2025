import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import st_folium
import numpy as np
import random
from datetime import datetime, timedelta
import math

# Set page config
st.set_page_config(
    page_title="SmartMobility",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apple-inspired CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;400;500;600&display=swap');

:root {
    --system-blue: #0A84FF;
    --system-green: #30D158;
    --system-red: #FF453A;
    --system-orange: #FF9F0A;
    --system-purple: #BF5AF2;
    --system-gray: #8E8E93;
    --system-background: #F2F2F7;
    --system-card: #FFFFFF;
    --system-label: #3C3C43;
}

* {
    font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
}

.main-header {
    font-size: 2.8rem;
    font-weight: 600;
    text-align: center;
    color: var(--system-label);
    margin-bottom: 1.5rem;
    letter-spacing: -0.5px;
}

.section-header {
    font-size: 1.5rem;
    font-weight: 500;
    color: var(--system-label);
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(0,0,0,0.1);
}

.metric-card {
    background-color: var(--system-card);
    padding: 1.25rem;
    border-radius: 12px;
    margin: 0.75rem 0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    border-left: 4px solid var(--system-blue);
}

.fun-fact {
    background: linear-gradient(135deg, #007AFF 0%, #34C759 100%);
    color: white;
    padding: 1.25rem;
    border-radius: 12px;
    margin: 1rem 0;
    box-shadow: 0 4px 12px rgba(0,122,255,0.15);
}

.tab-content {
    padding: 1rem 0;
}

/* Apple-style buttons */
.stButton>button {
    border-radius: 10px;
    border: none;
    background-color: var(--system-blue);
    color: white;
    padding: 0.5rem 1rem;
    font-weight: 500;
    transition: all 0.2s;
}

.stButton>button:hover {
    background-color: #0071E3;
    transform: translateY(-1px);
}

/* Apple-style select boxes */
.stSelectbox>div>div>select {
    border-radius: 10px;
    padding: 0.5rem;
    border: 1px solid rgba(0,0,0,0.1);
}

/* Apple-style sliders */
.stSlider>div>div>div>div {
    background-color: var(--system-blue) !important;
}

/* Map container */
.map-container {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

/* Apple-style tabs */
.stTabs>div>div>div>div {
    padding: 0.5rem 1rem;
    border-radius: 10px 10px 0 0;
}

.stTabs>div>div>div>div[aria-selected="true"] {
    background-color: var(--system-blue);
    color: white;
}

/* Data table styling */
.stDataFrame {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

# Data functions (unchanged from original)
@st.cache_data
def load_parking_data():
    cologne_data = [
        {'name': 'Parkhaus Opern Passagen', 'address': 'Schwertnergasse 1, 50667 Köln', 'postal_code': '50667', 'lat': 50.9386, 'lon': 6.9482, 'fee_per_hour': 2.5, 'ev_charging': True, 'total_spots': 350, 'available_spots': 45, 'opening_hours': 'Tag und Nacht geöffnet'},
        {'name': 'Tiefgarage Hauptbahnhof', 'address': 'Am Alten Ufer, 50667 Köln', 'postal_code': '50667', 'lat': 50.9429, 'lon': 6.9581, 'fee_per_hour': 3.0, 'ev_charging': True, 'total_spots': 500, 'available_spots': 78, 'opening_hours': '00:00 - 24:00'},
        {'name': 'Tiefgarage Neptunplatz', 'address': 'Neptunstraße, 50823 Köln', 'postal_code': '50823', 'lat': 50.9472, 'lon': 6.9231, 'fee_per_hour': 2.0, 'ev_charging': False, 'total_spots': 200, 'available_spots': 34, 'opening_hours': 'Mo-Sa: 07:00-01:00, So: 09:00-01:00'},
        {'name': 'Parkhaus Hauptbahnhof Altstadt-Nord P7', 'address': 'Am Alten Ufer 35, 50668 Köln', 'postal_code': '50668', 'lat': 50.9435, 'lon': 6.9578, 'fee_per_hour': 3.5, 'ev_charging': True, 'total_spots': 400, 'available_spots': 120, 'opening_hours': 'Tag und Nacht geöffnet'},
        {'name': 'Parkplatz Maximinenstraße P2', 'address': 'Maximinenstraße, 50668 Köln', 'postal_code': '50668', 'lat': 50.9418, 'lon': 6.9602, 'fee_per_hour': 2.0, 'ev_charging': False, 'total_spots': 150, 'available_spots': 23, 'opening_hours': 'Tag und Nacht geöffnet'},
        {'name': 'Tiefgarage MesseCity', 'address': 'Deutzer Allee 1, 50679 Köln', 'postal_code': '50679', 'lat': 50.9422, 'lon': 6.9854, 'fee_per_hour': 2.8, 'ev_charging': True, 'total_spots': 600, 'available_spots': 156, 'opening_hours': 'Tag und Nacht geöffnet'},
        {'name': 'Tiefgarage Am Dom', 'address': 'Kurt-Hackenbergplatz 2, 50667 Köln', 'postal_code': '50667', 'lat': 50.9413, 'lon': 6.9581, 'fee_per_hour': 3.2, 'ev_charging': True, 'total_spots': 450, 'available_spots': 89, 'opening_hours': 'Tag und Nacht geöffnet'},
        {'name': 'Tiefgarage Heumarkt', 'address': 'Markmannsgasse 3, 50667 Köln', 'postal_code': '50667', 'lat': 50.9364, 'lon': 6.9605, 'fee_per_hour': 2.5, 'ev_charging': False, 'total_spots': 300, 'available_spots': 45, 'opening_hours': '00:00 - 24:00'},
        {'name': 'Tiefgarage Mülheim', 'address': 'Jan-Wellem-Straße 2, 51065 Köln', 'postal_code': '51065', 'lat': 50.9632, 'lon': 7.0078, 'fee_per_hour': 1.8, 'ev_charging': False, 'total_spots': 250, 'available_spots': 67, 'opening_hours': '06:00 - 24:00'},
        {'name': 'Tiefgarage Am Willy-Millowitsch-Platz', 'address': 'Breite Str. 169-177, 50667 Köln', 'postal_code': '50667', 'lat': 50.9335, 'lon': 6.9524, 'fee_per_hour': 2.2, 'ev_charging': True, 'total_spots': 180, 'available_spots': 12, 'opening_hours': 'Mo-Fr: 08:00-20:00, Sa: 08:00-20:00, So: geschlossen'}
    ]
    
    data = {
        'Berlin': [
            {'name': 'Tiefgarage Plaza', 'address': 'Mildred-Harnack-Straße 11-13, 10243 Berlin', 'postal_code': '10243', 'lat': 52.5170, 'lon': 13.4015, 'fee_per_hour': 2.5, 'ev_charging': True, 'total_spots': 400, 'available_spots': 45, 'opening_hours': '24/7'},
            {'name': 'Parkhaus Spandau Altstädter Ring', 'address': 'Altstädter Ring 20, 13597 Berlin', 'postal_code': '13597', 'lat': 52.5350, 'lon': 13.2050, 'fee_per_hour': 1.5, 'ev_charging': False, 'total_spots': 300, 'available_spots': 78, 'opening_hours': '06:00-22:00'},
            {'name': 'Tiefgarage Hauptbahnhof P1', 'address': 'Clara-Jaschke-Straße 88, 10557 Berlin', 'postal_code': '10557', 'lat': 52.5250, 'lon': 13.3693, 'fee_per_hour': 3.0, 'ev_charging': True, 'total_spots': 814, 'available_spots': 120, 'opening_hours': '24/7'},
            {'name': 'Parkhaus Europa-Center', 'address': 'Nürnberger Straße 5-7, 10787 Berlin', 'postal_code': '10787', 'lat': 52.5044, 'lon': 13.3347, 'fee_per_hour': 2.8, 'ev_charging': True, 'total_spots': 954, 'available_spots': 230, 'opening_hours': '24/7'}
        ],
        'Munich': [
            {'name': 'Tiefgarage Hauptbahnhof Süd P4', 'address': 'Senefelderstraße, 80336 München', 'postal_code': '80336', 'lat': 48.1374, 'lon': 11.5588, 'fee_per_hour': 3.0, 'ev_charging': False, 'total_spots': 242, 'available_spots': 34, 'opening_hours': '06:00-22:00'},
            {'name': 'Tiefgarage Stachus', 'address': 'Herzog-Wilhelm-Straße 11, 80331 München', 'postal_code': '80331', 'lat': 48.1395, 'lon': 11.5661, 'fee_per_hour': 2.8, 'ev_charging': False, 'total_spots': 700, 'available_spots': 89, 'opening_hours': '06:00-24:00'},
            {'name': 'Tiefgarage Marienplatz', 'address': 'Rindermarkt 16, 80331 München', 'postal_code': '80331', 'lat': 48.1374, 'lon': 11.5755, 'fee_per_hour': 3.2, 'ev_charging': True, 'total_spots': 265, 'available_spots': 12, 'opening_hours': '07:00-20:00'}
        ],
        'Hamburg': [
            {'name': 'Tiefgarage Am Sandtorkai', 'address': 'Singapurstraße Haus 2, 20457 Hamburg', 'postal_code': '20457', 'lat': 53.5438, 'lon': 9.9955, 'fee_per_hour': 2.2, 'ev_charging': True, 'total_spots': 277, 'available_spots': 56, 'opening_hours': '24/7'},
            {'name': 'Parkhaus Speicherstadt', 'address': 'Am Sandtorkai 6, 20457 Hamburg', 'postal_code': '20457', 'lat': 53.5441, 'lon': 9.9899, 'fee_per_hour': 2.5, 'ev_charging': False, 'total_spots': 814, 'available_spots': 145, 'opening_hours': '06:00-24:00'},
            {'name': 'Tiefgarage Europa Passage', 'address': 'Hermannstraße 11, 20095 Hamburg', 'postal_code': '20095', 'lat': 53.5511, 'lon': 10.0006, 'fee_per_hour': 2.8, 'ev_charging': False, 'total_spots': 720, 'available_spots': 98, 'opening_hours': '09:00-21:00'}
        ],
        'Frankfurt': [
            {'name': 'Tiefgarage Alte Oper', 'address': 'Opernplatz 1, 60313 Frankfurt am Main', 'postal_code': '60313', 'lat': 50.1188, 'lon': 8.6719, 'fee_per_hour': 2.5, 'ev_charging': True, 'total_spots': 402, 'available_spots': 67, 'opening_hours': '24/7'},
            {'name': 'Parkhaus Börse', 'address': 'Meisengasse, 60313 Frankfurt am Main', 'postal_code': '60313', 'lat': 50.1136, 'lon': 8.6797, 'fee_per_hour': 2.5, 'ev_charging': True, 'total_spots': 891, 'available_spots': 134, 'opening_hours': '06:00-24:00'},
            {'name': 'Tiefgarage Hauptbahnhof Nord P1', 'address': 'Poststraße 3, 60329 Frankfurt am Main', 'postal_code': '60329', 'lat': 50.1072, 'lon': 8.6647, 'fee_per_hour': 4.0, 'ev_charging': True, 'total_spots': 365, 'available_spots': 89, 'opening_hours': '24/7'}
        ],
        'Cologne': cologne_data
    }
    
    all_data = [dict(spot, city=city) for city, spots in data.items() for spot in spots]
    return pd.DataFrame(all_data)

@st.cache_data
def load_fuel_prices():
    # Read the CSV data directly
    df = pd.read_csv("fuel_price.csv", sep=";", skiprows=5)
    
    # Clean the data
    df = df.rename(columns={'Datum': 'date', 'Super E10': 'e10', 'Diesel': 'diesel', 'Super E5': 'e5'})
    df['date'] = pd.to_datetime(df['date'])
    
    # Convert comma decimal separators to dots and convert to float
    for col in ['e10', 'diesel', 'e5']:
        df[col] = df[col].str.replace(',', '.').astype(float)
    
    # Set date as index
    df = df.set_index('date')
    
    # Rename columns to match your original code
    df = df.rename(columns={
        'e10': 'Super E10',
        'diesel': 'Diesel',
        'e5': 'Super E5'
    })
    
    return df

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth's radius in km
    lat1_rad, lat2_rad = math.radians(lat1), math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def generate_co2_data():
    return {
        'Car (Gasoline)': 120, 'Car (Diesel)': 110, 'Electric Car': 30, 'Hybrid Car': 80,
        'Public Transport': 25, 'Bicycle': 0, 'Walking': 0, 'E-Scooter': 15
    }

def get_fun_fact():
    facts = [
        "🚗 The average car spends 95% of its time parked!",
        "🌱 One electric car can save 1.5 tons of CO2 per year compared to gasoline cars.",
        "🚴‍♀️ Cycling just 10km per week can save 1,600kg of CO2 annually.",
        "🏙️ Smart parking systems can reduce urban traffic by up to 30%.",
        "⚡ Germany has over 60,000 public EV charging points.",
        "🚊 Public transport in German cities is 5x more efficient than private cars.",
        "🌍 Transportation accounts for 24% of global CO2 emissions.",
        "🅿️ Dynamic parking pricing can reduce search time by 43%."
    ]
    return random.choice(facts)

def create_apple_gauge(value, max_value, color, title):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title, 'font': {'size': 16}},
        gauge = {
            'axis': {'range': [0, max_value], 'tickwidth': 1, 'tickcolor': "var(--system-label)"},
            'bar': {'color': color},
            'bgcolor': "var(--system-card)",
            'borderwidth': 0,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, max_value*0.6], 'color': '#D1E7DD'},
                {'range': [max_value*0.6, max_value*0.8], 'color': '#FFF3CD'},
                {'range': [max_value*0.8, max_value], 'color': '#F8D7DA'}],
            'threshold': {
                'line': {'color': color, 'width': 4},
                'thickness': 0.75,
                'value': value}
        }
    ))
    fig.update_layout(
        margin=dict(l=30, r=30, t=50, b=30),
        height=250,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'family': 'SF Pro Display, sans-serif'}
    )
    return fig

def parking_tab():
    df = load_parking_data()
    
    st.sidebar.title("📍 Location & Preferences")
    selected_city = st.sidebar.selectbox("Select City", ["Berlin", "Munich", "Hamburg", "Frankfurt", "Cologne"])
    
    st.sidebar.subheader("Current Location")
    location_method = st.sidebar.radio("Input method:", ["City Center", "Postal Code", "Coordinates"])
    
    if location_method == "Postal Code":
        postal_code = st.sidebar.text_input("Enter Postal Code", "10117")
        user_lat, user_lon = 52.5200, 13.4050
    elif location_method == "Coordinates":
        user_lat = st.sidebar.number_input("Latitude", value=52.5200, step=0.0001, format="%.4f")
        user_lon = st.sidebar.number_input("Longitude", value=13.4050, step=0.0001, format="%.4f")
    else:
        city_coords = {
            "Berlin": (52.5200, 13.4050), "Munich": (48.1351, 11.5820), "Hamburg": (53.5511, 9.9937),
            "Frankfurt": (50.1109, 8.6821), "Cologne": (50.9375, 6.9603)
        }
        user_lat, user_lon = city_coords[selected_city]
    
    st.sidebar.subheader("Filters")
    max_fee = st.sidebar.slider("Maximum Fee per Hour (€)", 0.0, 5.0, 3.0, 0.1)
    transport_types = st.sidebar.multiselect(
        "Transportation Types",
        ["Car (Gasoline)", "Car (Diesel)", "Electric Car", "Hybrid Car", "Public Transport", "Bicycle", "E-Scooter"],
        default=["Car (Gasoline)", "Electric Car"]
    )
    ev_charging_required = st.sidebar.checkbox("Require EV Charging", value=False)
    max_distance = st.sidebar.slider("Maximum Distance (km)", 0.5, 10.0, 5.0, 0.5)
    user_profile = st.sidebar.selectbox("Select User Type", ["Commuter", "Tourist", "Delivery Driver", "Business Traveler"])
    
    city_df = df[df['city'] == selected_city].copy()
    filtered_df = city_df[(city_df['fee_per_hour'] <= max_fee) & (city_df['ev_charging'] >= ev_charging_required)].copy()
    filtered_df['distance'] = filtered_df.apply(lambda row: calculate_distance(user_lat, user_lon, row['lat'], row['lon']), axis=1)
    filtered_df = filtered_df[filtered_df['distance'] <= max_distance].sort_values('distance')
    
    st.markdown('<div class="section-header">🗺️ Parking Locations</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        center_lat, center_lon = (filtered_df[['lat', 'lon']].mean().values if not filtered_df.empty else (user_lat, user_lon))
        m = folium.Map(location=[center_lat, center_lon], zoom_start=12)
        folium.Marker(
            [user_lat, user_lon],
            popup="Your Location",
            icon=folium.Icon(color='red', icon='user', prefix='fa')
        ).add_to(m)
        
        for idx, row in filtered_df.iterrows():
            color = 'green' if row['available_spots'] > 50 else 'orange' if row['available_spots'] > 20 else 'red'
            popup_text = f"""
            <b>{row['name']}</b><br>
            Address: {row['address']}<br>
            Fee: €{row['fee_per_hour']}/hour<br>
            Available: {row['available_spots']}/{row['total_spots']}<br>
            Distance: {row['distance']:.1f} km<br>
            EV Charging: {'Yes' if row['ev_charging'] else 'No'}<br>
            Opening Hours: {row['opening_hours']}<br>
            <a href="https://www.google.com/maps/search/?api=1&query={row['lat']},{row['lon']}" target="_blank">📍 Open in Google Maps</a>
            """
            folium.Marker(
                [row['lat'], row['lon']],
                popup=folium.Popup(popup_text, max_width=300),
                icon=folium.Icon(color=color, icon='car', prefix='fa')
            ).add_to(m)
        
        st_folium(m, width=700, height=400)
    
    with col2:
        st.markdown('<div class="section-header">📊 Parking Stats</div>', unsafe_allow_html=True)
        
        if not filtered_df.empty:
            avg_fee = filtered_df['fee_per_hour'].mean()
            total_spots = filtered_df['total_spots'].sum()
            available_spots = filtered_df['available_spots'].sum()
            availability_rate = (available_spots / total_spots * 100) if total_spots > 0 else 0
            
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 1.1rem; font-weight: 500; color: var(--system-label);">Average Fee</div>
                <div style="font-size: 1.8rem; font-weight: 600; color: var(--system-blue);">€{avg_fee:.2f}/hour</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 1.1rem; font-weight: 500; color: var(--system-label);">Total Spots</div>
                <div style="font-size: 1.8rem; font-weight: 600; color: var(--system-blue);">{total_spots:,}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 1.1rem; font-weight: 500; color: var(--system-label);">Available Now</div>
                <div style="font-size: 1.8rem; font-weight: 600; color: var(--system-green);">{available_spots:,}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 1.1rem; font-weight: 500; color: var(--system-label);">Availability Rate</div>
                <div style="font-size: 1.8rem; font-weight: 600; color: { '#30D158' if availability_rate > 30 else '#FF9F0A' };">{availability_rate:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("No parking spots match your criteria.")
        
        st.markdown(f'<div class="fun-fact">**💡 Smart Tip**\n\n{get_fun_fact()}</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="section-header">📈 Mobility Insights</div>', unsafe_allow_html=True)
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        if not filtered_df.empty:
            fig_fee = px.bar(
                filtered_df.head(10),
                x='name',
                y='fee_per_hour',
                color='available_spots',
                title='Parking Fees Comparison',
                labels={'fee_per_hour': 'Fee (€/hour)', 'name': 'Parking Location'},
                color_continuous_scale='Tealgrn'
            )
            fig_fee.update_layout(
                xaxis_tickangle=-45,
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font={'family': 'SF Pro Display, sans-serif'}
            )
            st.plotly_chart(fig_fee, use_container_width=True)
    
    with chart_col2:
        co2_data = generate_co2_data()
        co2_df = pd.DataFrame(list(co2_data.items()), columns=['Transport', 'CO2_grams_per_km'])
        
        # Create Apple-style gauges for key transport modes
        st.plotly_chart(
            create_apple_gauge(
                co2_data['Car (Gasoline)'],
                150,
                '#FF453A',
                'Gasoline Car Emissions'
            ),
            use_container_width=True
        )
        
        st.plotly_chart(
            create_apple_gauge(
                co2_data['Electric Car'],
                150,
                '#30D158',
                'Electric Car Emissions'
            ),
            use_container_width=True
        )
    
    st.markdown('<div class="section-header">💰 Trip Calculator</div>', unsafe_allow_html=True)
    calc_col1, calc_col2, calc_col3 = st.columns(3)
    
    with calc_col1:
        trip_distance = st.number_input("Trip Distance (km)", min_value=0.1, value=5.0, step=0.1)
        parking_duration = st.number_input("Parking Duration (hours)", min_value=0.5, value=2.0, step=0.5)
    
    with calc_col2:
        fuel_type = st.selectbox("Fuel Type", ["Super E10", "Diesel", "Super E5"])
        fuel_df = load_fuel_prices()
        current_fuel_price = fuel_df[fuel_type].iloc[-1]
        
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 1.1rem; font-weight: 500; color: var(--system-label);">Current {fuel_type} Price</div>
            <div style="font-size: 1.5rem; font-weight: 600; color: var(--system-blue);">€{current_fuel_price:.2f}/L</div>
        </div>
        """, unsafe_allow_html=True)
        
        consumption = st.number_input("Fuel Consumption (L/100km)", min_value=3.0, value=7.5, step=0.1)
    
    with calc_col3:
        time_value = st.number_input("Time Value (€/hour)", min_value=5.0, value=15.0, step=1.0)
    
    if st.button("Calculate Trip Cost", key="calc_trip") and not filtered_df.empty:
        selected_parking = filtered_df.iloc[0]
        fuel_cost = (trip_distance * 2 * consumption / 100) * current_fuel_price
        parking_cost = selected_parking['fee_per_hour'] * parking_duration
        time_cost = (trip_distance * 2 / 30) * time_value
        total_cost = fuel_cost + parking_cost + time_cost
        co2_emission = trip_distance * 2 * 120 / 1000
        
        st.success(f"""
        **Trip Cost Breakdown:**  
        ⛽ **Fuel Cost:** €{fuel_cost:.2f}  
        🅿️ **Parking Cost:** €{parking_cost:.2f}  
        ⏱️ **Time Cost:** €{time_cost:.2f}  
        💰 **Total Cost:** €{total_cost:.2f}  
        
        **Environmental Impact:**  
        🌍 **CO₂ Emissions:** {co2_emission:.2f} kg  
        🌳 **Offset needed:** {co2_emission/22:.1f} trees/year
        """)
    
    if not filtered_df.empty:
        st.markdown('<div class="section-header">🔥 Parking Availability</div>', unsafe_allow_html=True)
        filtered_df['availability_pct'] = (filtered_df['available_spots'] / filtered_df['total_spots'] * 100).round(1)
        fig_heatmap = px.scatter(
            filtered_df,
            x='lon',
            y='lat',
            size='total_spots',
            color='availability_pct',
            hover_name='name',
            hover_data=['fee_per_hour', 'available_spots', 'total_spots'],
            title='Parking Availability by Location',
            labels={'availability_pct': 'Availability %'},
            color_continuous_scale='Tealgrn',
            size_max=20
        )
        fig_heatmap.update_layout(
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font={'family': 'SF Pro Display, sans-serif'}
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        st.markdown('<div class="section-header">🎯 Smart Recommendations</div>', unsafe_allow_html=True)
        if user_profile == "Commuter":
            recommendation = filtered_df.nsmallest(1, 'fee_per_hour')
            st.info(f"💼 **For Commuters**: We recommend {recommendation.iloc[0]['name']} - lowest cost at €{recommendation.iloc[0]['fee_per_hour']}/hour")
        elif user_profile == "Tourist":
            recommendation = filtered_df.nsmallest(1, 'distance')
            st.info(f"🏛️ **For Tourists**: We recommend {recommendation.iloc[0]['name']} - closest to city center ({recommendation.iloc[0]['distance']:.1f}km)")
        elif user_profile == "Delivery Driver":
            recommendation = filtered_df.nlargest(1, 'available_spots')
            st.info(f"📦 **For Delivery Drivers**: We recommend {recommendation.iloc[0]['name']} - most available spots ({recommendation.iloc[0]['available_spots']})")
        else:
            recommendation = filtered_df[filtered_df['ev_charging'] == True].nsmallest(1, 'distance') if any(filtered_df['ev_charging']) else filtered_df.nsmallest(1, 'distance')
            st.info(f"💼 **For Business Travelers**: We recommend {recommendation.iloc[0]['name']} - premium location with amenities")

def fuel_tab():
    st.markdown('<div class="section-header">⛽ Fuel Price Analysis</div>', unsafe_allow_html=True)
    fuel_df = load_fuel_prices()
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=fuel_df.index.min())
    with col2:
        end_date = st.date_input("End Date", value=fuel_df.index.max())
    
    filtered_fuel = fuel_df[(fuel_df.index >= pd.to_datetime(start_date)) & (fuel_df.index <= pd.to_datetime(end_date))]
    
    if filtered_fuel.empty:
        st.error("No data available for the selected date range. Please adjust your date selection.")
        return
    
    if st.checkbox("Show raw data"):
        st.dataframe(filtered_fuel)
    
    fuel_types = st.multiselect(
        "Select Fuel Types to Compare",
        ['Super E10', 'Diesel', 'Super E5'],
        default=['Super E10', 'Diesel']
    )
    
    if fuel_types:
        fig = make_subplots(specs=[[{"secondary_y": False}]])
        
        colors = {
            'Super E10': '#FF453A',
            'Diesel': '#FF9F0A',
            'Super E5': '#30D158'
        }
        
        for fuel in fuel_types:
            fig.add_trace(go.Scatter(
                x=filtered_fuel.index,
                y=filtered_fuel[fuel],
                name=fuel,
                mode='lines',
                line=dict(color=colors.get(fuel, '#0A84FF'), width=3)
            ))
        
        fig.update_layout(
            title='Fuel Price Trends Over Time',
            xaxis_title='Date',
            yaxis_title='Price (€/L)',
            height=500,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font={'family': 'SF Pro Display, sans-serif'},
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Please select at least one fuel type to display the chart.")
    
    st.markdown('<div class="section-header">📊 Fuel Statistics</div>', unsafe_allow_html=True)
    
    if not filtered_fuel.empty and len(filtered_fuel) > 0:
        stats_col1, stats_col2, stats_col3 = st.columns(3)
        
        with stats_col1:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 1.1rem; font-weight: 500; color: var(--system-label);">Current Super E10</div>
                <div style="font-size: 1.8rem; font-weight: 600; color: var(--system-red);">€{filtered_fuel['Super E10'].iloc[-1]:.2f}/L</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 1.1rem; font-weight: 500; color: var(--system-label);">Current Diesel</div>
                <div style="font-size: 1.8rem; font-weight: 600; color: var(--system-orange);">€{filtered_fuel['Diesel'].iloc[-1]:.2f}/L</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 1.1rem; font-weight: 500; color: var(--system-label);">Current Super E5</div>
                <div style="font-size: 1.8rem; font-weight: 600; color: var(--system-green);">€{filtered_fuel['Super E5'].iloc[-1]:.2f}/L</div>
            </div>
            """, unsafe_allow_html=True)
        
        with stats_col2:
            if len(filtered_fuel) >= 30:
                super_e10_change = filtered_fuel['Super E10'].iloc[-1] - filtered_fuel['Super E10'].iloc[-30]
                super_e10_pct_change = (super_e10_change / filtered_fuel['Super E10'].iloc[-30]) * 100
                diesel_change = filtered_fuel['Diesel'].iloc[-1] - filtered_fuel['Diesel'].iloc[-30]
                diesel_pct_change = (diesel_change / filtered_fuel['Diesel'].iloc[-30]) * 100
                super_e5_change = filtered_fuel['Super E5'].iloc[-1] - filtered_fuel['Super E5'].iloc[-30]
                super_e5_pct_change = (super_e5_change / filtered_fuel['Super E5'].iloc[-30]) * 100
                period_label = "30-Day Change"
            else:
                super_e10_change = filtered_fuel['Super E10'].iloc[-1] - filtered_fuel['Super E10'].iloc[0]
                super_e10_pct_change = (super_e10_change / filtered_fuel['Super E10'].iloc[0]) * 100
                diesel_change = filtered_fuel['Diesel'].iloc[-1] - filtered_fuel['Diesel'].iloc[0]
                diesel_pct_change = (diesel_change / filtered_fuel['Diesel'].iloc[0]) * 100
                super_e5_change = filtered_fuel['Super E5'].iloc[-1] - filtered_fuel['Super E5'].iloc[0]
                super_e5_pct_change = (super_e5_change / filtered_fuel['Super E5'].iloc[0]) * 100
                period_label = f"{len(filtered_fuel)}-Day Change"
            
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 1.1rem; font-weight: 500; color: var(--system-label);">{period_label} (Super E10)</div>
                <div style="font-size: 1.5rem; font-weight: 600; color: {'var(--system-green)' if super_e10_change < 0 else 'var(--system-red)'};">€{super_e10_change:.2f}</div>
                <div style="font-size: 1rem; color: {'var(--system-green)' if super_e10_pct_change < 0 else 'var(--system-red)'};">{super_e10_pct_change:+.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 1.1rem; font-weight: 500; color: var(--system-label);">{period_label} (Diesel)</div>
                <div style="font-size: 1.5rem; font-weight: 600; color: {'var(--system-green)' if diesel_change < 0 else 'var(--system-red)'};">€{diesel_change:.2f}</div>
                <div style="font-size: 1rem; color: {'var(--system-green)' if diesel_pct_change < 0 else 'var(--system-red)'};">{diesel_pct_change:+.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 1.1rem; font-weight: 500; color: var(--system-label);">{period_label} (Super E5)</div>
                <div style="font-size: 1.5rem; font-weight: 600; color: {'var(--system-green)' if super_e5_change < 0 else 'var(--system-red)'};">€{super_e5_change:.2f}</div>
                <div style="font-size: 1rem; color: {'var(--system-green)' if super_e5_pct_change < 0 else 'var(--system-red)'};">{super_e5_pct_change:+.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with stats_col3:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 1.1rem; font-weight: 500; color: var(--system-label);">All-Time High (Super E10)</div>
                <div style="font-size: 1.5rem; font-weight: 600; color: var(--system-red);">€{filtered_fuel['Super E10'].max():.2f}/L</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 1.1rem; font-weight: 500; color: var(--system-label);">All-Time High (Diesel)</div>
                <div style="font-size: 1.5rem; font-weight: 600; color: var(--system-orange);">€{filtered_fuel['Diesel'].max():.2f}/L</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 1.1rem; font-weight: 500; color: var(--system-label);">All-Time High (Super E5)</div>
                <div style="font-size: 1.5rem; font-weight: 600; color: var(--system-green);">€{filtered_fuel['Super E5'].max():.2f}/L</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('<div class="section-header">🔮 Price Prediction</div>', unsafe_allow_html=True)
    pred_days = st.slider("Days to predict ahead", 1, 30, 7)
    
    if st.button("Predict Prices", key="predict_prices") and len(filtered_fuel) >= 30:
        recent_super_e10 = filtered_fuel['Super E10'].iloc[-30:]
        recent_diesel = filtered_fuel['Diesel'].iloc[-30:]
        recent_super_e5 = filtered_fuel['Super E5'].iloc[-30:]
        
        super_e10_change = (recent_super_e10.iloc[-1] - recent_super_e10.iloc[0]) / 30
        diesel_change = (recent_diesel.iloc[-1] - recent_diesel.iloc[0]) / 30
        super_e5_change = (recent_super_e5.iloc[-1] - recent_super_e5.iloc[0]) / 30
        
        pred_super_e10 = filtered_fuel['Super E10'].iloc[-1] + (super_e10_change * pred_days)
        pred_diesel = filtered_fuel['Diesel'].iloc[-1] + (diesel_change * pred_days)
        pred_super_e5 = filtered_fuel['Super E5'].iloc[-1] + (super_e5_change * pred_days)
        
        st.success(f"""
        **Predicted Prices in {pred_days} Days:**  
        ⛽ **Super E10:** €{max(0, pred_super_e10):.2f}/L  
        🚛 **Diesel:** €{max(0, pred_diesel):.2f}/L  
        ⚡ **Super E5:** €{max(0, pred_super_e5):.2f}/L  
        
        *Based on 30-day trend analysis*
        """)

def main():
    st.markdown('<h1 class="main-header">🚗 SmartMobility</h1>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Parking Finder", "Fuel Price Analysis"])
    
    with tab1:
        parking_tab()
    
    with tab2:
        fuel_tab()

if __name__ == "__main__":
    main()
