# app.py
import streamlit as st
import pandas as pd
from map import render_map, load_data as load_map_data
from diagram import render, load_data as load_diagram_data

# Set up app layout
st.set_page_config(
    page_title="ParkSmart - Find your parking spot",
    layout="wide",
    initial_sidebar_state="expanded"
)

tabs = st.tabs(["Map View", "Compare Parkings", "Raw Data"])

# --- Tab 1: Map ---
with tabs[0]:
    render_map()

# --- Tab 2: Charts / Comparison ---
with tabs[1]:
    render()

# --- Tab 3: Raw Data Viewer ---
with tabs[2]:
    st.header("Raw Parking Data")
    # Merge data loaders to ensure consistency
    df1 = load_map_data()
    df2 = load_diagram_data()
    if not df1.empty:
        st.subheader("From map.py loader")
        st.dataframe(df1, use_container_width=True)
    if not df2.empty:
        st.subheader("From diagram.py loader")
        st.dataframe(df2, use_container_width=True)
    if df1.empty and df2.empty:
        st.warning("No data available – check `parking_data.csv` and loaders.")

# Footer
st.markdown("---")
