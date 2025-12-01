# helpers/history_helpers.py
import streamlit as st
import pandas as pd
from services.history_service import HistoryService

def show_history_search(category="request"):
    """
    Display a searchable/filterable table for a given history category.
    category: "request", "bin", "dispatch"
    """
    history_service = HistoryService()
    history_data = history_service.get_category(category)  # list of dicts
    
    if not history_data:
        st.info(f"No {category} history available.")
        return

    # Convert history to a DataFrame depending on category
    if category == "request":
        df = pd.DataFrame([{
            "User": h["data"]["user"],
            "Bin ID": h["data"]["bin_id"],
            "Request Type": h["data"]["request_type"],
            "Time": h["data"]["time"]
        } for h in history_data])
        
        # Filters
        users = ["All"] + sorted(df["User"].unique().tolist())
        request_types = ["All"] + sorted(df["Request Type"].unique().tolist())

        selected_user = st.selectbox("Filter by User", users, key="user_filter")
        selected_type = st.selectbox("Filter by Request Type", request_types, key="type_filter")

        # Apply filters
        if selected_user != "All":
            df = df[df["User"] == selected_user]
        if selected_type != "All":
            df = df[df["Request Type"] == selected_type]

    elif category == "bin":
        df = pd.DataFrame([{
            "Bin ID": h["data"]["bin"]["id"],
            "Location": h["data"]["bin"]["location"],
            "Bin Type": h["data"]["bin"]["bin_type"],
            "Capacity": h["data"]["bin"]["capacity"],
            "Fill Level": h["data"]["bin"]["fill_level"]
        } for h in history_data])

        bin_types = ["All"] + sorted(df["Bin Type"].unique().tolist())
        selected_bin_type = st.selectbox("Filter by Bin Type", bin_types, key="bin_type_filter")

        if selected_bin_type != "All":
            df = df[df["Bin Type"] == selected_bin_type]

    elif category == "dispatch":
        # For dispatch, we can show simplified info
        df = pd.DataFrame([{
            "Dispatch Type": h["type"],
            "Vehicles Count": len(h["data"]["vehicles"]),
            "Bins Count": len(h["data"]["bins"])
        } for h in history_data])

    else:
        st.warning("Unknown category for history.")
        return

    st.subheader(f"{category.capitalize()} History")
    st.dataframe(df, use_container_width=True)
