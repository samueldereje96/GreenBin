# pages/home.py or wherever you show the report
import streamlit as st
import pandas as pd
import plotly.express as px
from services.reporting_service import ReportService
from services.prediction_service import PredictionService
from utils.ui_helper import load_css

def show_home(bin_service, vehicle_service):
    st.title("GreenBin – Smart Waste Management")

    st.subheader("Environmental & Operational Report")
    load_css("metric_card.css")

    report_service = ReportService()

    # Summary metrics
    total_requests = report_service.total_requests()
    total_bins = len(bin_service.bins)
    total_facilities = len(report_service.facility_service.get_all())
    total_vehicles = len(vehicle_service.vehicles)

    col1, col2, col3, col4 = st.columns(4)
    
    # Requests - Light Blue
    with col1:
        st.markdown(f"""
        <div class="metric-card row-layout" style="background-color: #e0f2fe;">
            <div class="metric-content">
                <div class="metric-label">Total Requests</div>
                <div class="metric-value">{total_requests}</div>
            </div>
            <div class="metric-icon">
                <svg xmlns="http://www.w3.org/2000/svg" height="32" viewBox="0 0 24 24" width="32" fill="#0284c7">
                    <path d="M19 3h-4.18C14.4 1.84 13.3 1 12 1c-1.3 0-2.4.84-2.82 2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 0c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm2 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
                </svg>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    # Bins - Light Green
    with col2:
        st.markdown(f"""
        <div class="metric-card row-layout" style="background-color: #dcfce7;">
            <div class="metric-content">
                <div class="metric-label">Total Bins</div>
                <div class="metric-value">{total_bins}</div>
            </div>
            <div class="metric-icon">
                <svg xmlns="http://www.w3.org/2000/svg" height="32" viewBox="0 0 24 24" width="32" fill="#16a34a">
                    <path d="M16 9v10H8V9h8m-1.5-6h-5l-1 1H5v2h14V4h-3.5l-1-1zM18 7H6v12c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7z"/>
                </svg>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    # Facilities - Light Orange
    with col3:
        st.markdown(f"""
        <div class="metric-card row-layout" style="background-color: #ffedd5;">
            <div class="metric-content">
                <div class="metric-label">Total Facilities</div>
                <div class="metric-value">{total_facilities}</div>
            </div>
            <div class="metric-icon">
                <svg xmlns="http://www.w3.org/2000/svg" height="32" viewBox="0 0 24 24" width="32" fill="#ea580c">
                    <path d="M12 7V3H2v18h20V7H12zM6 19H4v-2h2v2zm0-4H4v-2h2v2zm0-4H4V9h2v2zm0-4H4V5h2v2zm4 12H8v-2h2v2zm0-4H8v-2h2v2zm0-4H8V9h2v2zm0-4H8V5h2v2zm10 12h-8v-2h2v-2h-2v-2h2v-2h-2V9h8v10zm-2-8h-2v2h2v-2zm0 4h-2v2h2v-2z"/>
                </svg>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    # Vehicles - Light Purple
    with col4:
        st.markdown(f"""
        <div class="metric-card row-layout" style="background-color: #f3e8ff;">
            <div class="metric-content">
                <div class="metric-label">Total Vehicles</div>
                <div class="metric-value">{total_vehicles}</div>
            </div>
            <div class="metric-icon">
                <svg xmlns="http://www.w3.org/2000/svg" height="32" viewBox="0 0 24 24" width="32" fill="#9333ea">
                    <path d="M20 8h-3V4H3c-1.1 0-2 .9-2 2v11h2c0 1.66 1.34 3 3 3s3-1.34 3-3h6c0 1.66 1.34 3 3 3s3-1.34 3-3h2v-5l-3-4zM6 18.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zm13.5-9l1.96 2.5H17V9.5h2.5zm-1.5 9c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5z"/>
                </svg>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Container 1: Table + Pie chart
    with st.container():
        report_service = ReportService() # Keep this if other parts of the report still need it
        co2_dict = report_service.co2_saved_per_facility()
        df_co2 = pd.DataFrame(list(co2_dict.items()), columns=["Facility", "CO2_Saved"])
        
        left, right = st.columns([1,1])
        with left:
            with st.container(border=True):
                st.subheader("CO2 Saved per Facility (kg)")
                st.dataframe(df_co2, use_container_width=True, hide_index=True)

        with right:
            with st.container(border=True):
                st.subheader("CO2 Saved Distribution")
                fig = px.pie(df_co2, names="Facility", values="CO2_Saved",
                             color_discrete_sequence=px.colors.qualitative.Set2,
                             title="CO2 Saved Pie")
                fig.update_layout(
                    width=400, height=400, 
                    margin=dict(l=20,r=20,t=40,b=20),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig, use_container_width=True)

    # Container 2: Bar chart
    with st.container():
        with st.container(border=True):
            st.subheader("CO2 Saved per Facility (Bar Chart)")
            fig2 = px.bar(df_co2, x="Facility", y="CO2_Saved",
                          color="CO2_Saved", color_continuous_scale="Viridis",
                          title="CO2 Saved Bar Chart")
            fig2.update_layout(
                width=600, height=400, 
                margin=dict(l=20,r=20,t=40,b=20),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig2, use_container_width=True)


    # Initialize prediction
    prediction_service = PredictionService(bin_service)
    top_bins = prediction_service.top_overflow_bins(hours_ahead=2, top_n=20)

    df_top_bins = pd.DataFrame([
        {"Bin ID": b.id, "Location": b.location, "Predicted Fill (%)": fill}
        for fill, b in top_bins
    ])

    left, right = st.columns([1,1])
    with left:
        with st.container(border=True):
            st.subheader("Top Bins Predicted to Overflow")
            st.dataframe(df_top_bins, use_container_width=True, hide_index=True)

    with right:
        with st.container(border=True):
            st.subheader("Overflow Risk (Bar Chart)")
            fig = px.bar(df_top_bins, x="Location", y="Predicted Fill (%)",
                        color="Predicted Fill (%)", color_continuous_scale="Reds",
                        title="Predicted Fill Levels")
            fig.update_layout(
                width=500, height=400, 
                margin=dict(l=20,r=20,t=40,b=20),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
