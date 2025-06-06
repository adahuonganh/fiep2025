# app.py
import streamlit as st
from map import render as render_map
from diagram import render as render_diagram

def render():
    st.title("🚗 Urban Parking Finder")

    # Sidebar navigation to switch between parts
    page = st.sidebar.selectbox("Choose view", ["Map", "Comparison Diagrams"])

    if page == "Map":
        render_map()
    elif page == "Comparison Diagrams":
        render_diagram()

if __name__ == "__main__":
    render()
