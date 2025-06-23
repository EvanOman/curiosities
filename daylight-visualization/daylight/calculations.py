"""Astronomical calculations for daylight duration."""

import numpy as np
from datetime import datetime, date
from typing import Union


def day_of_year(input_date: Union[date, datetime]) -> int:
    """Get the day of year (1-366) for a given date."""
    if isinstance(input_date, datetime):
        input_date = input_date.date()
    return input_date.timetuple().tm_yday


def solar_declination(day_of_year: int) -> float:
    """
    Calculate solar declination angle in degrees for a given day of year.
    
    Args:
        day_of_year: Day of year (1-366)
        
    Returns:
        Solar declination angle in degrees (-23.45 to +23.45)
    """
    # Solar declination using simplified formula
    # Maximum declination occurs around day 172 (summer solstice)
    declination = 23.45 * np.sin(np.radians(360 * (284 + day_of_year) / 365))
    return declination


def hour_angle(latitude: float, declination: float) -> float:
    """
    Calculate sunrise hour angle in degrees.
    
    Args:
        latitude: Latitude in degrees (-90 to +90)
        declination: Solar declination angle in degrees
        
    Returns:
        Hour angle in degrees (0-180), or NaN if sun doesn't rise/set
    """
    lat_rad = np.radians(latitude)
    decl_rad = np.radians(declination)
    
    # Calculate hour angle using sunrise equation
    cos_hour_angle = -np.tan(lat_rad) * np.tan(decl_rad)
    
    # Handle polar day/night conditions
    if cos_hour_angle < -1:
        # Polar day - sun never sets
        return 180.0
    elif cos_hour_angle > 1:
        # Polar night - sun never rises
        return 0.0
    else:
        # Normal sunrise/sunset
        return np.degrees(np.arccos(cos_hour_angle))


def daylight_duration(latitude: float, input_date: Union[date, datetime]) -> float:
    """
    Calculate daylight duration in hours for a given latitude and date.
    
    Args:
        latitude: Latitude in degrees (-90 to +90)
        input_date: Date for calculation
        
    Returns:
        Daylight duration in hours (0-24)
    """
    doy = day_of_year(input_date)
    declination = solar_declination(doy)
    h_angle = hour_angle(latitude, declination)
    
    # Daylight duration = 2 * hour_angle / 15 (convert degrees to hours)
    duration = 2 * h_angle / 15
    return duration


def daylight_duration_array(latitudes: np.ndarray, input_date: Union[date, datetime]) -> np.ndarray:
    """
    Calculate daylight duration for an array of latitudes.
    
    Args:
        latitudes: Array of latitudes in degrees
        input_date: Date for calculation
        
    Returns:
        Array of daylight durations in hours
    """
    doy = day_of_year(input_date)
    declination = solar_declination(doy)
    
    # Vectorized calculation
    lat_rad = np.radians(latitudes)
    decl_rad = np.radians(declination)
    
    cos_hour_angle = -np.tan(lat_rad) * np.tan(decl_rad)
    
    # Handle polar conditions and clip values to valid range for arccos
    cos_hour_angle_clipped = np.clip(cos_hour_angle, -1.0, 1.0)
    hour_angles = np.where(
        cos_hour_angle < -1, 180.0,  # Polar day
        np.where(
            cos_hour_angle > 1, 0.0,  # Polar night
            np.degrees(np.arccos(cos_hour_angle_clipped))  # Normal conditions
        )
    )
    
    durations = 2 * hour_angles / 15
    return durations


def create_daylight_grid(date_input: Union[date, datetime], 
                        lat_resolution: float = 1.0,
                        lon_resolution: float = 1.0) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Create a grid of daylight durations for mapping.
    
    Args:
        date_input: Date for calculation
        lat_resolution: Latitude grid resolution in degrees
        lon_resolution: Longitude grid resolution in degrees
        
    Returns:
        Tuple of (latitudes, longitudes, daylight_durations)
    """
    # Create latitude and longitude grids
    latitudes = np.arange(-90, 90 + lat_resolution, lat_resolution)
    longitudes = np.arange(-180, 180 + lon_resolution, lon_resolution)
    
    # Calculate daylight duration for each latitude
    daylight_hours = daylight_duration_array(latitudes, date_input)
    
    # Create meshgrid - daylight only depends on latitude, not longitude
    lat_grid, lon_grid = np.meshgrid(latitudes, longitudes, indexing='ij')
    daylight_grid = np.tile(daylight_hours[:, np.newaxis], (1, len(longitudes)))
    
    return lat_grid, lon_grid, daylight_grid