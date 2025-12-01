import streamlit as st
import pandas as pd

def show_facilities_page(service):
    st.title("Recycling Facilities Management")
    
    # Inject Custom CSS
    from utils.ui_helper import load_css
    load_css("metric_card.css")
    
    # --- Metrics Section ---
    facilities = service.get_all()
    total_facilities = len(facilities)
    avg_efficiency = sum(f.efficiency for f in facilities) / total_facilities if total_facilities > 0 else 0
    total_capacity = sum(f.capacity for f in facilities)
    
    # Most common type
    if facilities:
        types = [f.type for f in facilities]
        most_common_type = max(set(types), key=types.count).capitalize()
    else:
        most_common_type = "N/A"
        
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown(f"""
        <div class="metric-card" style="background-color: #e0f2fe;">
            <div class="metric-label">Total Facilities</div>
            <div class="metric-value">{total_facilities}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown(f"""
        <div class="metric-card" style="background-color: #dcfce7;">
            <div class="metric-label">Avg Efficiency</div>
            <div class="metric-value">{avg_efficiency:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c3:
        st.markdown(f"""
        <div class="metric-card" style="background-color: #ffedd5;">
            <div class="metric-label">Total Capacity</div>
            <div class="metric-value">{total_capacity}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c4:
        st.markdown(f"""
        <div class="metric-card" style="background-color: #f3e8ff;">
            <div class="metric-label">Primary Type</div>
            <div class="metric-value">{most_common_type}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # --- Main Content: Tabs ---
    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Add Facility", "Update Facility", "Delete Facility"])
    
    # TAB 1: Overview
    with tab1:
        # Search & Filter
        with st.container(border=True):
            col_search, col_filter, col_sort = st.columns(3)
            
            with col_search:
                search_name = st.text_input("Search", placeholder="Facility name...", key="search_name")
            
            with col_filter:
                filter_type = st.selectbox("Filter Type", ["All", "household", "industrial", "recycling"], key="filter_type")
                
            with col_sort:
                sort_option = st.selectbox("Sort By", ["ID", "Name", "Capacity", "Efficiency"], key="sort_option")
        
        st.markdown("### Facilities Grid")
        
        # Filter Logic
        filtered_facilities = facilities
        if search_name:
            filtered_facilities = [f for f in filtered_facilities if search_name.lower() in f.name.lower()]
        
        if filter_type != "All":
            filtered_facilities = [f for f in filtered_facilities if f.type == filter_type]
            
        # Sort Logic
        if sort_option == "ID":
            filtered_facilities.sort(key=lambda x: x.id)
        elif sort_option == "Name":
            filtered_facilities.sort(key=lambda x: x.name.lower())
        elif sort_option == "Capacity":
            filtered_facilities.sort(key=lambda x: x.capacity, reverse=True)
        elif sort_option == "Efficiency":
            filtered_facilities.sort(key=lambda x: x.efficiency, reverse=True)

        # Display Grid
        if filtered_facilities:
            cols = st.columns(3)
            for i, f in enumerate(filtered_facilities):
                with cols[i % 3]:
                    with st.container(border=True):
                        # Clean Name Display (No Icons)
                        st.markdown(f"### {f.name}")
                        st.caption(f"ID: {f.id} | {f.type.capitalize()}")
                        st.markdown(f"{f.location}")
                        
                        m1, m2 = st.columns(2)
                        m1.metric("Capacity", f.capacity)
                        m2.metric("Efficiency", f"{f.efficiency}%")
        else:
            st.info("No facilities found.")

    # TAB 2: Add Facility
    with tab2:
        with st.container(border=True):
            st.subheader("Add New Facility")
            
            with st.form("add_facility_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                
                with c1:
                    new_name = st.text_input("Name", placeholder="e.g., Central Recycling Center")
                    new_loc = st.text_input("Location", placeholder="e.g., Downtown District")
                    new_type = st.selectbox("Type", ["household", "industrial", "recycling"])
                
                with c2:
                    new_cap = st.number_input("Capacity", min_value=0, value=100, step=10)
                    new_eff = st.number_input("Efficiency (%)", min_value=0, max_value=100, value=80, step=5)
                    c_x, c_y = st.columns(2)
                    new_x = c_x.number_input("X", value=0)
                    new_y = c_y.number_input("Y", value=0)
                
                submitted = st.form_submit_button("Add Facility", type="primary", use_container_width=True)
                
                if submitted:
                    if new_name and new_loc:
                        service.add_facility(new_name, new_loc, int(new_x), int(new_y), new_type, new_cap, new_eff)
                        st.success(f"Added '{new_name}'!")
                        st.rerun()
                    else:
                        st.error("Name and Location required.")

    # TAB 3: Update Facility
    with tab3:
        with st.container(border=True):
            st.subheader("Update Facility")
            
            all_ids = [f.id for f in facilities]
            if all_ids:
                # Selectbox OUTSIDE form for reactivity
                facility_options = {f"{f.name} (ID: {f.id})": f.id for f in facilities}
                selected_label = st.selectbox("Select Facility to Update", list(facility_options.keys()), key="update_facility_select")
                selected_id = facility_options[selected_label]
                
                # Get current values
                current = next((f for f in facilities if f.id == selected_id), None)
                
                if current:
                    st.info(f"Editing: **{current.name}**")
                    
                    with st.form("update_facility_form"):
                        c1, c2 = st.columns(2)
                        with c1:
                            up_cap = st.number_input("New Capacity", min_value=0, value=current.capacity)
                            up_eff = st.number_input("New Efficiency (%)", min_value=0, max_value=100, value=current.efficiency)
                        with c2:
                            up_loc = st.text_input("New Location", value=current.location)
                            
                        submitted = st.form_submit_button("Update Facility", type="primary", use_container_width=True)
                        
                        if submitted:
                            service.update_facility(selected_id, capacity=up_cap, efficiency=up_eff, location=up_loc)
                            st.success("Facility updated!")
                            st.rerun()
            else:
                st.info("No facilities to update.")

    # TAB 4: Delete Facility
    with tab4:
        with st.container(border=True):
            st.subheader("Delete Facility")
            
            if facilities:
                # Selectbox OUTSIDE form for reactivity
                facility_delete_options = {f"{f.name} (ID: {f.id})": f.id for f in facilities}
                selected_del_label = st.selectbox("Select Facility to Delete", list(facility_delete_options.keys()), key="delete_facility_select_tab4")
                selected_del_id = facility_delete_options[selected_del_label]
                
                if st.button("Delete Facility", type="primary", use_container_width=True):
                    service.remove_facility(selected_del_id)
                    st.success("Deleted!")
                    st.rerun()
            else:
                st.info("No facilities to delete.")
