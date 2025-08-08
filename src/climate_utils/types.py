"""
Type definitions for climate-utils package.

This module defines TypedDict structures for DataFrame columns and other data types
used throughout the package to ensure type safety and documentation.
"""

from typing import TypedDict, Union, Literal
import pandas as pd


# Type definitions for EPW DataFrame columns
EPWDataFrame = TypedDict(
    "EPWDataFrame",
    {
        # Basic weather parameters
        "Year": pd.Series[int],
        "Month": pd.Series[int],
        "Day": pd.Series[int],
        "Hour": pd.Series[int],
        "Minute": pd.Series[int],
        "Data Source and Uncertainty Flags": pd.Series[str],
        # Temperature and humidity
        "Dry Bulb Temperature (°C)": pd.Series[float],
        "Dew Point Temperature (°C)": pd.Series[float],
        "Relative Humidity (%)": pd.Series[float],
        "Atmospheric Station Pressure (Pa)": pd.Series[float],
        # Wind data
        "Wind Direction (°)": pd.Series[float],
        "Wind Speed (m/s)": pd.Series[float],
        # Solar radiation
        "Direct Normal Radiation (Wh/m²)": pd.Series[float],
        "Diffuse Horizontal Radiation (Wh/m²)": pd.Series[float],
        "Global Horizontal Radiation (Wh/m²)": pd.Series[float],
        # Additional parameters
        "Total Sky Cover (tenths)": pd.Series[float],
        "Opaque Sky Cover (tenths)": pd.Series[float],
        "Visibility (km)": pd.Series[float],
        "Ceiling Height (m)": pd.Series[float],
        "Present Weather Observation": pd.Series[int],
        "Present Weather Codes": pd.Series[int],
        "Precipitable Water (mm)": pd.Series[float],
        "Aerosol Optical Depth (thousandths)": pd.Series[float],
        "Snow Depth (cm)": pd.Series[float],
        "Days Since Last Snowfall": pd.Series[float],
        "Albedo (unitless)": pd.Series[float],
        "Liquid Precipitation Depth (mm)": pd.Series[float],
        "Liquid Precipitation Quantity (hr)": pd.Series[float],
        # Calculated psychrometric properties
        "Humidity Ratio (kg/kg)": pd.Series[float],
        "Enthalpy (kJ/kg)": pd.Series[float],
        "Wet Bulb Temperature (°C)": pd.Series[float],
        "Specific Volume (m³/kg)": pd.Series[float],
        # Wind direction sectors
        "Wind Direction Sector": pd.Series[int],
    },
)


# Required columns for different analysis types
REQUIRED_EPW_COLUMNS = {
    "basic": [
        "Dry Bulb Temperature (°C)",
        "Relative Humidity (%)",
        "Wind Speed (m/s)",
        "Wind Direction (°)",
    ],
    "solar": [
        "Direct Normal Radiation (Wh/m²)",
        "Diffuse Horizontal Radiation (Wh/m²)",
        "Global Horizontal Radiation (Wh/m²)",
    ],
    "psychrometric": [
        "Dry Bulb Temperature (°C)",
        "Relative Humidity (%)",
        "Atmospheric Station Pressure (Pa)",
    ],
    "wind_analysis": [
        "Wind Speed (m/s)",
        "Wind Direction (°)",
    ],
    "complete": [
        "Year",
        "Month",
        "Day",
        "Hour",
        "Dry Bulb Temperature (°C)",
        "Dew Point Temperature (°C)",
        "Relative Humidity (%)",
        "Atmospheric Station Pressure (Pa)",
        "Wind Direction (°)",
        "Wind Speed (m/s)",
        "Direct Normal Radiation (Wh/m²)",
        "Diffuse Horizontal Radiation (Wh/m²)",
        "Global Horizontal Radiation (Wh/m²)",
        "Total Sky Cover (tenths)",
        "Opaque Sky Cover (tenths)",
        "Visibility (km)",
        "Ceiling Height (m)",
        "Present Weather Observation",
        "Present Weather Codes",
        "Precipitable Water (mm)",
        "Aerosol Optical Depth (thousandths)",
        "Snow Depth (cm)",
        "Days Since Last Snowfall",
        "Albedo (unitless)",
        "Liquid Precipitation Depth (mm)",
        "Liquid Precipitation Quantity (hr)",
    ],
}


# Type aliases for common use cases
EPWDataFrameBasic = TypedDict(
    "EPWDataFrameBasic",
    {
        "Dry Bulb Temperature (°C)": pd.Series[float],
        "Relative Humidity (%)": pd.Series[float],
        "Wind Speed (m/s)": pd.Series[float],
        "Wind Direction (°)": pd.Series[float],
    },
)

EPWDataFrameSolar = TypedDict(
    "EPWDataFrameSolar",
    {
        "Direct Normal Radiation (Wh/m²)": pd.Series[float],
        "Diffuse Horizontal Radiation (Wh/m²)": pd.Series[float],
        "Global Horizontal Radiation (Wh/m²)": pd.Series[float],
    },
)

EPWDataFramePsychrometric = TypedDict(
    "EPWDataFramePsychrometric",
    {
        "Dry Bulb Temperature (°C)": pd.Series[float],
        "Relative Humidity (%)": pd.Series[float],
        "Atmospheric Station Pressure (Pa)": pd.Series[float],
    },
)


# Validation functions
def validate_epw_dataframe(
    df: pd.DataFrame, required_columns: list[str] = None
) -> None:
    """
    Validate that a DataFrame has the required EPW columns.

    Args:
        df: DataFrame to validate
        required_columns: List of required column names. If None, uses 'basic' columns.

    Raises:
        ValueError: If required columns are missing
        TypeError: If DataFrame is not a pandas DataFrame
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(df)}")

    if required_columns is None:
        required_columns = REQUIRED_EPW_COLUMNS["basic"]

    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}. "
            f"Available columns: {list(df.columns)}"
        )


def get_epw_column_info() -> dict[str, dict[str, str]]:
    """
    Get information about EPW DataFrame columns.

    Returns:
        Dictionary mapping column names to their descriptions and units.
    """
    return {
        "Dry Bulb Temperature (°C)": {
            "description": "Ambient air temperature",
            "unit": "°C",
            "type": "float",
            "required": True,
        },
        "Relative Humidity (%)": {
            "description": "Relative humidity as percentage",
            "unit": "%",
            "type": "float",
            "required": True,
        },
        "Wind Speed (m/s)": {
            "description": "Wind speed at measurement height",
            "unit": "m/s",
            "type": "float",
            "required": True,
        },
        "Wind Direction (°)": {
            "description": "Wind direction in degrees from north",
            "unit": "°",
            "type": "float",
            "required": True,
        },
        "Direct Normal Radiation (Wh/m²)": {
            "description": "Direct normal solar radiation",
            "unit": "Wh/m²",
            "type": "float",
            "required": False,
        },
        "Diffuse Horizontal Radiation (Wh/m²)": {
            "description": "Diffuse horizontal solar radiation",
            "unit": "Wh/m²",
            "type": "float",
            "required": False,
        },
        "Global Horizontal Radiation (Wh/m²)": {
            "description": "Global horizontal solar radiation",
            "unit": "Wh/m²",
            "type": "float",
            "required": False,
        },
        "Atmospheric Station Pressure (Pa)": {
            "description": "Atmospheric pressure at station",
            "unit": "Pa",
            "type": "float",
            "required": False,
        },
        "Humidity Ratio (kg/kg)": {
            "description": "Calculated humidity ratio",
            "unit": "kg/kg",
            "type": "float",
            "required": False,
        },
        "Enthalpy (kJ/kg)": {
            "description": "Calculated air enthalpy",
            "unit": "kJ/kg",
            "type": "float",
            "required": False,
        },
        "Wet Bulb Temperature (°C)": {
            "description": "Calculated wet bulb temperature",
            "unit": "°C",
            "type": "float",
            "required": False,
        },
        "Specific Volume (m³/kg)": {
            "description": "Calculated specific volume",
            "unit": "m³/kg",
            "type": "float",
            "required": False,
        },
        "Wind Direction Sector": {
            "description": "Wind direction mapped to compass sector",
            "unit": "sector number",
            "type": "int",
            "required": False,
        },
    }
