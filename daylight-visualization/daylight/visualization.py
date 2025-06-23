"""Visualization functions for daylight data."""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import folium
from folium import plugins
import matplotlib.pyplot as plt
from datetime import date, datetime, timedelta
from typing import Union, Optional, Tuple

from .calculations import daylight_duration_array, create_daylight_grid, daylight_duration


def create_mercator_heatmap_plotly(input_date: Union[date, datetime], 
                                  resolution: float = 2.0) -> go.Figure:
    """
    Create a Plotly heatmap showing daylight duration on a Mercator projection.
    
    Args:
        input_date: Date for calculation
        resolution: Grid resolution in degrees
        
    Returns:
        Plotly figure object
    """
    # Create daylight grid
    lat_grid, lon_grid, daylight_grid = create_daylight_grid(input_date, resolution, resolution)
    
    # Create the heatmap
    fig = go.Figure(data=go.Heatmap(
        z=daylight_grid,
        x=np.arange(-180, 180 + resolution, resolution),
        y=np.arange(-90, 90 + resolution, resolution),
        colorscale='Viridis',
        zmin=0,
        zmax=24,
        colorbar=dict(
            title="Daylight Hours"
        ),
        hovertemplate='Latitude: %{y:.1f}°<br>Longitude: %{x:.1f}°<br>Daylight: %{z:.1f} hours<extra></extra>'
    ))
    
    # Update layout for Mercator-like appearance
    fig.update_layout(
        title=f"Daylight Duration - {input_date.strftime('%B %d, %Y')}",
        xaxis_title="Longitude (°)",
        yaxis_title="Latitude (°)",
        width=1000,
        height=600,
        xaxis=dict(range=[-180, 180]),
        yaxis=dict(range=[-90, 90])
    )
    
    return fig


def create_folium_heatmap(input_date: Union[date, datetime], 
                         resolution: float = 5.0) -> folium.Map:
    """
    Create a Folium map with daylight duration heatmap.
    
    Args:
        input_date: Date for calculation
        resolution: Grid resolution in degrees
        
    Returns:
        Folium map object
    """
    # Create daylight grid
    lat_grid, lon_grid, daylight_grid = create_daylight_grid(input_date, resolution, resolution)
    
    # Create base map
    m = folium.Map(location=[0, 0], zoom_start=2)
    
    # Prepare data for heatmap
    heat_data = []
    for i in range(lat_grid.shape[0]):
        for j in range(lat_grid.shape[1]):
            lat = lat_grid[i, j]
            lon = lon_grid[i, j]
            intensity = daylight_grid[i, j] / 24.0  # Normalize to 0-1
            heat_data.append([lat, lon, intensity])
    
    # Add heatmap layer
    plugins.HeatMap(heat_data, radius=15, blur=10, gradient={
        0.0: 'navy',
        0.25: 'blue', 
        0.5: 'cyan',
        0.75: 'yellow',
        1.0: 'red'
    }).add_to(m)
    
    return m


def plot_daylight_by_latitude(input_date: Union[date, datetime],
                             lat_range: Tuple[float, float] = (-90, 90),
                             resolution: float = 1.0) -> go.Figure:
    """
    Plot daylight duration vs latitude for a specific date.
    
    Args:
        input_date: Date for calculation
        lat_range: Tuple of (min_lat, max_lat)
        resolution: Latitude resolution in degrees
        
    Returns:
        Plotly figure object
    """
    latitudes = np.arange(lat_range[0], lat_range[1] + resolution, resolution)
    daylight_hours = daylight_duration_array(latitudes, input_date)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=latitudes,
        y=daylight_hours,
        mode='lines',
        name='Daylight Duration',
        line=dict(width=3, color='orange'),
        hovertemplate='Latitude: %{x:.1f}°<br>Daylight: %{y:.1f} hours<extra></extra>'
    ))
    
    # Add reference lines
    fig.add_hline(y=12, line_dash="dash", line_color="gray", 
                  annotation_text="12 hours (equinox)")
    fig.add_vline(x=0, line_dash="dash", line_color="gray",
                  annotation_text="Equator")
    
    # Add seasonal context lines
    fig.add_vline(x=23.45, line_dash="dot", line_color="red", opacity=0.5,
                  annotation_text="Tropic of Cancer")
    fig.add_vline(x=-23.45, line_dash="dot", line_color="red", opacity=0.5,
                  annotation_text="Tropic of Capricorn")
    fig.add_vline(x=66.56, line_dash="dot", line_color="blue", opacity=0.5,
                  annotation_text="Arctic Circle")
    fig.add_vline(x=-66.56, line_dash="dot", line_color="blue", opacity=0.5,
                  annotation_text="Antarctic Circle")
    
    fig.update_layout(
        title=f"Daylight Duration by Latitude - {input_date.strftime('%B %d, %Y')}",
        xaxis_title="Latitude (°)",
        yaxis_title="Daylight Duration (hours)",
        xaxis=dict(range=lat_range, tickmode='linear', dtick=30),
        yaxis=dict(range=[0, 24]),
        width=800,
        height=500,
        showlegend=False
    )
    
    return fig


def plot_daylight_over_time(latitude: float,
                           year: int = 2024,
                           day_interval: int = 7) -> go.Figure:
    """
    Plot daylight duration over time for a specific latitude.
    
    Args:
        latitude: Latitude in degrees
        year: Year for calculation
        day_interval: Interval between data points in days
        
    Returns:
        Plotly figure object
    """
    # Generate dates throughout the year
    start_date = date(year, 1, 1)
    dates = []
    daylight_hours = []
    
    current_date = start_date
    while current_date.year == year:
        # Convert to datetime for Plotly compatibility
        dates.append(datetime.combine(current_date, datetime.min.time()))
        daylight_hours.append(daylight_duration(latitude, current_date))
        current_date += timedelta(days=day_interval)
    
    # Convert to pandas for easier plotting
    df = pd.DataFrame({
        'date': dates,
        'daylight_hours': daylight_hours
    })
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['daylight_hours'],
        mode='lines+markers',
        name=f'Latitude {latitude}°',
        line=dict(width=3, color='orange'),
        marker=dict(size=4),
        hovertemplate='Date: %{x}<br>Daylight: %{y:.1f} hours<extra></extra>'
    ))
    
    # Add reference line for 12 hours
    fig.add_hline(y=12, line_dash="dash", line_color="gray",
                  annotation_text="12 hours (equinox)")
    
    # Add seasonal markers
    solstice_summer = datetime(year, 6, 21)
    solstice_winter = datetime(year, 12, 21)
    equinox_spring = datetime(year, 3, 20)
    equinox_fall = datetime(year, 9, 22)
    
    for season_date, label, color in [
        (solstice_summer, "Summer Solstice", "red"),
        (solstice_winter, "Winter Solstice", "blue"),
        (equinox_spring, "Spring Equinox", "green"),
        (equinox_fall, "Fall Equinox", "orange")
    ]:
        fig.add_vline(x=season_date, line_dash="dot", line_color=color, opacity=0.7,
                      annotation_text=label)
    
    fig.update_layout(
        title=f"Daylight Duration Throughout {year} - Latitude {latitude}°",
        xaxis_title="Date",
        yaxis_title="Daylight Duration (hours)",
        yaxis=dict(range=[0, 24]),
        width=900,
        height=500,
        showlegend=False
    )
    
    return fig


def create_comparison_plot(latitudes: list[float],
                          input_date: Union[date, datetime]) -> go.Figure:
    """
    Create a comparison plot of daylight duration for multiple latitudes.
    
    Args:
        latitudes: List of latitudes to compare
        input_date: Date for calculation
        
    Returns:
        Plotly figure object
    """
    fig = go.Figure()
    
    colors = px.colors.qualitative.Set1
    
    for i, lat in enumerate(latitudes):
        # Generate data for the year
        year = input_date.year
        dates = []
        daylight_hours = []
        
        current_date = date(year, 1, 1)
        while current_date.year == year:
            # Convert to datetime for Plotly compatibility
            dates.append(datetime.combine(current_date, datetime.min.time()))
            daylight_hours.append(daylight_duration(lat, current_date))
            current_date += timedelta(days=7)
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=daylight_hours,
            mode='lines',
            name=f'{lat}°',
            line=dict(width=2, color=colors[i % len(colors)]),
            hovertemplate=f'Latitude {lat}°<br>Date: %{{x}}<br>Daylight: %{{y:.1f}} hours<extra></extra>'
        ))
    
    # Add current date marker - convert to datetime
    input_datetime = datetime.combine(input_date, datetime.min.time())
    fig.add_vline(x=input_datetime, line_dash="solid", line_color="black", line_width=2,
                  annotation_text=f"Selected: {input_date.strftime('%b %d')}")
    
    fig.update_layout(
        title=f"Daylight Duration Comparison - {input_date.year}",
        xaxis_title="Date",
        yaxis_title="Daylight Duration (hours)",
        yaxis=dict(range=[0, 24]),
        width=900,
        height=500,
        legend=dict(title="Latitude")
    )
    
    return fig