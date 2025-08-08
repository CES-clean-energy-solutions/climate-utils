"""
Test configuration and fixtures for climate-utils.

This module provides shared fixtures for testing with real EPW data.
"""

import pytest
import pandas as pd
from pathlib import Path
from climate_utils.epw import load_epw_to_df


@pytest.fixture
def sf_epw_file():
    """Path to the San Francisco EPW file."""
    return Path(__file__).parent / "USA_CA_San.Francisco.Intl.AP.724940_TMYx.epw"


@pytest.fixture
def sf_epw_data(sf_epw_file):
    """Load San Francisco EPW data as a processed DataFrame with location info."""
    from climate_utils.epw import load_epw_with_location

    df, lat, lon, tz = load_epw_with_location(sf_epw_file, year=2023)
    # Store location info as attributes for easy access
    df._epw_location_info = (lat, lon, tz)
    df._epw_file_path = sf_epw_file
    return df


@pytest.fixture
def sharm_epw_file():
    """Path to the Sharm El Sheikh EPW file."""
    return Path(__file__).parent / "EGY_JS_Sharm.Sheikh.Intl.AP.624639_TMYx.epw"


@pytest.fixture
def sharm_epw_data(sharm_epw_file):
    """Load Sharm El Sheikh EPW data as a processed DataFrame with location info."""
    from climate_utils.epw import load_epw_with_location

    df, lat, lon, tz = load_epw_with_location(sharm_epw_file, year=2023)
    # Store location info as attributes for easy access
    df._epw_location_info = (lat, lon, tz)
    df._epw_file_path = sharm_epw_file
    return df


@pytest.fixture
def sf_epw_raw(sf_epw_file):
    """Load San Francisco EPW data as a raw EPW object."""
    from climate_utils.epw import load_epw

    return load_epw(sf_epw_file)


@pytest.fixture
def sample_weather_data():
    """Sample weather data for testing without requiring EPW file."""
    return pd.DataFrame(
        {
            "Dry Bulb Temperature (°C)": [20, 25, 30, 35, 40],
            "Relative Humidity (%)": [50, 60, 70, 80, 90],
            "Wind Speed (m/s)": [2, 3, 4, 5, 6],
            "Wind Direction (°)": [180, 270, 90, 0, 135],
            "Direct Normal Radiation (Wh/m²)": [500, 600, 700, 800, 900],
            "Diffuse Horizontal Radiation (Wh/m²)": [100, 120, 140, 160, 180],
            "Global Horizontal Radiation (Wh/m²)": [600, 720, 840, 960, 1080],
            "Atmospheric Pressure (Pa)": [101325, 101325, 101325, 101325, 101325],
        }
    )
