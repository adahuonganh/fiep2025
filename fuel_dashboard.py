import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

@st.cache_data
def load_fuel_prices():
    df = pd.read_csv("fuel_price.csv", sep=";", skiprows=5)
    df = df.rename(columns={'Datum': 'date', 'Super E10': 'e10', 'Diesel': 'diesel', 'Super E5': 'e5'})
    df['date'] = pd.to_datetime(df['date'])
    for col in ['e10', 'diesel', 'e5']:
        df[col] = df[col].str.replace(',', '.').astype(float)
    df = df.set_index('date')
    return df.rename(columns={'e10': 'Super E10', 'diesel': 'Diesel', 'e5': 'Super E5'})

def fuel_tab():
    st.markdown('<div class="section-header">⛽ Fuel Price Analysis</div>', unsafe_allow_html=True)
    fuel_df = load_fuel_prices()
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=fuel_df.index.min())
    with col2:
        end_date = st.date_input("End Date", value=fuel_df.index.max())
    
    filtered_fuel = fuel_df[(fuel_df.index >= pd.to_datetime(start_date)) & 
                           (fuel_df.index <= pd.to_datetime(end_date))]
    
    if filtered_fuel.empty:
        st.error("No data available for the selected date range.")
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
        colors = {'Super E10': '#FF453A', 'Diesel': '#FF9F0A', 'Super E5': '#30D158'}
        
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
        st.warning("Please select at least one fuel type.")
    
    # ... (rest of fuel price statistics code)
