"""
Wind utilities for climate data processing.

This module provides basic wind analysis functions for adjusting wind speeds
and mapping wind directions to compass sectors.
"""

import pandas as pd
import numpy as np
from typing import Union


def adjust_wind_speed(
    wind_speed: Union[float, pd.Series],
    ref_height: float = 10.0,
    new_height: float = 10.0,
    shear_coef: float = 0.15
) -> Union[float, pd.Series]:
    """
    Adjust wind speed to a specified height using the power law.

    Parameters:
    -----------
    wind_speed : float or pd.Series
        Wind speed at the reference height
    ref_height : float, default 10.0
        Reference height of the input wind speed in meters
    new_height : float, default 10.0
        Target height for wind speed adjustment in meters
    shear_coef : float, default 0.15
        Shear coefficient for wind speed adjustment

    Returns:
    --------
    float or pd.Series
        Wind speed adjusted to the target height
    """
    if new_height is None:
        raise ValueError("Target height must be provided for wind speed adjustment")

    if shear_coef is None:
        raise ValueError("Shear coefficient must be provided for wind speed adjustment")

    return wind_speed * ((new_height / ref_height) ** shear_coef)


def map_wind_direction_to_sector(series_wind_direction, num_sectors=16):
    """
    Maps wind direction in degrees (0-360) to compass sectors.

    Parameters:
    - series_wind_direction (pd.Series): Wind direction in degrees (0-360), int or float.
    - num_sectors (int, optional): Number of sectors (16, 8, or 4). Default is 16.

    Returns:
    - pd.Series: Assigned sector labels.
    """
    if not isinstance(series_wind_direction, pd.Series):
        raise TypeError("Input must be a pandas Series.")

    if num_sectors not in [4, 8, 16]:
        raise ValueError("num_sectors must be one of [4, 8, 16].")

    sector_labels = {
        16: ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
             "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"],
        8:  ["N", "NE", "E", "SE", "S", "SW", "W", "NW"],
        4:  ["N", "E", "S", "W"]
    }[num_sectors]

    sector_width = 360 / num_sectors
    sector_edges = np.linspace(-sector_width / 2, 360 - sector_width / 2, num_sectors + 1)
    sector_edges[-1] = 360  # Ensure wrap-around for 360 degrees

    return pd.cut(series_wind_direction % 360, bins=sector_edges, labels=sector_labels, right=False, include_lowest=True)

# Example usage:
# df["Wind Sector 16"] = map_wind_direction_to_sector(df["Average Direction"], 16)
# df["Wind Sector 8"] = map_wind_direction_to_sector(df["Average Direction"], 8)
# df["Wind Sector 4"] = map_wind_direction_to_sector(df["Average Direction"], 4)
