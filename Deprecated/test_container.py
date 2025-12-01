import streamlit as st

try:
    with st.container(border=True):
        st.write("Container with border supported")
except TypeError:
    st.write("Container with border NOT supported")
