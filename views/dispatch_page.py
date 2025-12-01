import streamlit as st
import json
import streamlit.components.v1 as components

def show_dispatch_page(vehicle_service, bin_service):
    st.title("City Map Operations (Dubai)")
    
    # Inject Custom CSS
    from utils.ui_helper import load_css, get_map_html
    load_css("metric_card.css")
    
    # Use passed services
    service = vehicle_service
    
    # Metrics
    total_bins = len(bin_service.bins)
    full_bins = sum(1 for b in bin_service.bins if b.fill_level > 80)
    active_vehicles = sum(1 for v in service.vehicles if v.target_bin)
    
    # Calculate total distance (km)
    total_distance_m = sum(getattr(v, "total_distance", 0) for v in service.vehicles)
    total_distance_km = total_distance_m / 1000.0
    
    # Metrics Row
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown(f"""
        <div class="metric-card" style="background-color: #e0f2fe;">
            <div class="metric-label">Total Bins</div>
            <div class="metric-value">{total_bins}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown(f"""
        <div class="metric-card" style="background-color: #fee2e2;">
            <div class="metric-label">Critical (>80%)</div>
            <div class="metric-value">{full_bins}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c3:
        st.markdown(f"""
        <div class="metric-card" style="background-color: #ffedd5;">
            <div class="metric-label">Active Vehicles</div>
            <div class="metric-value">{active_vehicles}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c4:
        st.markdown(f"""
        <div class="metric-card" style="background-color: #f3e8ff;">
            <div class="metric-label">Fleet Distance</div>
            <div class="metric-value">{total_distance_km:.2f} km</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")

    # Prepare Data for JavaScript (Moved up to be available for map generation)
    bins_data = []
    for b in bin_service.bins:
        bins_data.append({
            "id": b.id,
            "lat": b.x,
            "lon": b.y,
            "fill": b.fill_level,
            "type": b.bin_type,
            "is_critical": b.fill_level > 80
        })

    facilities_data = []
    # VehicleService has facility_service
    for f in service.facility_service.get_all():
        facilities_data.append({
            "id": f.id,
            "name": f.name,
            "lat": f.x,
            "lon": f.y,
            "type": f.type
        })

    vehicles_data = []
    for v in service.vehicles:
        route = []
        if hasattr(v, "current_route") and v.current_route:
            # OSRM/Dijkstra returns [lon, lat], Leaflet needs [lat, lon]
            route = [[pt[1], pt[0]] for pt in v.current_route]
            
        vehicles_data.append({
            "id": v.id,
            "lat": v.x,
            "lon": v.y,
            "has_target": v.target_bin is not None,
            "route": route
        })

    # Convert to JSON for injection
    bins_json = json.dumps(bins_data)
    facilities_json = json.dumps(facilities_data)
    vehicles_json = json.dumps(vehicles_data)

    # HTML/JS Code
    html_code = get_map_html(bins_json, facilities_json, vehicles_json)
    
    # Tabs
    tab1, tab2 = st.tabs(["Live Map", "Fleet Status"])
    
    # TAB 1: Live Map & Controls
    with tab1:
        with st.container(border=True):
            # Controls Area
            col_a, col_b = st.columns(2)
            
            with col_a:
                if st.button("Dispatch Vehicles", type="primary", use_container_width=True):
                    service.dispatch_all_vehicles()
                    st.success("Vehicles dispatched!")
                    st.rerun()
            
            with col_b:
                if st.button("Undo Last Action", use_container_width=True):
                    result = service.undo_last()
                    if result:
                        st.toast(result, icon="↩️")
                        st.rerun()
                    else:
                        st.warning("Nothing to undo")
            
            st.markdown("---")
            
            # Map
            components.html(html_code, height=620)

    # TAB 2: Fleet Status
    with tab2:
        with st.container(border=True):
            st.subheader("Active Fleet Details")
            
            for v in service.vehicles:
                if v.target_bin:
                    st.markdown(f"**Vehicle {v.id}**")
                    st.markdown(f"Target Bin: {v.target_bin.id} ({v.target_bin.location})")
                    if v.target_facility:
                        st.markdown(f"Target Facility: {v.target_facility.name}")
                    
                    if hasattr(v, "total_distance") and v.total_distance:
                        dist_km = v.total_distance / 1000
                        st.markdown(f"**Total Distance:** {dist_km:.2f} km")
                    
                    st.markdown("---")
                else:
                     st.markdown(f"**Vehicle {v.id}**: Idle")
                     st.markdown("---")
