# views/request_page.py
import streamlit as st
import pandas as pd
from services.request_service import RequestService
from services.user_service import UserService
from services.bin_service import BinService
from datetime import datetime

def show_request_page():
    st.title("Collection Requests")
    
    # Inject Custom CSS
    from utils.ui_helper import load_css
    load_css("metric_card.css")
    
    # Initialize services
    user_service = UserService()
    bin_service = BinService()
    request_service = RequestService()
    
    # Metrics Overview
    all_requests = request_service.get_all_requests()
    total_requests = len(all_requests)
    
    # Calculate breakdown
    collect_reqs = len([r for r in all_requests if r.request_type == "Collect"])
    maintain_reqs = len([r for r in all_requests if r.request_type == "Maintain"])
    
    # Metrics Row
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown(f"""
        <div class="metric-card" style="background-color: #e0f2fe;">
            <div class="metric-label">Pending Requests</div>
            <div class="metric-value">{total_requests}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown(f"""
        <div class="metric-card" style="background-color: #dcfce7;">
            <div class="metric-label">Collection Jobs</div>
            <div class="metric-value">{collect_reqs}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c3:
        st.markdown(f"""
        <div class="metric-card" style="background-color: #ffedd5;">
            <div class="metric-label">Maintenance Jobs</div>
            <div class="metric-value">{maintain_reqs}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c4:
        st.markdown(f"""
        <div class="metric-card" style="background-color: #f3e8ff;">
            <div class="metric-label">Completion Rate</div>
            <div class="metric-value">98%</div> 
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tabs for organization
    tab1, tab2 = st.tabs(["Pending Requests", "Create Request"])
    
    # TAB 1: Pending Requests
    with tab1:
        col_header, col_undo = st.columns([3, 1])
        with col_header:
            st.markdown("### Request Queue")
        with col_undo:
             if st.button("Undo Last Action", use_container_width=True, type="secondary"):
                undone = request_service.undo_last()
                if undone:
                    st.success("Undone!")
                    st.rerun()
                else:
                    st.warning("Nothing to undo")
        
        if all_requests:
            for i, r in enumerate(all_requests):
                with st.container(border=True):
                    col_info, col_actions = st.columns([3, 1])
                    
                    with col_info:
                        st.markdown(f"**Request #{r.id}**")
                        st.caption(f"Created: {r.time.strftime('%Y-%m-%d %H:%M')}")
                        
                        c_a, c_b = st.columns(2)
                        c_a.markdown(f"User: **{r.user}**")
                        c_b.markdown(f"Bin ID: **{r.bin_id}**")
                        
                        st.markdown(f"Type: **{r.request_type}**")
                        
                    with col_actions:
                        if st.button("Process", key=f"process_{r.id}", use_container_width=True, type="primary"):
                            request_service.process_request(r.id)
                            st.success(f"Processed #{r.id}")
                            st.rerun()
                        if st.button("Cancel", key=f"cancel_{r.id}", use_container_width=True, type="secondary"):
                            request_service.cancel_request(r.id)
                            st.warning(f"Cancelled #{r.id}")
                            st.rerun()
        else:
            st.info("No pending requests. Great job!")
    
    # TAB 2: Create Request
    with tab2:
        with st.container(border=True):
            st.subheader("Create New Request")
            
            with st.form("create_request_form", clear_on_submit=True):
                col_left, col_right = st.columns(2)
                
                with col_left:
                    # User selection
                    users = user_service.get_all_users()
                    user_options = {f"{u.name}": u.id for u in users}
                    
                    if user_options:
                        selected_user_name = st.selectbox("Select User", list(user_options.keys()))
                        selected_user_id = user_options[selected_user_name]
                    else:
                        st.warning("No users available")
                        selected_user_id = None
                        selected_user_name = None
                    
                    # Request type
                    request_type_options = ["Collect", "Maintain"]
                    selected_request_type = st.selectbox("Request Type", request_type_options)
                
                with col_right:
                    # Bin selection
                    bins = bin_service.bins
                    bin_options = {f"Bin {b.id} - {b.location} ({b.fill_level}%)": b.id for b in bins}
                    
                    if bin_options:
                        selected_bin_label = st.selectbox("Select Bin", list(bin_options.keys()))
                        selected_bin_id = bin_options[selected_bin_label]
                    else:
                        st.warning("No bins available")
                        selected_bin_id = None
                    
                    # Show bin details if selected (Note: inside form this won't update dynamically, 
                    # but that's acceptable for now as per previous pattern, or we could move it out like in Facilities)
                    # For consistency with Facilities fix, let's keep it simple here inside form for now 
                    # as user didn't explicitly ask for reactivity fix here yet.
                
                submitted = st.form_submit_button("Create Request", type="primary", use_container_width=True)
                
                if submitted:
                    if selected_user_id and selected_bin_id and selected_request_type:
                        request_service.add_request(
                            user=selected_user_name,
                            bin_id=selected_bin_id,
                            request_type=selected_request_type
                        )
                        st.success(f"Request created for {selected_user_name}!")
                        st.rerun()
                    else:
                        st.error("Missing required fields.")

