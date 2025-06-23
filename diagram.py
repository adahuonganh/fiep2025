import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random
from math import radians, sin, cos, sqrt, atan2
from map import load_parking_data

@st.cache_data
def load_fuel_prices():
    # Read the CSV data directly without skipping rows
    df = pd.read_csv("fuel_price.csv", sep=";")
    
    # Rename columns
    df = df.rename(columns={'Datum': 'date', 'Super E10': 'e10', 'Diesel': 'diesel', 'Super E5': 'e5'})
    df['date'] = pd.to_datetime(df['date'])

    # Convert comma decimal separators to dots and cast to float
    for col in ['e10', 'diesel', 'e5']:
        df[col] = df[col].str.replace(',', '.', regex=False).astype(float)

    # Set date as index
    df = df.set_index('date')

    # Rename columns to match the expected output
    df = df.rename(columns={
        'e10': 'Super E10',
        'diesel': 'Diesel',
        'e5': 'Super E5'
    })

    return df

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

def haversine(lat1, lon1, lat2, lon2):
    try:
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlon, dlat = lon2 - lon1, lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
        return 6371 * 2 * atan2(sqrt(a), sqrt(1-a))
    except:
        return float('inf')

def filter_df(df, user_location, max_dist, fee_range, ev_only):
    if df.empty:
        return df

    df['distance'] = df.apply(lambda r: haversine(user_location[0], user_location[1], r['lat'], r['lon']), axis=1)
    df = df[df['distance'] <= max_dist]
    df = df[df['fee_per_hour'].between(fee_range[0], fee_range[1])]

    if ev_only:
        df = df[df['ev_charging'] > 0]

    return df.sort_values('distance').reset_index(drop=True)

def show_comparison_charts(filtered_df):
    if filtered_df.empty:
        st.warning("No data to display.")
        return

    top5 = filtered_df.head(5)    
    # Fee per Hour
    st.markdown("###### 💰 Fee per Hour")
    fig = px.bar(top5, x='name', y='fee_per_hour',
                labels={'fee_per_hour': 'Fee (€/hour)', 'name': 'Parking Location'},
                color='fee_per_hour',
                color_continuous_scale='Oranges')
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family': 'SF Pro Display, sans-serif'},
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig, use_container_width=True)

    # Travel Distance
    st.markdown("###### 🚗 Travel Distance")
    fig = px.bar(top5, x='name', y='distance',
                labels={'distance': 'Distance (km)', 'name': 'Parking Location'},
                color='distance',
                color_continuous_scale='Greens')
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family': 'SF Pro Display, sans-serif'},
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig, use_container_width=True)

    # Spots Available
    st.markdown("###### 🅿️ Total Spot Availability")
    fig = px.bar(top5, x='name', y='total_spots',
                labels={'total_spots': 'Available Spots', 'name': 'Parking Location'},
                color='total_spots',
                color_continuous_scale='Blues')
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family': 'SF Pro Display, sans-serif'},
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig, use_container_width=True)

def insights_tab():
    df = load_parking_data()
    filtered_df = filter_df(df, (st.session_state.user_lat, st.session_state.user_lon), 
                          max_dist=10.0, fee_range=(0.0, 5.0), ev_only=False)
        
    st.markdown("#### 🌱 Environmental Impact")

    # Your CO2 data
    co2_data = {
        'Car (Gasoline)': 120, 'Car (Diesel)': 110, 'Electric Car': 30, 'Hybrid Car': 80,
        'Public Transport': 25, 'Bicycle': 0, 'Walking': 0, 'E-Scooter': 15
    }

    # Define color for each transport type
    transport_colors = {
        'Car (Gasoline)': '#FF453A',
        'Car (Diesel)': '#FFD60A',
        'Electric Car': '#30D158',
        'Hybrid Car': '#FFD60A',
        'Public Transport': '#30D158',
        'Bicycle': '#30D158',
        'Walking': '#30D158',
        'E-Scooter': '#30D158'
    }

    # Create 4 columns (2 charts per row)
    col1, col2, col3, col4 = st.columns(4)

    # First row
    with col1:
        st.plotly_chart(
            create_apple_gauge(
                co2_data['Car (Gasoline)'],
                150,
                transport_colors['Car (Gasoline)'],
                'Gasoline Car'
            ),
            use_container_width=True
        )

    with col2:
        st.plotly_chart(
            create_apple_gauge(
                co2_data['Car (Diesel)'],
                150,
                transport_colors['Car (Diesel)'],
                'Diesel Car'
            ),
            use_container_width=True
        )

    with col3:
        st.plotly_chart(
            create_apple_gauge(
                co2_data['Electric Car'],
                150,
                transport_colors['Electric Car'],
                'Electric Car'
            ),
            use_container_width=True
        )

    with col4:
        st.plotly_chart(
            create_apple_gauge(
                co2_data['Hybrid Car'],
                150,
                transport_colors['Hybrid Car'],
                'Hybrid Car'
            ),
            use_container_width=True
        )

    # Second row
    col5, col6, col7, col8 = st.columns(4)

    with col5:
        st.plotly_chart(
            create_apple_gauge(
                co2_data['Public Transport'],
                150,
                transport_colors['Public Transport'],
                'Public Transport'
            ),
            use_container_width=True
        )

    with col6:
        st.plotly_chart(
            create_apple_gauge(
                co2_data['E-Scooter'],
                150,
                transport_colors['E-Scooter'],
                'E-Scooter'
            ),
            use_container_width=True
        )

    with col7:
        st.plotly_chart(
            create_apple_gauge(
                co2_data['Bicycle'],
                150,
                transport_colors['Bicycle'],
                'Bicycle'
            ),
            use_container_width=True
        )

    with col8:
        st.plotly_chart(
            create_apple_gauge(
                co2_data['Walking'],
                150,
                transport_colors['Walking'],
                'Walking'
            ),
            use_container_width=True
        )
    
    # Show comparison charts
    st.markdown("#### 📊 Parking Insights")
    if not filtered_df.empty:
        show_comparison_charts(filtered_df)
    
    st.markdown("#### 💰 Trip Calculator")
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
