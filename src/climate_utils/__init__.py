"""
Climate Utils - Shared utilities for climate data processing and weather file manipulation.

This package provides essential utilities for working with climate data, weather files,
and environmental analysis.
"""

__version__ = "0.1.0"

# Import main modules for easy access
from . import epw
from . import wind
from . import solar
from . import state_point
from . import wind_analysis

# Import commonly used functions
from .epw import load_epw, load_epw_to_df, epw_to_df
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
    "epw",
    "wind",
    "solar",
    "state_point",
    "wind_analysis",
    # Common functions
    "load_epw",
    "load_epw_to_df",
    "epw_to_df",
    "adjust_wind_speed",
    "map_wind_direction_to_sector",
    "get_surface_irradiation_orientations_epw",
    "StatePoint",
    "create_state_point_from_epw",
    "adjust_wind_speed_height",
    "calculate_wind_rose_data",
    "calculate_wind_statistics",
    "analyze_wind_resource",
]
