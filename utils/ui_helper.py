import streamlit as st
import os

def load_css(file_name):
    """Load CSS from css folder and inject into Streamlit."""
    file_path = os.path.join("css", file_name)
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def get_map_html(bins_json, facilities_json, vehicles_json):
    """Load map template and inject data."""
    file_path = os.path.join("css", "map_template.html")
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            template = f.read()
            # Replace placeholders
            # Note: We use double curly braces in the template for JS/CSS, 
            # so we need to be careful with f-string formatting or use .format()
            # But since the template has {bins_json} etc, we can use format.
            # However, the template also has {s}, {z}, {x}, {y} for Leaflet which might conflict.
            # Let's use simple string replacement for safety.
            
            html = template.replace("{{bins_json}}", bins_json)
            html = html.replace("{{facilities_json}}", facilities_json)
            html = html.replace("{{vehicles_json}}", vehicles_json)
            return html
    return "<div>Error loading map template</div>"
