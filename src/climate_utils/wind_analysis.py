"""
Advanced wind analysis utilities for climate data processing.

This module provides comprehensive wind analysis functions including
wind speed adjustments, directional analysis, and sector mapping.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
import math


def adjust_wind_speed_height(
    wind_speed: Union[float, pd.Series],
    from_height: float,
    to_height: float,
    shear_coefficient: float = 0.14,
    surface_roughness: Optional[float] = None
) -> Union[float, pd.Series]:
    """
    Adjust wind speed from one height to another using wind profile power law.

    Parameters:
    -----------
    wind_speed : float or pd.Series
        Wind speed at the original height
    from_height : float
        Original measurement height in meters
    to_height : float
        Target height in meters
    shear_coefficient : float, default 0.14
        Wind shear coefficient (alpha). Common values:
        - 0.14: Open terrain
        - 0.20: Suburban areas
        - 0.25: Urban areas
        - 0.33: Dense urban areas
    surface_roughness : float, optional
        Surface roughness length in meters. If provided, overrides shear_coefficient.
        Common values:
        - 0.01: Open water
        - 0.05: Open terrain
        - 0.3: Suburban areas
        - 1.0: Urban areas

    Returns:
    --------
    float or pd.Series
        Wind speed adjusted to target height
    """
    if surface_roughness is not None:
        # Use logarithmic wind profile
        if from_height <= surface_roughness or to_height <= surface_roughness:
            raise ValueError("Height must be greater than surface roughness length")

        adjusted_speed = wind_speed * (np.log(to_height / surface_roughness) /
                                     np.log(from_height / surface_roughness))
    else:
        # Use power law wind profile
        adjusted_speed = wind_speed * (to_height / from_height) ** shear_coefficient

    return adjusted_speed


def map_wind_direction_to_sector(
    wind_direction: Union[float, pd.Series],
    num_sectors: int = 16,
    sector_names: Optional[List[str]] = None
) -> Union[str, pd.Series]:
    """
    Map wind direction to compass sectors.

    Parameters:
    -----------
    wind_direction : float or pd.Series
        Wind direction in degrees (0-360, where 0/360 is North)
    num_sectors : int, default 16
        Number of sectors to divide the compass into
    sector_names : List[str], optional
        Custom sector names. If None, uses standard compass directions

    Returns:
    --------
    str or pd.Series
        Sector name(s) for the wind direction(s)
    """
    if sector_names is None:
        if num_sectors == 16:
            sector_names = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                           'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
        elif num_sectors == 8:
            sector_names = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
        elif num_sectors == 4:
            sector_names = ['N', 'E', 'S', 'W']
        else:
            sector_names = [f'Sector_{i}' for i in range(num_sectors)]

    if len(sector_names) != num_sectors:
        raise ValueError(f"Number of sector names ({len(sector_names)}) must match num_sectors ({num_sectors})")

    # Normalize wind direction to 0-360
    normalized_direction = wind_direction % 360

    # Calculate sector index
    sector_size = 360 / num_sectors
    sector_index = (normalized_direction / sector_size).astype(int)

    # Handle edge case where direction is exactly 360 degrees
    sector_index = sector_index % num_sectors

    if isinstance(wind_direction, pd.Series):
        return pd.Series([sector_names[i] for i in sector_index], index=wind_direction.index)
    else:
        return sector_names[sector_index]


def calculate_wind_rose_data(
    wind_speed: pd.Series,
    wind_direction: pd.Series,
    speed_bins: Optional[List[float]] = None,
    direction_bins: int = 16
) -> pd.DataFrame:
    """
    Calculate wind rose data for visualization.

    Parameters:
    -----------
    wind_speed : pd.Series
        Wind speed data
    wind_direction : pd.Series
        Wind direction data in degrees
    speed_bins : List[float], optional
        Speed bin boundaries. If None, uses default bins
    direction_bins : int, default 16
        Number of direction sectors

    Returns:
    --------
    pd.DataFrame
        Wind rose data with columns: direction, speed_bin, frequency, count
    """
    if speed_bins is None:
        speed_bins = [0, 2, 4, 6, 8, 10, 12, 15, 20, 25, 30, 50]

    # Create direction sectors
    direction_sectors = map_wind_direction_to_sector(wind_direction, direction_bins)

    # Create speed bins
    speed_categories = pd.cut(wind_speed, bins=speed_bins, labels=False, include_lowest=True)

    # Create combined DataFrame
    wind_data = pd.DataFrame({
        'wind_speed': wind_speed,
        'wind_direction': wind_direction,
        'direction_sector': direction_sectors,
        'speed_bin': speed_categories
    })

    # Calculate frequencies
    wind_rose = wind_data.groupby(['direction_sector', 'speed_bin']).size().reset_index(name='count')
    wind_rose['frequency'] = wind_rose['count'] / len(wind_data) * 100

    # Add speed bin labels
    speed_labels = [f"{speed_bins[i]}-{speed_bins[i+1]}" for i in range(len(speed_bins)-1)]
    wind_rose['speed_label'] = wind_rose['speed_bin'].map(lambda x: speed_labels[x] if pd.notna(x) else 'Missing')

    return wind_rose


def calculate_wind_statistics(
    wind_speed: pd.Series,
    wind_direction: pd.Series,
    time_period: Optional[str] = None
) -> Dict[str, float]:
    """
    Calculate comprehensive wind statistics.

    Parameters:
    -----------
    wind_speed : pd.Series
        Wind speed data
    wind_direction : pd.Series
        Wind direction data in degrees
    time_period : str, optional
        Time period for grouping (e.g., 'D' for daily, 'M' for monthly)

    Returns:
    --------
    Dict[str, float]
        Dictionary containing wind statistics
    """
    if time_period is not None:
        # Group by time period
        wind_data = pd.DataFrame({
            'wind_speed': wind_speed,
            'wind_direction': wind_direction
        })

        # Add time index if not present
        if not isinstance(wind_data.index, pd.DatetimeIndex):
            wind_data.index = pd.date_range(start='2020-01-01', periods=len(wind_data), freq='H')

        # Group and calculate statistics
        grouped = wind_data.groupby(pd.Grouper(freq=time_period))

        stats = {}
        for name, group in grouped:
            if len(group) > 0:
                period_stats = _calculate_single_period_stats(group['wind_speed'], group['wind_direction'])
                for key, value in period_stats.items():
                    stats[f"{name}_{key}"] = value
    else:
        stats = _calculate_single_period_stats(wind_speed, wind_direction)

    return stats


def _calculate_single_period_stats(wind_speed: pd.Series, wind_direction: pd.Series) -> Dict[str, float]:
    """Calculate wind statistics for a single time period."""
    # Remove missing values
    valid_mask = wind_speed.notna() & wind_direction.notna()
    wind_speed_clean = wind_speed[valid_mask]
    wind_direction_clean = wind_direction[valid_mask]

    if len(wind_speed_clean) == 0:
        return {}

    stats = {
        'mean_speed': wind_speed_clean.mean(),
        'max_speed': wind_speed_clean.max(),
        'min_speed': wind_speed_clean.min(),
        'std_speed': wind_speed_clean.std(),
        'median_speed': wind_speed_clean.median(),
        'mean_direction': _calculate_mean_direction(wind_direction_clean),
        'std_direction': _calculate_direction_std(wind_direction_clean),
        'calm_percentage': (wind_speed_clean < 0.5).mean() * 100,
        'data_count': len(wind_speed_clean)
    }

    return stats


def _calculate_mean_direction(wind_direction: pd.Series) -> float:
    """Calculate mean wind direction using vector averaging."""
    # Convert to radians
    direction_rad = np.radians(wind_direction)

    # Calculate vector components
    u = np.mean(np.cos(direction_rad))
    v = np.mean(np.sin(direction_rad))

    # Calculate mean direction
    mean_direction = np.degrees(np.arctan2(v, u))

    # Ensure result is in 0-360 range
    if mean_direction < 0:
        mean_direction += 360

    return mean_direction


def _calculate_direction_std(wind_direction: pd.Series) -> float:
    """Calculate standard deviation of wind direction."""
    # Convert to radians
    direction_rad = np.radians(wind_direction)

    # Calculate vector components
    u = np.mean(np.cos(direction_rad))
    v = np.mean(np.sin(direction_rad))

    # Calculate resultant length
    r = np.sqrt(u**2 + v**2)

    # Calculate circular standard deviation
    if r > 0:
        std_direction = np.sqrt(-2 * np.log(r))
    else:
        std_direction = np.inf

    return np.degrees(std_direction)


def analyze_wind_resource(
    wind_speed: pd.Series,
    wind_direction: pd.Series,
    height: float = 10.0,
    target_height: float = 80.0,
    shear_coefficient: float = 0.14
) -> Dict[str, Union[float, pd.Series, pd.DataFrame]]:
    """
    Comprehensive wind resource analysis.

    Parameters:
    -----------
    wind_speed : pd.Series
        Wind speed data at measurement height
    wind_direction : pd.Series
        Wind direction data in degrees
    height : float, default 10.0
        Measurement height in meters
    target_height : float, default 80.0
        Target height for wind speed adjustment
    shear_coefficient : float, default 0.14
        Wind shear coefficient for height adjustment

    Returns:
    --------
    Dict[str, Union[float, pd.Series, pd.DataFrame]]
        Comprehensive wind resource analysis results
    """
    # Adjust wind speed to target height
    adjusted_wind_speed = adjust_wind_speed_height(
        wind_speed, height, target_height, shear_coefficient
    )

    # Calculate basic statistics
    basic_stats = calculate_wind_statistics(wind_speed, wind_direction)
    adjusted_stats = calculate_wind_statistics(adjusted_wind_speed, wind_direction)

    # Calculate wind rose data
    wind_rose_data = calculate_wind_rose_data(adjusted_wind_speed, wind_direction)

    # Calculate Weibull parameters
    weibull_params = _fit_weibull_distribution(adjusted_wind_speed)

    # Calculate power density
    power_density = _calculate_power_density(adjusted_wind_speed)

    results = {
        'basic_statistics': basic_stats,
        'adjusted_statistics': adjusted_stats,
        'wind_rose_data': wind_rose_data,
        'weibull_parameters': weibull_params,
        'power_density': power_density,
        'adjusted_wind_speed': adjusted_wind_speed,
        'measurement_height': height,
        'target_height': target_height,
        'shear_coefficient': shear_coefficient
    }

    return results


def _fit_weibull_distribution(wind_speed: pd.Series) -> Dict[str, float]:
    """Fit Weibull distribution to wind speed data."""
    # Remove zero and negative values
    wind_speed_clean = wind_speed[wind_speed > 0]

    if len(wind_speed_clean) == 0:
        return {'shape': np.nan, 'scale': np.nan, 'r_squared': np.nan}

    # Method of moments estimation
    mean_speed = wind_speed_clean.mean()
    std_speed = wind_speed_clean.std()

    # Estimate shape parameter (k)
    if std_speed > 0 and mean_speed > 0:
        cv = std_speed / mean_speed
        k = (cv ** (-1.086))
        c = mean_speed / math.gamma(1 + 1/k)
    else:
        k = np.nan
        c = np.nan

    # Calculate R-squared (simplified)
    if not np.isnan(k) and not np.isnan(c):
        # Generate theoretical Weibull distribution
        theoretical = np.random.weibull(k, len(wind_speed_clean)) * c
        r_squared = np.corrcoef(wind_speed_clean, theoretical)[0, 1] ** 2
    else:
        r_squared = np.nan

    return {
        'shape': k,
        'scale': c,
        'r_squared': r_squared
    }


def _calculate_power_density(wind_speed: pd.Series, air_density: float = 1.225) -> float:
    """Calculate wind power density."""
    # Power density = 0.5 * air_density * wind_speed^3
    power_density = 0.5 * air_density * (wind_speed ** 3).mean()
    return power_density