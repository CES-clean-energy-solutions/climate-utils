"""
Climate Utils - Shared utilities for climate data processing and weather file manipulation.

This package provides essential utilities for working with climate data, weather files,
and environmental analysis.
"""

__version__ = "0.1.0"

# Import all modules for direct access
from . import epw, wind, solar, state_point, wind_analysis, types, psychrometrics_utils

# Import commonly used functions for convenience
from .epw import (
    load_epw,
    load_epw_to_df,
    load_epw_with_location,
    epw_to_df,
    get_epw_location_info,
    get_epw_datetime_index,
    create_blank_epw,
    update_epw_column,
)
from .wind import adjust_wind_speed, map_wind_direction_to_sector
from .solar import get_surface_irradiation_orientations_epw
from .state_point import StatePoint, create_state_point_from_epw
from .wind_analysis import (
    adjust_wind_speed_height,
    calculate_wind_rose_data,
    calculate_wind_statistics,
    analyze_wind_resource,
)

__all__ = [
    # Modules
    "epw", "wind", "solar", "state_point", "wind_analysis", "types", "psychrometrics_utils",
    # Common functions
    "load_epw", "load_epw_to_df", "load_epw_with_location", "epw_to_df",
    "get_epw_location_info", "get_epw_datetime_index", "create_blank_epw", "update_epw_column",
    "adjust_wind_speed", "map_wind_direction_to_sector",
    "get_surface_irradiation_orientations_epw",
    "StatePoint", "create_state_point_from_epw",
    "adjust_wind_speed_height", "calculate_wind_rose_data", "calculate_wind_statistics", "analyze_wind_resource",
]
