# app.py
import streamlit as st
import pandas as pd
from map import draw_map  # your function that generates folium/map
from diagram import create_diagrams  # your function(s) that generate diagrams/charts

st.set_page_config(
    page_title="ParkSmart",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar: controls & settings
st.sidebar.title("Controls")

# Option to re-load CSV file
csv_path = st.sidebar.text_input(
    "Parking CSV file path", value="parking_data.csv"
)
use_sample = st.sidebar.checkbox("Load example data", value=False)

# Tabs: Map, Diagrams, Data Table
tabs = st.tabs(["Map View", "Charts", "Data"])

@st.cache_data
def load_data(path, sample):
    if sample:
        # fallback sample from your repo or demo
        return pd.read_csv(path)  # adapt as needed
    else:
        return pd.read_csv(path)

df = load_data(csv_path, use_sample)

# ===== Tab: Map View =====
with tabs[0]:
    st.header("Parking Map")
    if df is not None and not df.empty:
        # Make sure your draw_map returns a folium.Folium object or a compatible Streamlit component
        m = draw_map(df)
        st_data = m._repr_html_()
        st.components.v1.html(st_data, height=600, scrolling=True)
    else:
        st.info("No data available to draw map.")

# ===== Tab: Charts =====
with tabs[1]:
    st.header("Parking Analytics")
    if df is not None and not df.empty:
        # Assume create_diagrams returns one or more matplotlib/plotly charts
        charts = create_diagrams(df)
        if isinstance(charts, dict):
            for title, chart in charts.items():
                st.subheader(title)
                st.pyplot(chart) if hasattr(chart, 'figure') else st.write(chart)
        else:
            st.pyplot(charts) if hasattr(charts, 'figure') else st.write(charts)
    else:
        st.info("No data available to create charts.")

# ===== Tab: Raw Data =====
with tabs[2]:
    st.header("Parking Data Table")
    st.write(f"Total records: {len(df):,}")
    st.dataframe(df, use_container_width=True)

# ===== Footer =====
st.markdown("---")
st.markdown(
    "Built with ❤️ using [Streamlit](https://streamlit.io) | "
    "[View on GitHub](https://github.com/adahuonganh/fiep2025)"
)
