import streamlit as st
import map  # your map.py file, assumed to have a function to render part 1
import diagram  # your diagram.py file, assumed to have a function to render part 2

st.title("ParkSmart – Urban Parking Finder")

tab1, tab2 = st.tabs(["Map & List", "Diagrams"])

with tab1:
    map.render_map()  # assuming map.py has a function called render_map() that draws part 1

with tab2:
    diagram.render_diagram()  # assuming diagram.py has a function called render_diagram() that draws part 2
