import streamlit as st
import pandas as pd

st.title("Map Test")

data = pd.DataFrame({
    'lat': [25.2048, 25.2100],
    'lon': [55.2708, 55.2800]
})

st.write("Data:", data)

try:
    st.map(data)
    st.success("Basic map rendered")
except Exception as e:
    st.error(f"Basic map failed: {e}")

try:
    st.map(data, latitude='lat', longitude='lon', size=20, color='#ff0000')
    st.success("Advanced map rendered")
except Exception as e:
    st.error(f"Advanced map failed: {e}")
