import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random
from map import load_parking_data, filter_data

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

def insights_tab():
    df = load_parking_data()
    filtered_df = filter_data(df, st.session_state.user_lat, st.session_state.user_lon, 
                            max_dist=10.0, fee_range=(0.0, 5.0), 
                            ev_only=False, open_weekend=False, cashless_payment=False)
    
    st.markdown('<div class="section-header">📊 Parking Statistics</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
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
            st.warning("No parking spots in the area.")
        
        st.markdown(f'<div class="fun-fact">**💡 Smart Tip**\n\n{get_fun_fact()}</div>', unsafe_allow_html=True)
    
    with col2:
        if not filtered_df.empty:
            fig_price = px.histogram(filtered_df, x='fee_per_hour', 
                                   title='Price Distribution',
                                   labels={'fee_per_hour': 'Fee per hour (€)'},
                                   color_discrete_sequence=['#0A84FF'])
            fig_price.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font={'family': 'SF Pro Display, sans-serif'}
            )
            st.plotly_chart(fig_price, use_container_width=True)
    
    st.markdown('<div class="section-header">🌱 Environmental Impact</div>', unsafe_allow_html=True)
    
    co2_data = {
        'Car (Gasoline)': 120, 'Car (Diesel)': 110, 'Electric Car': 30, 'Hybrid Car': 80,
        'Public Transport': 25, 'Bicycle': 0, 'Walking': 0, 'E-Scooter': 15
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(
            create_apple_gauge(
                co2_data['Car (Gasoline)'],
                150,
                '#FF453A',
                'Gasoline Car Emissions'
            ),
            use_container_width=True
        )
    
    with col2:
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
    # ... (rest of trip calculator code)
