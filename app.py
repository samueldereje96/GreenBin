import sys
import os
import streamlit as st
from views.history_page import show_history_page
from views.home_page import show_home
from views.request_page import show_request_page
from views.bins_page import show_bins_page
from views.dispatch_page import show_dispatch_page
from views.facilities_page import show_facilities_page
from services.bin_service import BinService
# from services.city_serivce import create_city_grid # Unused
from services.facility_service import FacilityService
from services.vehicle_service import VehicleService

# Ensure the project root is in sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Initialize services
bin_service = BinService()
service = FacilityService()

# Persist VehicleService in session state
if "vehicle_service" not in st.session_state:
    st.session_state.vehicle_service = VehicleService()
    # Initial assignment (optional, maybe we want them idle first)
    # st.session_state.vehicle_service.assign_bins_and_facilities()

# Check for stale state (missing undo_last) and re-initialize if needed
if not hasattr(st.session_state.vehicle_service, "undo_last"):
    st.warning("Detecting stale service version. Reloading VehicleService...")
    st.session_state.vehicle_service = VehicleService()

vehicle_service = st.session_state.vehicle_service


st.set_page_config(page_title="GreenBin", layout="wide")

st.sidebar.markdown(
    """
    <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 20px;">
        <svg xmlns="http://www.w3.org/2000/svg" height="42" viewBox="0 0 24 24" width="42" fill="green">
            <path d="M17,8C8,10,5.9,16.17,3.82,21.34L5.71,22l1-2.3A4.49,4.49,0,0,0,8,20C19,20,22,3,22,3,21,5,14,5.25,9,6.25S2,11.5,2,13.5a6.22,6.22,0,0,0,1.75,3.75C7,8,17,8,17,8Z"/>
        </svg>
        <h1 style="color:green; font-size:42px; font-weight:bold; margin: 0 0 0 10px; display: inline;">GreenBin</h1>
    </div>
    """,
    unsafe_allow_html=True
)

from utils.ui_helper import load_css

# Inject custom CSS for sidebar buttons and background
load_css("sidebar.css")

if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

# Helper function to determine button type
def get_button_type(page_name):
    return "primary" if st.session_state.current_page == page_name else "secondary"

# Sidebar buttons
if st.sidebar.button("Home", icon=":material/home:", type=get_button_type("Home"), use_container_width=True):
    st.session_state.current_page = "Home"
    st.rerun()
if st.sidebar.button("Bins", icon=":material/delete:", type=get_button_type("Bins"), use_container_width=True):
    st.session_state.current_page = "Bins"
    st.rerun()
if st.sidebar.button("Dispatch", icon=":material/local_shipping:", type=get_button_type("Dispatch"), use_container_width=True):
    st.session_state.current_page = "Dispatch"
    st.rerun()
if st.sidebar.button("Facilities", icon=":material/factory:", type=get_button_type("Facilities"), use_container_width=True):
    st.session_state.current_page = "Facilities"
    st.rerun()
if st.sidebar.button("Requests", icon=":material/assignment:", type=get_button_type("Requests"), use_container_width=True):
    st.session_state.current_page = "Requests"
    st.rerun()
if st.sidebar.button("History", icon=":material/history:", type=get_button_type("History"), use_container_width=True):
    st.session_state.current_page = "History"
    st.rerun()

# Admin Profile Section
st.sidebar.markdown(
    """
    <div class="admin-profile">
        <svg xmlns="http://www.w3.org/2000/svg" height="40" viewBox="0 0 24 24" width="40" fill="#555555" style="margin-right: 15px;">
            <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
        </svg>
        <div>
            <p style="margin: 0; font-weight: bold; font-size: 16px; color: #333;">Admin</p>
            <p style="margin: 0; font-size: 12px; color: #666;">Administrator</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

if st.session_state.current_page == "Home":
    show_home(bin_service, vehicle_service)

elif st.session_state.current_page == "Bins":
    show_bins_page(bin_service)

elif st.session_state.current_page == "Dispatch":
    show_dispatch_page(vehicle_service, bin_service)

elif st.session_state.current_page == "Facilities":
    show_facilities_page(service)

elif st.session_state.current_page == "Requests":
    show_request_page()

elif st.session_state.current_page == "History":
    show_history_page()
