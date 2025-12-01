# views/history_page.py
import streamlit as st
import pandas as pd
from services.history_service import HistoryService

def show_request_history(history_service):
    """Display request history in a clean format with filters"""
    stack = history_service.get_stack("request")
    if stack and not stack.is_empty():
        history_list = stack.to_list()[::-1]  # newest first
        
        history_data = []
        for i, h in enumerate(history_list, 1):
            action_type = h["type"]
            data = h["data"]
            
            # Determine status based on action type
            if action_type == "add_request":
                status = "Added"
            elif action_type == "process_request":
                status = "Processed"
            elif action_type == "cancel_request":
                status = "Cancelled"
            else:
                status = action_type
            
            history_data.append({
                "#": i,
                "Action": status,
                "Request ID": data.get("id", "N/A"),
                "User": data.get("user", "N/A"),
                "Bin ID": data.get("bin_id", "N/A"),
                "Type": data.get("request_type", "N/A"),
                "Timestamp": data.get("time", "N/A")
            })
        
        df = pd.DataFrame(history_data)
        
        # Filters
        with st.container(border=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                actions = ["All"] + sorted(df["Action"].unique().tolist())
                selected_action = st.selectbox("Filter by Action", actions, key="action_filter")
            with col2:
                users = ["All"] + sorted(df["User"].unique().tolist())
                selected_user = st.selectbox("Filter by User", users, key="user_filter")
            with col3:
                types = ["All"] + sorted(df["Type"].unique().tolist())
                selected_type = st.selectbox("Filter by Request Type", types, key="request_type_filter")
        
        if selected_action != "All":
            df = df[df["Action"] == selected_action]
        if selected_user != "All":
            df = df[df["User"] == selected_user]
        if selected_type != "All":
            df = df[df["Type"] == selected_type]

        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No request history available")

def show_bin_history(history_service):
    """Display bin history in a clean format with filters"""
    stack = history_service.get_stack("bin")
    if stack and not stack.is_empty():
        history_list = stack.to_list()[::-1]
        
        history_data = []
        for i, h in enumerate(history_list, 1):
            history_data.append({
                "#": i,
                "Action": h["type"],
                "Bin ID": h["data"].get("id", "N/A"),
                "Location": h["data"].get("location", "N/A"),
                "Type": h["data"].get("bin_type", "N/A"),
                "Fill Level": f"{h['data'].get('fill_level', 0)}%",
                "Position": f"({h['data'].get('x', 0)}, {h['data'].get('y', 0)})"
            })
        
        df = pd.DataFrame(history_data)
        
        # Filter by Bin Type
        with st.container(border=True):
            bin_types = ["All"] + sorted(df["Type"].unique().tolist())
            selected_bin_type = st.selectbox("Filter by Bin Type", bin_types, key="bin_type_filter")
            
        if selected_bin_type != "All":
            df = df[df["Type"] == selected_bin_type]

        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No bin history available")

def show_dispatch_history(history_service):
    """Display dispatch history with filter by dispatch type"""
    stack = history_service.get_stack("dispatch")
    if stack and not stack.is_empty():
        history_list = stack.to_list()[::-1]  # newest first

        # Filter by Dispatch Type
        with st.container(border=True):
            dispatch_types = ["All"] + sorted(set(h.get("type") for h in history_list))
            selected_dispatch_type = st.selectbox("Filter by Dispatch Type", dispatch_types, key="dispatch_type_filter")

        for i, action in enumerate(history_list, 1):
            action_type = action.get("type")
            if selected_dispatch_type != "All" and action_type != selected_dispatch_type:
                continue
            data = action.get("data", {})
            vehicles = data.get("vehicles", [])
            bins = data.get("bins", [])

            with st.container(border=True):
                st.markdown(f"**Dispatch Action #{i}** - {action_type}")
                
                col1, col2 = st.columns(2)

                with col1:
                    st.caption("Vehicles")
                    vehicle_data = []
                    for v in vehicles[:10]:
                        vehicle_data.append({
                            "ID": v.get("id"),
                            "Load": v.get("load"),
                            "Capacity": v.get("capacity"),
                            "Available": "Yes" if v.get("available") else "No"
                        })
                    if vehicle_data:
                        st.dataframe(pd.DataFrame(vehicle_data), use_container_width=True, hide_index=True)
                    if len(vehicles) > 10:
                        st.caption(f"... and {len(vehicles) - 10} more vehicles")

                with col2:
                    st.caption("Bins")
                    bin_data = []
                    for b in bins[:10]:
                        bin_data.append({
                            "ID": b.get("id"),
                            "Location": b.get("location"),
                            "Type": b.get("bin_type"),
                            "Fill": f"{b.get('fill_level', 0)}%"
                        })
                    if bin_data:
                        st.dataframe(pd.DataFrame(bin_data), use_container_width=True, hide_index=True)
                    if len(bins) > 10:
                        st.caption(f"... and {len(bins) - 10} more bins")
    else:
        st.info("No dispatch history available")

def show_history_page():
    st.title("System History")
    
    # Inject Custom CSS
    from utils.ui_helper import load_css
    load_css("metric_card.css")
    
    history_service = HistoryService()
    
    # Metrics overview
    request_stack = history_service.get_stack("request")
    bin_stack = history_service.get_stack("bin")
    dispatch_stack = history_service.get_stack("dispatch")
    
    request_count = len(request_stack.to_list()) if request_stack and not request_stack.is_empty() else 0
    bin_count = len(bin_stack.to_list()) if bin_stack and not bin_stack.is_empty() else 0
    dispatch_count = len(dispatch_stack.to_list()) if dispatch_stack and not dispatch_stack.is_empty() else 0
    total_actions = request_count + bin_count + dispatch_count
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card" style="background-color: #e0f2fe;">
            <div class="metric-label">Total Actions</div>
            <div class="metric-value">{total_actions}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div class="metric-card" style="background-color: #dcfce7;">
            <div class="metric-label">Request Actions</div>
            <div class="metric-value">{request_count}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
        <div class="metric-card" style="background-color: #ffedd5;">
            <div class="metric-label">Bin Actions</div>
            <div class="metric-value">{bin_count}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown(f"""
        <div class="metric-card" style="background-color: #f3e8ff;">
            <div class="metric-label">Dispatch Actions</div>
            <div class="metric-value">{dispatch_count}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tabs for different history types
    tab1, tab2, tab3 = st.tabs(["Request History", "Bin History", "Dispatch History"])
    
    with tab1:
        st.markdown("### Request History")
        show_request_history(history_service)
    
    with tab2:
        st.markdown("### Bin History")
        show_bin_history(history_service)
    
    with tab3:
        st.markdown("### Dispatch History")
        show_dispatch_history(history_service)
