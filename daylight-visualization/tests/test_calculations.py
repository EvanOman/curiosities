"""Unit tests for daylight calculations."""

import pytest
import numpy as np
from datetime import date
from daylight.calculations import (
    day_of_year,
    solar_declination,
    hour_angle,
    daylight_duration,
    daylight_duration_array,
    create_daylight_grid
)


class TestDayOfYear:
    def test_january_1st(self):
        assert day_of_year(date(2024, 1, 1)) == 1
    
    def test_december_31st_regular_year(self):
        assert day_of_year(date(2023, 12, 31)) == 365
    
    def test_december_31st_leap_year(self):
        assert day_of_year(date(2024, 12, 31)) == 366


class TestSolarDeclination:
    def test_summer_solstice_approx(self):
        # Around June 21 (day ~172), declination should be near maximum
        decl = solar_declination(172)
        assert 23.0 < decl < 23.5
    
    def test_winter_solstice_approx(self):
        # Around December 21 (day ~355), declination should be near minimum
        decl = solar_declination(355)
        assert -23.5 < decl < -23.0
    
    def test_equinoxes_approx(self):
        # Around March 21 (day ~80) and September 21 (day ~264)
        decl_spring = solar_declination(80)
        decl_fall = solar_declination(264)
        assert abs(decl_spring) < 2.0  # Should be close to 0
        assert abs(decl_fall) < 2.0    # Should be close to 0


class TestHourAngle:
    def test_equator_equinox(self):
        # At equator during equinox, hour angle should be 90 degrees
        h_angle = hour_angle(0.0, 0.0)
        assert abs(h_angle - 90.0) < 0.1
    
    def test_polar_day_condition(self):
        # Arctic summer - should return 180 (sun never sets)
        h_angle = hour_angle(80.0, 23.0)
        assert h_angle == 180.0
    
    def test_polar_night_condition(self):
        # Arctic winter - should return 0 (sun never rises)
        h_angle = hour_angle(80.0, -23.0)
        assert h_angle == 0.0


class TestDaylightDuration:
    def test_equator_equinox(self):
        # At equator during equinoxes, daylight should be ~12 hours
        duration = daylight_duration(0.0, date(2024, 3, 20))  # Around spring equinox
        assert abs(duration - 12.0) < 0.5
    
    def test_equator_year_round(self):
        # At equator, daylight should always be close to 12 hours
        dates = [date(2024, 1, 1), date(2024, 4, 1), date(2024, 7, 1), date(2024, 10, 1)]
        for test_date in dates:
            duration = daylight_duration(0.0, test_date)
            assert 11.5 < duration < 12.5
    
    def test_northern_summer_vs_winter(self):
        # Northern latitudes should have longer days in summer than winter
        lat = 45.0  # 45°N
        summer_duration = daylight_duration(lat, date(2024, 6, 21))  # Summer solstice
        winter_duration = daylight_duration(lat, date(2024, 12, 21))  # Winter solstice
        assert summer_duration > winter_duration
        assert summer_duration > 12.0
        assert winter_duration < 12.0
    
    def test_southern_hemisphere_opposite_seasons(self):
        # Southern hemisphere should have opposite seasonal pattern
        lat = -45.0  # 45°S
        june_duration = daylight_duration(lat, date(2024, 6, 21))    # Their winter
        december_duration = daylight_duration(lat, date(2024, 12, 21))  # Their summer
        assert december_duration > june_duration
        assert december_duration > 12.0
        assert june_duration < 12.0
    
    def test_known_values_oslo_summer(self):
        # Oslo, Norway (59.9°N) on summer solstice should have ~18.4 hours of daylight
        duration = daylight_duration(59.9, date(2024, 6, 21))
        assert 18.0 < duration < 19.0
    
    def test_known_values_oslo_winter(self):
        # Oslo, Norway (59.9°N) on winter solstice should have ~6 hours of daylight
        duration = daylight_duration(59.9, date(2024, 12, 21))
        assert 5.5 < duration < 6.5
    
    def test_arctic_polar_conditions(self):
        # Test polar day and night conditions
        arctic_lat = 75.0
        
        # Summer - should have 24 hours (polar day)
        summer_duration = daylight_duration(arctic_lat, date(2024, 6, 21))
        assert summer_duration == 24.0
        
        # Winter - should have 0 hours (polar night)
        winter_duration = daylight_duration(arctic_lat, date(2024, 12, 21))
        assert winter_duration == 0.0


class TestDaylightDurationArray:
    def test_array_calculation_consistency(self):
        # Array calculation should match individual calculations
        latitudes = np.array([0.0, 30.0, 60.0, -30.0, -60.0])
        test_date = date(2024, 6, 21)
        
        array_result = daylight_duration_array(latitudes, test_date)
        individual_results = [daylight_duration(lat, test_date) for lat in latitudes]
        
        np.testing.assert_array_almost_equal(array_result, individual_results, decimal=6)
    
    def test_symmetry_across_equator_equinox(self):
        # During equinox, northern and southern latitudes should have similar daylight
        latitudes = np.array([-45.0, -30.0, 0.0, 30.0, 45.0])
        durations = daylight_duration_array(latitudes, date(2024, 3, 20))
        
        # All should be close to 12 hours during equinox
        assert all(11.5 < d < 12.5 for d in durations)


class TestCreateDaylightGrid:
    def test_grid_dimensions(self):
        # Test that grid has correct dimensions
        lat_grid, lon_grid, daylight_grid = create_daylight_grid(
            date(2024, 6, 21), lat_resolution=5.0, lon_resolution=10.0
        )
        
        expected_lat_points = len(np.arange(-90, 95, 5))  # -90 to 90 with step 5
        expected_lon_points = len(np.arange(-180, 190, 10))  # -180 to 180 with step 10
        
        assert lat_grid.shape == (expected_lat_points, expected_lon_points)
        assert lon_grid.shape == (expected_lat_points, expected_lon_points)
        assert daylight_grid.shape == (expected_lat_points, expected_lon_points)
    
    def test_grid_daylight_varies_by_latitude_only(self):
        # Daylight should be the same across longitudes for same latitude
        lat_grid, lon_grid, daylight_grid = create_daylight_grid(
            date(2024, 6, 21), lat_resolution=10.0, lon_resolution=10.0
        )
        
        # Check that daylight is constant across longitude for each latitude row
        for i in range(daylight_grid.shape[0]):
            row_values = daylight_grid[i, :]
            assert np.all(np.isclose(row_values, row_values[0]))


if __name__ == "__main__":
    pytest.main([__file__])