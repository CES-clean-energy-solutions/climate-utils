"""
Tests for wind module functionality.
"""

import pytest
import pandas as pd
import numpy as np
from climate_utils.wind import adjust_wind_speed, map_wind_direction_to_sector


class TestWind:
    """Test cases for wind functionality."""

    def test_adjust_wind_speed_scalar(self):
        """Test wind speed adjustment with scalar values."""
        # Test scalar input
        original_speed = 5.0
        adjusted = adjust_wind_speed(original_speed, 10, 80, 0.14)

        assert isinstance(adjusted, float)
        assert adjusted > original_speed  # Should be higher at 80m than 10m
        assert adjusted == pytest.approx(5.0 * (80/10) ** 0.14, rel=1e-6)

    def test_adjust_wind_speed_series(self):
        """Test wind speed adjustment with pandas Series."""
        # Test Series input
        original_speeds = pd.Series([2.0, 5.0, 8.0])
        adjusted = adjust_wind_speed(original_speeds, 10, 80, 0.14)

        assert isinstance(adjusted, pd.Series)
        assert len(adjusted) == 3
        assert all(adjusted > original_speeds)  # All should be higher at 80m

    def test_adjust_wind_speed_validation(self):
        """Test wind speed adjustment validation."""
        # Test missing parameters
        with pytest.raises(ValueError):
            adjust_wind_speed(5.0, 10, None, 0.14)

        with pytest.raises(ValueError):
            adjust_wind_speed(5.0, 10, 80, None)

    def test_map_wind_direction_16_sectors(self):
        """Test wind direction mapping to 16 sectors."""
        directions = pd.Series([0, 22.5, 45, 67.5, 90, 112.5, 135, 157.5,
                               180, 202.5, 225, 247.5, 270, 292.5, 315, 337.5])

        sectors = map_wind_direction_to_sector(directions, 16)

        expected_sectors = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                           'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']

        assert isinstance(sectors, pd.Series)
        assert len(sectors) == 16
        assert list(sectors) == expected_sectors

    def test_map_wind_direction_8_sectors(self):
        """Test wind direction mapping to 8 sectors."""
        directions = pd.Series([0, 45, 90, 135, 180, 225, 270, 315])

        sectors = map_wind_direction_to_sector(directions, 8)

        expected_sectors = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']

        assert isinstance(sectors, pd.Series)
        assert len(sectors) == 8
        assert list(sectors) == expected_sectors

    def test_map_wind_direction_4_sectors(self):
        """Test wind direction mapping to 4 sectors."""
        directions = pd.Series([0, 90, 180, 270])

        sectors = map_wind_direction_to_sector(directions, 4)

        expected_sectors = ['N', 'E', 'S', 'W']

        assert isinstance(sectors, pd.Series)
        assert len(sectors) == 4
        assert list(sectors) == expected_sectors

    def test_map_wind_direction_edge_cases(self):
        """Test wind direction mapping edge cases."""
        # Test 360 degrees (should map to North)
        directions = pd.Series([360])
        sectors = map_wind_direction_to_sector(directions, 16)
        assert sectors.iloc[0] == 'N'

        # Test negative values
        directions = pd.Series([-45])
        sectors = map_wind_direction_to_sector(directions, 8)
        assert sectors.iloc[0] == 'NW'

    def test_map_wind_direction_validation(self):
        """Test wind direction mapping validation."""
        # Test invalid number of sectors
        directions = pd.Series([0, 90, 180, 270])

        with pytest.raises(ValueError):
            map_wind_direction_to_sector(directions, 5)  # Invalid sector count

        # Test non-Series input
        with pytest.raises(TypeError):
            map_wind_direction_to_sector([0, 90, 180, 270], 8)