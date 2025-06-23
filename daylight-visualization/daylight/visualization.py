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
                                  resolution: float = 2.0,
                                  enable_animation: bool = False,
                                  animation_step: int = 7,
                                  use_world_map: bool = True) -> go.Figure:
    """
    Create a Plotly heatmap showing daylight duration on a Mercator projection.
    
    Args:
        input_date: Date for calculation
        resolution: Grid resolution in degrees
        enable_animation: Whether to create animation frames
        animation_step: Days between animation frames
        use_world_map: Whether to overlay on actual world map geography
        
    Returns:
        Plotly figure object
    """
    if not enable_animation:
        # Create single frame
        lat_grid, lon_grid, daylight_grid = create_daylight_grid(input_date, resolution, resolution)
        
        if use_world_map:
            # Create geographic scatter plot for world map overlay
            # Flatten the grids for plotting
            lats_flat = lat_grid.flatten()
            lons_flat = lon_grid.flatten()
            daylight_flat = daylight_grid.flatten()
            
            # Create smooth heatmap using Scattermapbox with large overlapping markers
            # This preserves accurate color mapping unlike Densitymapbox
            marker_size = max(20, min(50, 1000 / resolution))  # Very large for smooth coverage
            
            fig = go.Figure(data=go.Scattermapbox(
                lat=lats_flat,
                lon=lons_flat,
                mode='markers',
                marker=dict(
                    size=marker_size,
                    color=daylight_flat,
                    colorscale=[[0, 'rgb(0,0,139)'], [0.1, 'rgb(0,50,200)'], [0.3, 'rgb(0,150,255)'], [0.45, 'rgb(100,255,100)'], [0.5, 'rgb(255,255,0)'], [0.55, 'rgb(255,200,0)'], [0.7, 'rgb(255,100,0)'], [0.9, 'rgb(255,0,0)'], [1, 'rgb(200,0,0)']],
                    cmin=0,
                    cmax=24,
                    colorbar=dict(
                        title="Daylight Hours"
                    ),
                    opacity=0.15,
                    allowoverlap=True,  # Key for smooth blending
                ),
                hovertemplate='Latitude: %{lat:.1f}°<br>Longitude: %{lon:.1f}°<br>Daylight: %{marker.color:.1f} hours<extra></extra>',
                showlegend=False
            ))
            
            fig.update_layout(
                title=f"Daylight Duration - {input_date.strftime('%B %d, %Y')}",
                mapbox=dict(
                    style="open-street-map",
                    center=dict(lat=0, lon=0),
                    zoom=1
                ),
                autosize=True,
                margin=dict(l=0, r=0, t=40, b=0),
                height=600
            )
            
            # Configure interaction - disable dragging via config
            fig.update_layout(
                dragmode=False
            )
        else:
            # Create regular heatmap
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
    
    else:
        # Create animation frames
        year = input_date.year
        frames = []
        frame_dates = []
        
        # Generate frames for the whole year (starting from Jan 1 for consistency)
        for day_of_year in range(1, 366, animation_step):
            frame_date = date(year, 1, 1) + timedelta(days=day_of_year - 1)
            frame_dates.append(frame_date)
            
            lat_grid, lon_grid, daylight_grid = create_daylight_grid(frame_date, resolution, resolution)
            
            if use_world_map:
                # Create geographic frame
                lats_flat = lat_grid.flatten()
                lons_flat = lon_grid.flatten()
                daylight_flat = daylight_grid.flatten()
                
                frame = go.Frame(
                    data=[go.Densitymapbox(
                        lat=lats_flat,
                        lon=lons_flat,
                        z=daylight_flat,
                        colorscale=[[0, 'rgb(0,0,139)'], [0.1, 'rgb(0,50,200)'], [0.3, 'rgb(0,150,255)'], [0.45, 'rgb(100,255,100)'], [0.5, 'rgb(255,255,0)'], [0.55, 'rgb(255,200,0)'], [0.7, 'rgb(255,100,0)'], [0.9, 'rgb(255,0,0)'], [1, 'rgb(200,0,0)']],
                        zmin=0,
                        zmax=24,
                        colorbar=dict(
                            title="Daylight Hours"
                        ),
                        opacity=0.6,
                        radius=30,
                        hovertemplate='Latitude: %{lat:.1f}°<br>Longitude: %{lon:.1f}°<br>Daylight: %{z:.1f} hours<extra></extra>',
                        showlegend=False
                    )],
                    name=f"Day {day_of_year}",
                    layout=go.Layout(
                        title=f"Daylight Duration - {frame_date.strftime('%B %d, %Y')} (Day {day_of_year})"
                    )
                )
            else:
                # Create regular heatmap frame
                frame = go.Frame(
                    data=[go.Heatmap(
                        z=daylight_grid,
                        x=np.arange(-180, 180 + resolution, resolution),
                        y=np.arange(-90, 90 + resolution, resolution),
                        colorscale=[[0, 'rgb(0,0,139)'], [0.1, 'rgb(0,50,200)'], [0.3, 'rgb(0,150,255)'], [0.45, 'rgb(100,255,100)'], [0.5, 'rgb(255,255,0)'], [0.55, 'rgb(255,200,0)'], [0.7, 'rgb(255,100,0)'], [0.9, 'rgb(255,0,0)'], [1, 'rgb(200,0,0)']],
                        zmin=0,
                        zmax=24,
                        colorbar=dict(
                            title="Daylight Hours"
                        ),
                        hovertemplate='Latitude: %{y:.1f}°<br>Longitude: %{x:.1f}°<br>Daylight: %{z:.1f} hours<extra></extra>'
                    )],
                    name=f"Day {day_of_year}",
                    layout=go.Layout(
                        title=f"Daylight Duration - {frame_date.strftime('%B %d, %Y')} (Day {day_of_year})"
                    )
                )
            frames.append(frame)
        
        # Create initial frame
        lat_grid, lon_grid, daylight_grid = create_daylight_grid(input_date, resolution, resolution)
        
        if use_world_map:
            # Create initial geographic plot
            lats_flat = lat_grid.flatten()
            lons_flat = lon_grid.flatten()
            daylight_flat = daylight_grid.flatten()
            
            fig = go.Figure(
                data=go.Densitymapbox(
                    lat=lats_flat,
                    lon=lons_flat,
                    z=daylight_flat,
                    colorscale=[[0, 'rgb(0,0,139)'], [0.1, 'rgb(0,50,200)'], [0.3, 'rgb(0,150,255)'], [0.45, 'rgb(100,255,100)'], [0.5, 'rgb(255,255,0)'], [0.55, 'rgb(255,200,0)'], [0.7, 'rgb(255,100,0)'], [0.9, 'rgb(255,0,0)'], [1, 'rgb(200,0,0)']],
                    zmin=0,
                    zmax=24,
                    colorbar=dict(
                        title="Daylight Hours"
                    ),
                    opacity=0.6,
                    radius=30,
                    hovertemplate='Latitude: %{lat:.1f}°<br>Longitude: %{lon:.1f}°<br>Daylight: %{z:.1f} hours<extra></extra>',
                    showlegend=False
                ),
                frames=frames
            )
        else:
            # Create initial heatmap plot
            fig = go.Figure(
                data=go.Heatmap(
                    z=daylight_grid,
                    x=np.arange(-180, 180 + resolution, resolution),
                    y=np.arange(-90, 90 + resolution, resolution),
                    colorscale=[[0, 'rgb(0,0,139)'], [0.1, 'rgb(0,50,200)'], [0.3, 'rgb(0,150,255)'], [0.45, 'rgb(100,255,100)'], [0.5, 'rgb(255,255,0)'], [0.55, 'rgb(255,200,0)'], [0.7, 'rgb(255,100,0)'], [0.9, 'rgb(255,0,0)'], [1, 'rgb(200,0,0)']],
                    zmin=0,
                    zmax=24,
                    colorbar=dict(
                        title="Daylight Hours"
                    ),
                    hovertemplate='Latitude: %{y:.1f}°<br>Longitude: %{x:.1f}°<br>Daylight: %{z:.1f} hours<extra></extra>'
                ),
                frames=frames
            )
        
        # Add animation controls
        if use_world_map:
            fig.update_layout(
                title=f"Daylight Duration Animation - {year}",
                mapbox=dict(
                    style="open-street-map",
                    center=dict(lat=0, lon=0),
                    zoom=1
                ),
                autosize=True,
                margin=dict(l=0, r=0, t=40, b=0),
                height=600,
                updatemenus=[{
                "buttons": [
                    {
                        "args": [None, {"frame": {"duration": 200, "redraw": True},
                                      "fromcurrent": True, "transition": {"duration": 100}}],
                        "label": "▶️ Play",
                        "method": "animate"
                    },
                    {
                        "args": [[None], {"frame": {"duration": 0, "redraw": True},
                                        "mode": "immediate",
                                        "transition": {"duration": 0}}],
                        "label": "⏸️ Pause",
                        "method": "animate"
                    }
                ],
                "direction": "left",
                "pad": {"r": 10, "t": 87},
                "showactive": False,
                "type": "buttons",
                "x": 0.1,
                "xanchor": "right",
                "y": 0,
                "yanchor": "top"
            }],
            sliders=[{
                "active": 0,
                "yanchor": "top",
                "xanchor": "left",
                "currentvalue": {
                    "font": {"size": 20},
                    "prefix": "Day: ",
                    "visible": True,
                    "xanchor": "right"
                },
                "transition": {"duration": 100, "easing": "cubic-in-out"},
                "pad": {"b": 10, "t": 50},
                "len": 0.9,
                "x": 0.1,
                "y": 0,
                "steps": [
                    {
                        "args": [[f"Day {day_of_year}"], 
                               {"frame": {"duration": 100, "redraw": True},
                                "mode": "immediate",
                                "transition": {"duration": 100}}],
                        "label": f"Day {day_of_year}",
                        "method": "animate"
                    }
                    for day_of_year in range(1, 366, animation_step)
                ]
            }]
        )
        else:
            fig.update_layout(
                title=f"Daylight Duration Animation - {year}",
                xaxis_title="Longitude (°)",
                yaxis_title="Latitude (°)",
                width=1000,
                height=600,
                xaxis=dict(range=[-180, 180]),
                yaxis=dict(range=[-90, 90]),
                updatemenus=[{
                    "buttons": [
                        {
                            "args": [None, {"frame": {"duration": 200, "redraw": True},
                                          "fromcurrent": True, "transition": {"duration": 100}}],
                            "label": "▶️ Play",
                            "method": "animate"
                        },
                        {
                            "args": [[None], {"frame": {"duration": 0, "redraw": True},
                                            "mode": "immediate",
                                            "transition": {"duration": 0}}],
                            "label": "⏸️ Pause",
                            "method": "animate"
                        }
                    ],
                    "direction": "left",
                    "pad": {"r": 10, "t": 87},
                    "showactive": False,
                    "type": "buttons",
                    "x": 0.1,
                    "xanchor": "right",
                    "y": 0,
                    "yanchor": "top"
                }],
                sliders=[{
                    "active": 0,
                    "yanchor": "top",
                    "xanchor": "left",
                    "currentvalue": {
                        "font": {"size": 20},
                        "prefix": "Day: ",
                        "visible": True,
                        "xanchor": "right"
                    },
                    "transition": {"duration": 100, "easing": "cubic-in-out"},
                    "pad": {"b": 10, "t": 50},
                    "len": 0.9,
                    "x": 0.1,
                    "y": 0,
                    "steps": [
                        {
                            "args": [[f"Day {day_of_year}"], 
                                   {"frame": {"duration": 100, "redraw": True},
                                    "mode": "immediate",
                                    "transition": {"duration": 100}}],
                            "label": f"Day {day_of_year}",
                            "method": "animate"
                        }
                        for day_of_year in range(1, 366, animation_step)
                    ]
                }]
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
                             resolution: float = 1.0,
                             enable_animation: bool = False,
                             animation_step: int = 7) -> go.Figure:
    """
    Plot daylight duration vs latitude for a specific date.
    
    Args:
        input_date: Date for calculation
        lat_range: Tuple of (min_lat, max_lat)
        resolution: Latitude resolution in degrees
        enable_animation: Whether to create animation frames
        animation_step: Days between animation frames
        
    Returns:
        Plotly figure object
    """
    latitudes = np.arange(lat_range[0], lat_range[1] + resolution, resolution)
    
    if not enable_animation:
        # Create single frame
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
    
    else:
        # Create animation frames
        year = input_date.year
        frames = []
        
        # Generate frames for the whole year
        for day_of_year in range(1, 366, animation_step):
            frame_date = date(year, 1, 1) + timedelta(days=day_of_year - 1)
            daylight_hours = daylight_duration_array(latitudes, frame_date)
            
            frame = go.Frame(
                data=[go.Scatter(
                    x=latitudes,
                    y=daylight_hours,
                    mode='lines',
                    name='Daylight Duration',
                    line=dict(width=3, color='orange'),
                    hovertemplate='Latitude: %{x:.1f}°<br>Daylight: %{y:.1f} hours<extra></extra>'
                )],
                name=f"Day {day_of_year}",
                layout=go.Layout(
                    title=f"Daylight Duration by Latitude - {frame_date.strftime('%B %d, %Y')} (Day {day_of_year})"
                )
            )
            frames.append(frame)
        
        # Create initial frame
        daylight_hours = daylight_duration_array(latitudes, input_date)
        
        fig = go.Figure(
            data=go.Scatter(
                x=latitudes,
                y=daylight_hours,
                mode='lines',
                name='Daylight Duration',
                line=dict(width=3, color='orange'),
                hovertemplate='Latitude: %{x:.1f}°<br>Daylight: %{y:.1f} hours<extra></extra>'
            ),
            frames=frames
        )
        
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
        
        # Add animation controls
        fig.update_layout(
            title=f"Daylight Duration by Latitude - Animation {year}",
            xaxis_title="Latitude (°)",
            yaxis_title="Daylight Duration (hours)",
            xaxis=dict(range=lat_range, tickmode='linear', dtick=30),
            yaxis=dict(range=[0, 24]),
            width=800,
            height=500,
            showlegend=False,
            updatemenus=[{
                "buttons": [
                    {
                        "args": [None, {"frame": {"duration": 200, "redraw": True},
                                      "fromcurrent": True, "transition": {"duration": 100}}],
                        "label": "▶️ Play",
                        "method": "animate"
                    },
                    {
                        "args": [[None], {"frame": {"duration": 0, "redraw": True},
                                        "mode": "immediate",
                                        "transition": {"duration": 0}}],
                        "label": "⏸️ Pause",
                        "method": "animate"
                    }
                ],
                "direction": "left",
                "pad": {"r": 10, "t": 87},
                "showactive": False,
                "type": "buttons",
                "x": 0.1,
                "xanchor": "right",
                "y": 0,
                "yanchor": "top"
            }],
            sliders=[{
                "active": 0,
                "yanchor": "top",
                "xanchor": "left",
                "currentvalue": {
                    "font": {"size": 20},
                    "prefix": "Day: ",
                    "visible": True,
                    "xanchor": "right"
                },
                "transition": {"duration": 100, "easing": "cubic-in-out"},
                "pad": {"b": 10, "t": 50},
                "len": 0.9,
                "x": 0.1,
                "y": 0,
                "steps": [
                    {
                        "args": [[f"Day {day_of_year}"], 
                               {"frame": {"duration": 100, "redraw": True},
                                "mode": "immediate",
                                "transition": {"duration": 100}}],
                        "label": f"Day {day_of_year}",
                        "method": "animate"
                    }
                    for day_of_year in range(1, 366, animation_step)
                ]
            }]
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
    
    # Add seasonal markers - using shapes instead of add_vline to avoid type issues
    seasonal_dates = [
        (datetime(year, 6, 21), "Summer Solstice", "red"),
        (datetime(year, 12, 21), "Winter Solstice", "blue"),
        (datetime(year, 3, 20), "Spring Equinox", "green"),
        (datetime(year, 9, 22), "Fall Equinox", "orange")
    ]
    
    shapes = []
    annotations = []
    
    for season_date, label, color in seasonal_dates:
        # Add vertical line shape
        shapes.append({
            "type": "line",
            "x0": season_date,
            "x1": season_date,
            "y0": 0,
            "y1": 24,
            "line": {"color": color, "width": 2, "dash": "dot"},
            "opacity": 0.7
        })
        
        # Add annotation
        annotations.append({
            "x": season_date,
            "y": 22,
            "text": label,
            "showarrow": True,
            "arrowhead": 2,
            "arrowsize": 1,
            "arrowwidth": 2,
            "arrowcolor": color,
            "font": {"color": color, "size": 10},
            "textangle": -90
        })
    
    fig.update_layout(
        title=f"Daylight Duration Throughout {year} - Latitude {latitude}°",
        xaxis_title="Date",
        yaxis_title="Daylight Duration (hours)",
        yaxis=dict(range=[0, 24]),
        width=900,
        height=500,
        showlegend=False,
        shapes=shapes,
        annotations=annotations
    )
    
    return fig


def create_comparison_plot(latitudes: list[float],
                          input_date: Union[date, datetime],
                          enable_animation: bool = False,
                          animation_step: int = 7) -> go.Figure:
    """
    Create a comparison plot of daylight duration for multiple latitudes.
    
    Args:
        latitudes: List of latitudes to compare
        input_date: Date for calculation
        enable_animation: Whether to create animation frames
        animation_step: Days between animation frames
        
    Returns:
        Plotly figure object
    """
    colors = px.colors.qualitative.Set1
    year = input_date.year
    
    if not enable_animation:
        # Create static plot
        fig = go.Figure()
        
        for i, lat in enumerate(latitudes):
            # Generate data for the year
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
        
        # Add current date marker using shapes instead of add_vline
        input_datetime = datetime.combine(input_date, datetime.min.time())
        
        fig.update_layout(
            title=f"Daylight Duration Comparison - {input_date.year}",
            xaxis_title="Date",
            yaxis_title="Daylight Duration (hours)",
            yaxis=dict(range=[0, 24]),
            width=900,
            height=500,
            legend=dict(title="Latitude"),
            shapes=[{
                "type": "line",
                "x0": input_datetime,
                "x1": input_datetime,
                "y0": 0,
                "y1": 24,
                "line": {"color": "black", "width": 3, "dash": "solid"}
            }],
            annotations=[{
                "x": input_datetime,
                "y": 22,
                "text": f"Selected: {input_date.strftime('%b %d')}",
                "showarrow": True,
                "arrowhead": 2,
                "arrowsize": 1,
                "arrowwidth": 2,
                "arrowcolor": "black",
                "font": {"color": "black", "size": 12}
            }]
        )
        
        return fig
    
    else:
        # Create animated plot showing the current date marker moving through the year
        frames = []
        
        # Pre-calculate all latitude data for the year
        all_lat_data = {}
        for lat in latitudes:
            dates = []
            daylight_hours = []
            current_date = date(year, 1, 1)
            while current_date.year == year:
                dates.append(datetime.combine(current_date, datetime.min.time()))
                daylight_hours.append(daylight_duration(lat, current_date))
                current_date += timedelta(days=7)
            all_lat_data[lat] = (dates, daylight_hours)
        
        # Generate frames for animation
        for day_of_year in range(1, 366, animation_step):
            frame_date = date(year, 1, 1) + timedelta(days=day_of_year - 1)
            frame_datetime = datetime.combine(frame_date, datetime.min.time())
            
            # Create traces for this frame
            frame_data = []
            for i, lat in enumerate(latitudes):
                dates, daylight_hours = all_lat_data[lat]
                frame_data.append(go.Scatter(
                    x=dates,
                    y=daylight_hours,
                    mode='lines',
                    name=f'{lat}°',
                    line=dict(width=2, color=colors[i % len(colors)]),
                    hovertemplate=f'Latitude {lat}°<br>Date: %{{x}}<br>Daylight: %{{y:.1f}} hours<extra></extra>'
                ))
            
            # Add current date marker for this frame
            frame_data.append(go.Scatter(
                x=[frame_datetime, frame_datetime],
                y=[0, 24],
                mode='lines',
                line=dict(color='black', width=3, dash='solid'),
                name=f"Selected: {frame_date.strftime('%b %d')}",
                showlegend=False,
                hovertemplate=f'Selected Date: {frame_date.strftime("%B %d")}<extra></extra>'
            ))
            
            frame = go.Frame(
                data=frame_data,
                name=f"Day {day_of_year}",
                layout=go.Layout(
                    title=f"Daylight Duration Comparison - {frame_date.strftime('%B %d, %Y')} (Day {day_of_year})"
                )
            )
            frames.append(frame)
        
        # Create initial frame
        initial_data = []
        for i, lat in enumerate(latitudes):
            dates, daylight_hours = all_lat_data[lat]
            initial_data.append(go.Scatter(
                x=dates,
                y=daylight_hours,
                mode='lines',
                name=f'{lat}°',
                line=dict(width=2, color=colors[i % len(colors)]),
                hovertemplate=f'Latitude {lat}°<br>Date: %{{x}}<br>Daylight: %{{y:.1f}} hours<extra></extra>'
            ))
        
        # Add initial date marker
        input_datetime = datetime.combine(input_date, datetime.min.time())
        initial_data.append(go.Scatter(
            x=[input_datetime, input_datetime],
            y=[0, 24],
            mode='lines',
            line=dict(color='black', width=3, dash='solid'),
            name=f"Selected: {input_date.strftime('%b %d')}",
            showlegend=False,
            hovertemplate=f'Selected Date: {input_date.strftime("%B %d")}<extra></extra>'
        ))
        
        fig = go.Figure(data=initial_data, frames=frames)
        
        # Add animation controls
        fig.update_layout(
            title=f"Daylight Duration Comparison - Animation {year}",
            xaxis_title="Date",
            yaxis_title="Daylight Duration (hours)",
            yaxis=dict(range=[0, 24]),
            width=900,
            height=500,
            legend=dict(title="Latitude"),
            updatemenus=[{
                "buttons": [
                    {
                        "args": [None, {"frame": {"duration": 150, "redraw": True},
                                      "fromcurrent": True, "transition": {"duration": 100}}],
                        "label": "▶️ Play",
                        "method": "animate"
                    },
                    {
                        "args": [[None], {"frame": {"duration": 0, "redraw": True},
                                        "mode": "immediate",
                                        "transition": {"duration": 0}}],
                        "label": "⏸️ Pause",
                        "method": "animate"
                    }
                ],
                "direction": "left",
                "pad": {"r": 10, "t": 87},
                "showactive": False,
                "type": "buttons",
                "x": 0.1,
                "xanchor": "right",
                "y": 0,
                "yanchor": "top"
            }],
            sliders=[{
                "active": 0,
                "yanchor": "top",
                "xanchor": "left",
                "currentvalue": {
                    "font": {"size": 20},
                    "prefix": "Day: ",
                    "visible": True,
                    "xanchor": "right"
                },
                "transition": {"duration": 100, "easing": "cubic-in-out"},
                "pad": {"b": 10, "t": 50},
                "len": 0.9,
                "x": 0.1,
                "y": 0,
                "steps": [
                    {
                        "args": [[f"Day {day_of_year}"], 
                               {"frame": {"duration": 100, "redraw": True},
                                "mode": "immediate",
                                "transition": {"duration": 100}}],
                        "label": f"Day {day_of_year}",
                        "method": "animate"
                    }
                    for day_of_year in range(1, 366, animation_step)
                ]
            }]
        )
        
        return fig