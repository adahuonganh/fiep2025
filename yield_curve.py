import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# Load Data
df = pd.read_csv("fredgraph.csv")
df["observation_date"] = pd.to_datetime(df["observation_date"]).dt.date  # Convert to date only
available_dates = df["observation_date"].sort_values().unique()

# Layout (Sidebar for vertical slider)
st.sidebar.title("Select Date")
selected_date = st.sidebar.slider(
    "Date",
    min_value=available_dates.min(),
    max_value=available_dates.max(),
    value=available_dates.min(),
    format="YYYY-MM-DD"
)

# Filter Data
filtered_df = df[df["observation_date"] <= selected_date]  # Show all past dates up to selected one

# Prepare Data for 3D Plot
maturities = ["1M", "3M", "6M", "1Y", "2Y", "3Y", "5Y", "7Y", "10Y", "20Y", "30Y"]
dates = filtered_df["observation_date"].values
yields = filtered_df.iloc[:, 1:].values  # Exclude date column

# Create 3D Surface Plot
fig = go.Figure(data=[go.Surface(z=yields, x=maturities, y=dates)])

# Add Highlighted Line for Selected Date
highlight_df = df[df["observation_date"] == selected_date]
if not highlight_df.empty:
    fig.add_trace(
        go.Scatter3d(
            x=maturities,
            y=[selected_date] * len(maturities),
            z=highlight_df.iloc[0, 1:].values,
            mode="lines",
            line=dict(color="red", width=5),
            name=f"Yield Curve on {selected_date}"
        )
    )

fig.update_layout(
    title="📈 3D U.S. Treasury Yield Curve",
    scene=dict(
        xaxis_title="Maturity",
        yaxis_title="Date",
        zaxis_title="Yield Rate (%)"
    ),
    width=1000,  # Increase graph size
    height=800
)

st.plotly_chart(fig)
