import streamlit as st
from diagram import render as render_diagram
from map import render as render_map
from co2 import render as render_co2
from details import render as render_details

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Map", "Diagram", "CO2 & Energy", "Details"])

if page == "Map":
    render_map()
elif page == "Diagram":
    render_diagram()
elif page == "CO2 & Energy":
    render_co2()
elif page == "Details":
    render_details()
