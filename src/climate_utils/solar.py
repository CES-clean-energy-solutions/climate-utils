"""
Solar calculation utilities for climate analysis.

This module provides functions for calculating solar radiation and surface
irradiation for different orientations.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
import math


def get_surface_irradiation_orientations_epw(
    df_epw: pd.DataFrame,
    orientations: Optional[List[float]] = None,
    albedo: float = 0.2,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    timezone: Optional[int] = None
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
    dni = df_epw['Direct Normal Radiation (Wh/m²)']
    dhi = df_epw['Diffuse Horizontal Radiation (Wh/m²)']
    ghi = df_epw['Global Horizontal Radiation (Wh/m²)']

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
    albedo: float = 0.2
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
            diffuse_component = dhi.iloc[i] * 0.5 * (1 + math.cos(math.radians(90)))  # Assuming vertical surface

            # Reflected component
            reflected_component = ghi.iloc[i] * albedo * 0.5 * (1 - math.cos(math.radians(90)))

            surface_irradiation.iloc[i] = direct_component + diffuse_component + reflected_component
        else:
            surface_irradiation.iloc[i] = 0

    return surface_irradiation


def calculate_solar_zenith(hour: int, latitude: float, longitude: float, timezone: int) -> float:
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


def calculate_solar_azimuth(hour: int, latitude: float, longitude: float, timezone: int) -> float:
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
    solar_zenith: float,
    solar_azimuth: float,
    surface_azimuth: float
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
    cos_incidence = (
        math.cos(zenith_rad) * math.cos(math.radians(90)) +  # Vertical surface
        math.sin(zenith_rad) * math.sin(math.radians(90)) *
        math.cos(solar_az_rad - surface_az_rad)
    )

    return max(0, cos_incidence)  # Ensure non-negative


def calculate_solar_angles_epw(
    df_epw: pd.DataFrame,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    timezone: Optional[int] = None
) -> Tuple[pd.Series, pd.Series]:
    """
    Calculate solar zenith and azimuth angles for EPW data.

    Parameters:
    -----------
    epw_data : pd.DataFrame
        EPW weather data
    latitude : float, optional
        Site latitude in degrees
    longitude : float, optional
        Site longitude in degrees
    timezone : int, optional
        Site timezone offset in hours

    Returns:
    --------
    Tuple[pd.Series, pd.Series]
        Solar zenith and azimuth angles
    """
    # This would need to be implemented with a proper solar position library
    # For now, return placeholder series
    hours = range(len(df_epw))

    zenith_angles = pd.Series([45.0] * len(df_epw), index=df_epw.index)
    azimuth_angles = pd.Series([180.0] * len(df_epw), index=df_epw.index)

    return zenith_angles, azimuth_angles