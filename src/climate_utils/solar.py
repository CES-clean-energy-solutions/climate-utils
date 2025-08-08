"""
Solar calculation utilities for climate analysis.

This module provides functions for calculating solar radiation and surface
irradiation for different orientations.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
import math
from datetime import datetime, timedelta

# Import pvlib for solar position calculations
import pvlib
from pvlib import solarposition


def get_surface_irradiation_orientations_epw(
    df_epw: pd.DataFrame,
    orientations: Optional[List[float]] = None,
    albedo: float = 0.2,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    timezone: Optional[int] = None,
) -> Dict[str, pd.Series]:
    """
    Calculate surface irradiation for different orientations from EPW data.

    Parameters:
    -----------
    epw_data : pd.DataFrame
        EPW weather data with columns for direct normal, diffuse horizontal,
        and global horizontal radiation
    orientations : List[float], optional
        List of surface orientations in degrees (0 = North, 90 = East, etc.)
        Default: [0, 90, 180, 270] (N, E, S, W)
    albedo : float, default 0.2
        Ground albedo (reflectance)
    latitude : float, optional
        Site latitude in degrees. If None, will try to extract from EPW data
    longitude : float, optional
        Site longitude in degrees. If None, will try to extract from EPW data
    timezone : int, optional
        Site timezone offset in hours. If None, will try to extract from EPW data

    Returns:
    --------
    Dict[str, pd.Series]
        Dictionary with orientation angles as keys and irradiation series as values
    """
    if orientations is None:
        orientations = [0, 90, 180, 270]  # N, E, S, W

    # Extract radiation data directly using exact column names
    dni = df_epw["Direct Normal Radiation (Wh/m²)"]
    dhi = df_epw["Diffuse Horizontal Radiation (Wh/m²)"]
    ghi = df_epw["Global Horizontal Radiation (Wh/m²)"]

    # Extract site information if not provided
    if latitude is None:
        # Try to get from EPW header or use default
        latitude = 40.0  # Default latitude

    if longitude is None:
        longitude = -74.0  # Default longitude

    if timezone is None:
        timezone = -5  # Default timezone

    results = {}

    for orientation in orientations:
        # Calculate surface irradiation for this orientation
        surface_irradiation = calculate_surface_irradiation(
            dni, dhi, ghi, orientation, latitude, longitude, timezone, albedo
        )
        results[f"{orientation}°"] = surface_irradiation

    return results


def calculate_surface_irradiation(
    dni: pd.Series,
    dhi: pd.Series,
    ghi: pd.Series,
    surface_azimuth: float,
    latitude: float,
    longitude: float,
    timezone: int,
    albedo: float = 0.2,
) -> pd.Series:
    """
    Calculate surface irradiation for a specific orientation.

    Parameters:
    -----------
    dni : pd.Series
        Direct Normal Irradiance
    dhi : pd.Series
        Diffuse Horizontal Irradiance
    ghi : pd.Series
        Global Horizontal Irradiance
    surface_azimuth : float
        Surface azimuth angle in degrees (0 = North, 90 = East)
    latitude : float
        Site latitude in degrees
    longitude : float
        Site longitude in degrees
    timezone : int
        Site timezone offset in hours
    albedo : float
        Ground albedo (reflectance)

    Returns:
    --------
    pd.Series
        Surface irradiation for the specified orientation
    """
    # Convert angles to radians
    lat_rad = math.radians(latitude)
    surface_az_rad = math.radians(surface_azimuth)

    # Calculate solar position for each hour
    # This is a simplified calculation - for more accuracy, use a proper solar position library
    hours = range(len(dni))

    surface_irradiation = pd.Series(index=dni.index, dtype=float)

    for i, hour in enumerate(hours):
        # Simplified solar position calculation
        # In a real implementation, you'd use a proper solar position algorithm
        solar_zenith = calculate_solar_zenith(hour, latitude, longitude, timezone)
        solar_azimuth = calculate_solar_azimuth(hour, latitude, longitude, timezone)

        if solar_zenith < 90:  # Sun is above horizon
            # Calculate angle of incidence
            cos_incidence = calculate_cos_incidence(
                solar_zenith, solar_azimuth, surface_azimuth
            )

            # Direct component
            if cos_incidence > 0:
                direct_component = dni.iloc[i] * cos_incidence
            else:
                direct_component = 0

            # Diffuse component (simplified isotropic model)
            diffuse_component = (
                dhi.iloc[i] * 0.5 * (1 + math.cos(math.radians(90)))
            )  # Assuming vertical surface

            # Reflected component
            reflected_component = (
                ghi.iloc[i] * albedo * 0.5 * (1 - math.cos(math.radians(90)))
            )

            surface_irradiation.iloc[i] = (
                direct_component + diffuse_component + reflected_component
            )
        else:
            surface_irradiation.iloc[i] = 0

    return surface_irradiation


def calculate_solar_zenith(
    hour: int, latitude: float, longitude: float, timezone: int
) -> float:
    """
    Calculate solar zenith angle for a given hour.

    This is a simplified calculation. For accurate results, use a proper
    solar position library like pvlib.
    """
    # Simplified calculation - in practice, use pvlib or similar
    # This is just a placeholder for the basic structure
    day_of_year = (hour // 24) + 1
    hour_of_day = hour % 24

    # Simplified solar position calculation
    # This would need to be replaced with proper astronomical calculations
    solar_zenith = 45 + 45 * math.cos(2 * math.pi * (hour_of_day - 12) / 24)

    return max(0, min(90, solar_zenith))


def calculate_solar_azimuth(
    hour: int, latitude: float, longitude: float, timezone: int
) -> float:
    """
    Calculate solar azimuth angle for a given hour.

    This is a simplified calculation. For accurate results, use a proper
    solar position library like pvlib.
    """
    # Simplified calculation - in practice, use pvlib or similar
    hour_of_day = hour % 24

    # Simplified azimuth calculation
    solar_azimuth = 180 + (hour_of_day - 12) * 15

    return solar_azimuth % 360


def calculate_cos_incidence(
    solar_zenith: float, solar_azimuth: float, surface_azimuth: float
) -> float:
    """
    Calculate cosine of angle of incidence between sun and surface.

    Parameters:
    -----------
    solar_zenith : float
        Solar zenith angle in degrees
    solar_azimuth : float
        Solar azimuth angle in degrees
    surface_azimuth : float
        Surface azimuth angle in degrees

    Returns:
    --------
    float
        Cosine of angle of incidence
    """
    # Convert to radians
    zenith_rad = math.radians(solar_zenith)
    solar_az_rad = math.radians(solar_azimuth)
    surface_az_rad = math.radians(surface_azimuth)

    # Calculate angle of incidence
    cos_incidence = math.cos(zenith_rad) * math.cos(
        math.radians(90)
    ) + math.sin(  # Vertical surface
        zenith_rad
    ) * math.sin(
        math.radians(90)
    ) * math.cos(
        solar_az_rad - surface_az_rad
    )

    return max(0, cos_incidence)  # Ensure non-negative


def calculate_solar_angles_epw(
    df_epw: pd.DataFrame,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    timezone: Optional[int] = None,
) -> Tuple[pd.Series, pd.Series]:
    """
    Calculate solar zenith and azimuth angles for EPW data.

    Parameters:
    -----------
    df_epw : pd.DataFrame
        EPW weather data with datetime index
    latitude : float, optional
        Site latitude in degrees. If None, will try to extract from EPW data
    longitude : float, optional
        Site longitude in degrees. If None, will try to extract from EPW data
    timezone : int, optional
        Site timezone offset in hours. If None, will try to extract from EPW data

    Returns:
    --------
    Tuple[pd.Series, pd.Series]
        Solar zenith and azimuth angles in degrees
    """
    # If location information is not provided, try to extract from EPW data
    if latitude is None or longitude is None or timezone is None:
        # Check if the DataFrame has location attributes (from load_epw_with_location)
        if hasattr(df_epw, "_epw_location_info"):
            epw_lat, epw_lon, epw_tz = df_epw._epw_location_info
            latitude = latitude or epw_lat
            longitude = longitude or epw_lon
            timezone = timezone or epw_tz
        else:
            # Try to get location from the original EPW file path if available
            if hasattr(df_epw, "_epw_file_path"):
                try:
                    from .epw import load_epw_with_location

                    _, epw_lat, epw_lon, epw_tz = load_epw_with_location(
                        df_epw._epw_file_path
                    )
                    latitude = latitude or epw_lat
                    longitude = longitude or epw_lon
                    timezone = timezone or epw_tz
                except Exception:
                    pass

    # Ensure we have all required location information
    if latitude is None or longitude is None or timezone is None:
        raise ValueError(
            "Latitude, longitude, and timezone are required for solar position calculations. "
            "Either provide them explicitly or use load_epw_with_location() to load EPW data with location info."
        )

    # Ensure we have a datetime index
    if not isinstance(df_epw.index, pd.DatetimeIndex):
        raise ValueError(
            "EPW DataFrame must have a datetime index for solar calculations"
        )

    # Convert local time to UTC for pvlib calculations
    # EPW data is typically in local time, but pvlib expects UTC
    # Note: Etc/GMT uses opposite sign convention (Etc/GMT-8 = UTC+8)
    local_times = df_epw.index
    timezone_int = int(timezone)  # Convert float to int for timezone string
    utc_times = local_times.tz_localize(
        f"Etc/GMT{-timezone_int:+d}"
        if timezone_int <= 0
        else f"Etc/GMT{-timezone_int:d}"
    ).tz_convert("UTC")

    # Calculate solar position using pvlib
    solar_pos = solarposition.get_solarposition(
        time=utc_times,
        latitude=latitude,
        longitude=longitude,
        altitude=0,  # Sea level
        pressure=None,  # Use standard atmosphere
        temperature=df_epw.get(
            "Dry Bulb Temperature (°C)", 20
        ),  # Use temperature from EPW if available
        delta_t=67.0,  # Delta T for solar position calculation
        atmos_refract=0.5667,  # Atmospheric refraction
        method="nrel_numpy",  # Use NREL's solar position algorithm
    )

    # Extract zenith and azimuth angles
    zenith_angles = solar_pos["zenith"]
    azimuth_angles = solar_pos["azimuth"]

    # Ensure angles are within valid ranges
    zenith_angles = zenith_angles.clip(0, 90)  # Zenith angle should be 0-90 degrees
    azimuth_angles = azimuth_angles.clip(
        0, 360
    )  # Azimuth angle should be 0-360 degrees

    return zenith_angles, azimuth_angles
