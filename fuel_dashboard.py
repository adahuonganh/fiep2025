import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

@st.cache_data
def load_fuel_prices():
    df = pd.read_csv("fuel_price.csv", sep=";")
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
    
    fuel_types = st.multiselect(
        "Select Fuel Types to Compare",
        ['Super E10', 'Diesel', 'Super E5'],
        default=['Super E10', 'Diesel', 'Super E5']
    )
    
    if fuel_types:
        fig = make_subplots(specs=[[{"secondary_y": False}]])
        colors = {'Super E10':  "#FF0A0A", 'Diesel': '#30D158', 'Super E5': '#FF9F0A'}
        
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
