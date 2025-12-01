import streamlit as st
import pandas as pd

def show_bins_page(bin_service):
    st.title("Bins Management")
    
    # Inject Custom CSS
    from utils.ui_helper import load_css
    load_css("metric_card.css")
    
    # Overview metrics at the top
    total_bins = len(bin_service.bins)
    full_bins = sum(1 for b in bin_service.bins if b.fill_level >= 90)
    half_bins = sum(1 for b in bin_service.bins if 50 <= b.fill_level < 90)
    empty_bins = sum(1 for b in bin_service.bins if b.fill_level < 50)
    avg_fill = sum(b.fill_level for b in bin_service.bins) / total_bins if total_bins > 0 else 0
    
    # Metrics row
    m1, m2, m3, m4, m5 = st.columns(5)
    
    with m1:
        st.markdown(f"""
        <div class="metric-card" style="background-color: #e0f2fe;">
            <div class="metric-label">Total Bins</div>
            <div class="metric-value">{total_bins}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with m2:
        st.markdown(f"""
        <div class="metric-card" style="background-color: #fee2e2;">
            <div class="metric-label">Critical (≥90%)</div>
            <div class="metric-value">{full_bins}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with m3:
        st.markdown(f"""
        <div class="metric-card" style="background-color: #ffedd5;">
            <div class="metric-label">Moderate</div>
            <div class="metric-value">{half_bins}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with m4:
        st.markdown(f"""
        <div class="metric-card" style="background-color: #dcfce7;">
            <div class="metric-label">Low (<50%)</div>
            <div class="metric-value">{empty_bins}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with m5:
        st.markdown(f"""
        <div class="metric-card" style="background-color: #f3e8ff;">
            <div class="metric-label">Avg Fill</div>
            <div class="metric-value">{avg_fill:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Main Content - Tabbed Interface
    tab1, tab2, tab3, tab4 = st.tabs(["Current Inventory", "Add Bin", "Update Bin", "Delete Bin"])
    
    # TAB 1: Current Inventory (with Undo)
    with tab1:
        with st.container(border=True):
            col_header, col_undo = st.columns([3, 1])
            with col_header:
                st.subheader("Inventory Overview")
            with col_undo:
                if st.button("Undo Last Action", use_container_width=True, type="secondary"):
                    result = bin_service.undo_last()
                    if result:
                        st.toast(result, icon="↩️")
                        st.rerun()
                    else:
                        st.warning("Nothing to undo")
            
            # Search and Sort Controls
            c_search, c_sort, c_order = st.columns([2, 1, 1])
            with c_search:
                search_query = st.text_input("Search", placeholder="Search by ID or Location", label_visibility="collapsed")
            with c_sort:
                sort_by = st.selectbox("Sort By", ["ID", "Fill Level", "Capacity", "Location"], label_visibility="collapsed")
            with c_order:
                sort_order = st.selectbox("Order", ["Ascending", "Descending"], label_visibility="collapsed")

            if bin_service.bins:
                bins_data = []
                for b in bin_service.bins:
                    # Add status based on fill level
                    if b.fill_level >= 90:
                        status = "Critical"
                    elif b.fill_level >= 70:
                        status = "High"
                    elif b.fill_level >= 40:
                        status = "Moderate"
                    else:
                        status = "Low"
                    
                    bins_data.append({
                        "ID": b.id,
                        "Location": b.location,
                        "Type": b.bin_type.capitalize(),
                        "Fill Level": b.fill_level,
                        "Capacity": b.capacity,
                        "Status": status,
                        "X": b.x,
                        "Y": b.y
                    })
                
                df = pd.DataFrame(bins_data)
                
                # Filter Logic
                if search_query:
                    query = search_query.lower()
                    df = df[
                        df["Location"].str.lower().str.contains(query) | 
                        df["ID"].astype(str).str.contains(query)
                    ]
                
                # Sort Logic
                ascending = sort_order == "Ascending"
                if sort_by == "ID":
                    df = df.sort_values("ID", ascending=ascending)
                elif sort_by == "Fill Level":
                    df = df.sort_values("Fill Level", ascending=ascending)
                elif sort_by == "Capacity":
                    df = df.sort_values("Capacity", ascending=ascending)
                elif sort_by == "Location":
                    df = df.sort_values("Location", ascending=ascending)
                
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Fill Level": st.column_config.ProgressColumn(
                            "Fill Level",
                            help="Current fill percentage",
                            format="%d%%",
                            min_value=0,
                            max_value=100,
                        ),
                        "Status": st.column_config.TextColumn(
                            "Status",
                        ),
                        "Type": st.column_config.TextColumn(
                            "Type",
                            width="small"
                        )
                    }
                )
            else:
                st.info("No bins available. Add your first bin to get started!")

    # TAB 2: Add Bin
    with tab2:
        with st.container(border=True):
            st.subheader("Add New Bin")
            with st.form("add_bin_form", clear_on_submit=True):
                location = st.text_input("Location", placeholder="e.g., Main St")
                
                c1, c2 = st.columns(2)
                with c1:
                    x = st.number_input("X (Latitude)", value=0.0, format="%.4f", step=0.0001)
                    bin_type = st.selectbox("Type", ["household", "industrial", "recycling"])
                with c2:
                    y = st.number_input("Y (Longitude)", value=0.0, format="%.4f", step=0.0001)
                    fill = st.slider("Fill %", 0, 100, 0)
                
                submitted = st.form_submit_button("Add Bin", use_container_width=True, type="primary")
                
                if submitted:
                    if location.strip():
                        bin_service.add_bin(location, fill, x,y, bin_type)
                        bin_service.save_bins()
                        st.success(f"Added!")
                        st.rerun()
                    else:
                        st.error("Location required")

    # TAB 3: Update Bin
    with tab3:
        with st.container(border=True):
            st.subheader("Update Bin Status")
            bin_ids = [b.id for b in bin_service.bins]
            
            if bin_ids:
                with st.form("update_bin_form"):
                    selected_id = st.selectbox("Select Bin", bin_ids)
                    
                    # Show current fill level
                    current_bin = next((b for b in bin_service.bins if b.id == selected_id), None)
                    if current_bin:
                        st.caption(f"Current: {current_bin.fill_level}%")
                    
                    new_level = st.slider("New Fill %", 0, 100, 
                                         value=current_bin.fill_level if current_bin else 0)
                    
                    submitted = st.form_submit_button("Update", use_container_width=True, type="primary")
                    
                    if submitted:
                        bin_service.update_bin(selected_id, new_level)
                        st.success(f"Updated!")
                        st.rerun()
            else:
                st.info("No bins")

    # TAB 4: Delete Bin
    with tab4:
        with st.container(border=True):
            st.subheader("Remove Bin")
            bins_removal = [b.id for b in bin_service.bins]
            
            if bins_removal:
                with st.form("delete_bin_form"):
                    removed_id = st.selectbox("Select Bin", bins_removal)
                    
                    submitted = st.form_submit_button("Delete", use_container_width=True, type="primary")
                    
                    if submitted:
                        bin_service.remove_bin(removed_id)
                        st.success(f"Deleted!")
                        st.rerun()
            else:
                st.info("No bins")
