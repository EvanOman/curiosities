"""Streamlit app for daylight duration visualization."""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
import plotly.graph_objects as go

from daylight.calculations import daylight_duration, daylight_duration_array
from daylight.visualization import (
    create_mercator_heatmap_plotly,
    plot_daylight_by_latitude,
    plot_daylight_over_time,
    create_comparison_plot
)


def main():
    st.set_page_config(
        page_title="Daylight Duration Visualizer",
        page_icon="☀️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("☀️ Daylight Duration Visualizer")
    st.markdown("""
    Explore how daylight duration varies across the globe and throughout the year.
    This interactive visualization shows the relationship between latitude, date, and daylight hours.
    """)
    
    # Sidebar controls
    st.sidebar.header("Controls")
    
    # Initialize session state for day of year
    if 'day_of_year' not in st.session_state:
        st.session_state.day_of_year = min(date.today().timetuple().tm_yday, 365)
    
    # Quick date selection buttons
    st.sidebar.markdown("### 🗓️ Quick Select:")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.sidebar.button("Jan 1", key="jan1"):
            st.session_state.day_of_year = 1
        if st.sidebar.button("Mar 20", key="mar20"):  # Spring equinox
            st.session_state.day_of_year = 79
        if st.sidebar.button("Jun 21", key="jun21"):  # Summer solstice
            st.session_state.day_of_year = 172
    with col2:
        if st.sidebar.button("Sep 22", key="sep22"):  # Fall equinox
            st.session_state.day_of_year = 265
        if st.sidebar.button("Dec 21", key="dec21"):  # Winter solstice
            st.session_state.day_of_year = 355
        if st.sidebar.button("Dec 31", key="dec31"):
            st.session_state.day_of_year = 365
    
    # Day of year selection
    selected_day_of_year = st.sidebar.slider(
        "Day of Year",
        min_value=1,
        max_value=365,
        value=st.session_state.day_of_year,
        help="1 = January 1st, 365 = December 31st",
        key="day_slider"
    )
    
    # Update session state
    st.session_state.day_of_year = selected_day_of_year
    
    # Convert day of year to date (using 2024 as reference year)
    reference_year = 2024
    selected_date = date(reference_year, 1, 1) + timedelta(days=selected_day_of_year - 1)
    
    # Show the actual date
    st.sidebar.info(f"📅 **{selected_date.strftime('%B %d')}** (Day {selected_day_of_year})")
    
    # Animation controls
    st.sidebar.markdown("### 🎬 Animation")
    
    # Animation toggle - now uses Plotly's built-in animation
    enable_plotly_animation = st.sidebar.checkbox(
        "Enable Plotly Animation", 
        value=False,
        help="Creates smooth client-side animation using Plotly's built-in controls"
    )
    
    if enable_plotly_animation:
        # Animation step size
        animation_step = st.sidebar.slider(
            "Animation Step (days)",
            min_value=1,
            max_value=30,
            value=7,
            help="Days between animation frames (smaller = smoother but slower loading)"
        )
        
        st.sidebar.info("🎬 **Plotly Animation Enabled**\nUse the ▶️ Play button and slider that appear below the chart!")
        st.sidebar.warning("⚠️ **Date Sync**: The animation shows the full year cycle starting from January 1st. The date slider above shows your selected starting date for the static view.")
    else:
        animation_step = 7  # Default value when animation is disabled
    
    # Visualization type selection
    viz_type = st.sidebar.selectbox(
        "Visualization Type",
        ["World Heatmap", "Latitude Profile", "Time Series", "Location Comparison"]
    )
    
    # Main content area
    if viz_type == "World Heatmap":
        st.header("🌍 Global Daylight Duration Heatmap")
        st.markdown(f"**Date:** {selected_date.strftime('%B %d, %Y')}")
        
        # Map options
        use_world_map = st.sidebar.checkbox(
            "Show World Map Overlay",
            value=True,
            help="Overlay daylight data on actual world map geography"
        )
        
        # Resolution slider
        resolution = st.sidebar.slider(
            "Map Resolution (degrees)",
            min_value=1.0,
            max_value=10.0,
            value=3.0,
            step=1.0,
            help="Lower values = higher resolution (slower)"
        )
        
        with st.spinner("Generating heatmap..." + (" (with animation frames)" if enable_plotly_animation else "")):
            fig = create_mercator_heatmap_plotly(
                selected_date, 
                resolution, 
                enable_animation=enable_plotly_animation,
                animation_step=animation_step,
                use_world_map=use_world_map
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Add explanation
        if enable_plotly_animation:
            st.info("""
            **How to use the animation:**
            - Click the **▶️ Play** button below the chart to start the animation
            - Use the **⏸️ Pause** button to stop
            - Drag the **slider** to jump to any day of the year
            - The animation shows the complete yearly cycle (Jan 1 - Dec 31)
            - Watch how daylight patterns shift dramatically with the seasons!
            
            **Map colors:**
            - **Dark** (purple/blue): Shorter daylight hours
            - **Bright** (yellow/green): Longer daylight hours  
            - **Red**: Maximum daylight (24 hours during polar summer)
            
            **World Map:** Toggle the world map overlay to see daylight patterns over actual geography with countries, oceans, and coastlines.
            
            **Note:** The animation runs independently from the date controls in the sidebar.
            """)
        else:
            st.info("""
            **How to read this map:**
            - **Dark colors** (purple/blue): Shorter daylight hours
            - **Bright colors** (yellow/green): Longer daylight hours
            - **Red**: Maximum daylight (up to 24 hours during polar summer)
            
            **World Map:** Toggle the world map overlay to see daylight patterns over actual geography with countries, oceans, and coastlines.
            
            - Enable Plotly Animation in the sidebar to see seasonal changes!
            """)
    
    elif viz_type == "Latitude Profile":
        st.header("📊 Daylight Duration by Latitude")
        st.markdown(f"**Date:** {selected_date.strftime('%B %d, %Y')}")
        
        # Latitude range selection
        lat_range = st.sidebar.slider(
            "Latitude Range",
            min_value=-90,
            max_value=90,
            value=(-90, 90),
            help="Select latitude range to display"
        )
        
        with st.spinner("Generating latitude profile..." + (" (with animation frames)" if enable_plotly_animation else "")):
            fig = plot_daylight_by_latitude(
                selected_date, 
                lat_range, 
                enable_animation=enable_plotly_animation,
                animation_step=animation_step
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Show key statistics
        latitudes = np.arange(lat_range[0], lat_range[1] + 1, 1)
        daylight_hours = daylight_duration_array(latitudes, selected_date)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Max Daylight", f"{daylight_hours.max():.1f} hours")
        with col2:
            st.metric("Min Daylight", f"{daylight_hours.min():.1f} hours")
        with col3:
            st.metric("Equator Daylight", f"{daylight_duration(0, selected_date):.1f} hours")
        with col4:
            variation = daylight_hours.max() - daylight_hours.min()
            st.metric("Variation", f"{variation:.1f} hours")
    
    elif viz_type == "Time Series":
        st.header("📈 Daylight Duration Over Time")
        
        # Latitude selection
        selected_latitude = st.sidebar.slider(
            "Select Latitude",
            min_value=-90.0,
            max_value=90.0,
            value=45.0,
            step=1.0,
            help="Choose latitude to analyze"
        )
        
        # Year selection
        selected_year = st.sidebar.selectbox(
            "Select Year",
            options=list(range(2020, 2031)),
            index=4  # Default to 2024
        )
        
        with st.spinner("Generating time series..."):
            fig = plot_daylight_over_time(selected_latitude, selected_year)
            st.plotly_chart(fig, use_container_width=True)
        
        # Show current date information
        current_daylight = daylight_duration(selected_latitude, selected_date)
        st.info(f"**Current daylight at {selected_latitude}°:** {current_daylight:.1f} hours")
        
        # Add location examples
        st.sidebar.markdown("### 📍 Try These Locations:")
        location_examples = {
            "Equator (0°)": 0,
            "Tropics (±23.5°)": 23.5,
            "Oslo, Norway (60°)": 60,
            "Arctic Circle (66.5°)": 66.5,
            "North Pole (90°)": 90
        }
        
        for location, lat in location_examples.items():
            if st.sidebar.button(location):
                st.sidebar.success(f"Set to {lat}°")
                # Note: This would need state management to actually update the slider
    
    elif viz_type == "Location Comparison":
        st.header("🔍 Compare Multiple Locations")
        
        # Multi-latitude selection
        st.sidebar.markdown("### Select Latitudes to Compare")
        comparison_lats = []
        
        # Predefined locations
        preset_locations = st.sidebar.checkbox("Use Preset Locations")
        if preset_locations:
            comparison_lats = [0, 23.5, 45, 60, 75, -23.5, -45, -60]
        else:
            # Custom latitude inputs
            num_locations = st.sidebar.slider("Number of Locations", 2, 8, 4)
            for i in range(num_locations):
                lat = st.sidebar.number_input(
                    f"Latitude {i+1}",
                    min_value=-90.0,
                    max_value=90.0,
                    value=float(i * 30 - 45),
                    step=1.0,
                    key=f"lat_{i}"
                )
                comparison_lats.append(lat)
        
        if comparison_lats:
            with st.spinner("Generating comparison plot..." + (" (with animation frames)" if enable_plotly_animation else "")):
                fig = create_comparison_plot(
                    comparison_lats, 
                    selected_date,
                    enable_animation=enable_plotly_animation,
                    animation_step=animation_step
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Show comparison table for selected date
            st.subheader(f"Daylight Hours on {selected_date.strftime('%B %d, %Y')}")
            
            comparison_data = []
            for lat in comparison_lats:
                daylight_hours = daylight_duration(lat, selected_date)
                comparison_data.append({
                    "Latitude": f"{lat}°",
                    "Daylight Hours": f"{daylight_hours:.1f}",
                    "Difference from 12h": f"{daylight_hours - 12:.1f}"
                })
            
            df = pd.DataFrame(comparison_data)
            st.dataframe(df, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    **About:** This app calculates daylight duration using astronomical formulas based on the sunrise equation.
    Calculations account for seasonal variations in solar declination and handle polar day/night conditions.
    
    **Animation:** Enable Plotly Animation for smooth, interactive visualization of seasonal changes. The animation runs in your browser with built-in play/pause controls and a scrub slider.
    
    **Note:** Times are calculated for sea level and don't account for atmospheric refraction or local terrain.
    """)


if __name__ == "__main__":
    main()