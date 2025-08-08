"""
EPW (EnergyPlus Weather) file processing utilities.

This module provides functions for loading, parsing, and manipulating
EPW weather files for climate analysis.
"""

from pathlib import Path
import pandas as pd
from typing import Optional, Union, Tuple

# Required imports
from ladybug.epw import EPW

from .psychrometrics_utils import series_humidity_ratio, series_enthalpy_air

from . import wind


def load_epw(epw_file_path):
    """
    Load an EPW file using ladybug.

    Parameters:
    -----------
    epw_file_path : str or Path
        Path to the EPW file

    Returns:
    --------
    EPW object
        EPW object from ladybug
    """
    epw_file_path = Path(epw_file_path)

    if not epw_file_path.exists():
        raise FileNotFoundError(f"EPW file not found: {epw_file_path}")

    epw = EPW(epw_file_path)
    epw._import_data()
    return epw


def get_epw_location_info(epw: EPW) -> Tuple[float, float, int]:
    """
    Extract location information from an EPW file.

    Parameters:
    -----------
    epw : EPW
        EPW object from ladybug

    Returns:
    --------
    Tuple[float, float, int]
        (latitude, longitude, timezone_offset)
    """
    try:
        latitude = epw.location.latitude
        longitude = epw.location.longitude
        timezone_offset = epw.location.time_zone
        return latitude, longitude, timezone_offset
    except AttributeError:
        # Fallback: try to parse from header
        raise ValueError("Could not extract location information from EPW file")


def get_epw_datetime_index(epw: EPW, year: Optional[int] = None) -> pd.DatetimeIndex:
    """
    Create a proper datetime index from EPW data.

    Parameters:
    -----------
    epw : EPW
        EPW object from ladybug
    year : int, optional
        Year to use for the datetime index. If None, uses 2023 as default.
        TMY files use fictional years, so this allows specifying a realistic year.

    Returns:
    --------
    pd.DatetimeIndex
        Datetime index for the EPW data
    """
    # Use specified year or default to 2023 for TMY files
    if year is None:
        year = 2023

    # Create datetime index for the entire year (8760 hours)
    # EPW files typically have hourly data for the entire year
    start_date = pd.Timestamp(year=year, month=1, day=1, hour=0)
    end_date = pd.Timestamp(year=year, month=12, day=31, hour=23)

    return pd.date_range(start=start_date, end=end_date, freq="h")


def epw_to_df(epw, year: Optional[int] = None):
    """
    Load an EPW file and return a processed DataFrame with
    - Select columns from the EPW file
    - Augmented psychrometric properties (Humidity Ratio, Enthalpy)
    - Wind sectors (16 sectors)
    - Proper datetime index from EPW data

    Parameters:
    -----------
    epw : EPW
        EPW object from ladybug
    year : int, optional
        Year to use for the datetime index. If None, uses 2023 as default.
        TMY files use fictional years, so this allows specifying a realistic year.
    """
    # Extract relevant data columns
    data = {
        "Dry Bulb Temperature (°C)": epw.dry_bulb_temperature,
        "Dew Point Temperature (°C)": epw.dew_point_temperature,
        "Relative Humidity (%)": epw.relative_humidity,
        "Atmospheric Pressure (Pa)": epw.atmospheric_station_pressure,
        "Global Horizontal Radiation (Wh/m²)": epw.global_horizontal_radiation,
        "Direct Normal Radiation (Wh/m²)": epw.direct_normal_radiation,
        "Diffuse Horizontal Radiation (Wh/m²)": epw.diffuse_horizontal_radiation,
        "Wind Direction (°)": epw.wind_direction,
        "Wind Speed (m/s)": epw.wind_speed,
        "Sky Cover (Total) (tenths)": epw.total_sky_cover,
        "Sky Cover (Opaque) (tenths)": epw.opaque_sky_cover,
        "Precipitable Water (mm)": epw.precipitable_water,
        "Snow Depth (cm)": epw.snow_depth,
        "Visibility (km)": epw.visibility,
        "Ceiling Height (m)": epw.ceiling_height,
    }

    # Create a DataFrame
    df = pd.DataFrame(data)

    assert (
        df["Relative Humidity (%)"].between(0, 100).all()
    ), f"Invalid RH values found:\n{df[~df['Relative Humidity (%)'].between(0, 100)]}"

    # Compute psychrometric properties
    df["Humidity Ratio (g/kg)"] = series_humidity_ratio(
        df["Dry Bulb Temperature (°C)"],
        df["Relative Humidity (%)"],
        df["Atmospheric Pressure (Pa)"],
    )
    df["Enthalpy (J/kg)"] = series_enthalpy_air(
        df["Dry Bulb Temperature (°C)"],
        df["Relative Humidity (%)"],
        df["Atmospheric Pressure (Pa)"],
    )

    df["Sector"] = wind.map_wind_direction_to_sector(df["Wind Direction (°)"], 16)

    df["2 Sector"] = df["Wind Direction (°)"].apply(
        lambda x: "N" if (x > 270 or x < 90) else "S"
    )

    # Set datetime index from actual EPW data
    df.index = get_epw_datetime_index(epw, year=year)

    return df


def create_blank_epw() -> EPW:
    """
    Creates a blank EPW object with zeroed-out weather data and default flags.

    Returns:
        EPW: A blank EPW object ready for custom weather data insertion.
    """

    # EPW Metadata
    raw_epw_template = """\
LOCATION,Blank_Location,XX,XXX,Custom,000000,0.00000,0.00000,0.0,0.0
DESIGN CONDITIONS,0
TYPICAL/EXTREME PERIODS,0
GROUND TEMPERATURES,0
HOLIDAYS/DAYLIGHT SAVINGS,No,0,0,0
COMMENTS 1,"Blank EPW file generated for custom data input."
COMMENTS 2,"All data values set to zero."
DATA PERIODS,1,1,Data,Sunday,1/1,12/31
"""

    # Generate 8760 lines of blank hourly data
    for hour in range(1, 8761):  # EPW uses 1-based hour indexing
        raw_epw_template += (
            f"1999,1,1,{hour%24+1},0,"  # Year, Month, Day, Hour, Minute
            "0,"  # Data Source and Uncertainty Flags
            "0.0,0.0,0,"  # Dry Bulb Temp (°C), Dew Point Temp (°C), Rel. Humidity (%)
            "101325,"  # Atmospheric Pressure (Pa)
            "0,0,0,0,0,0,0,0,0,0,"  # Radiation & Illuminance values
            "0,0.0,0,0,0,77777,9,999999999,0,0.000,0,0,0.000,0.0,0.0\n"  # Wind, Precip, and Flags
        )

    # Convert the raw string into an EPW object
    epw = EPW.from_file_string(raw_epw_template)

    return epw


def update_epw_column(epw: EPW, column_name: str, data_series: pd.Series) -> EPW:
    """
    Updates a specific data column in an EPW object with values from a pandas Series.

    Args:
        epw (EPW): The EPW object to be updated.
        column_name (str): The exact EPW weather parameter name (e.g., "Dry Bulb Temperature").
        data_series (pd.Series): A pandas Series containing the new data values.

    Returns:
        EPW: The updated EPW object.
    """

    # Ensure the data_series has exactly 8760 values
    if len(data_series) != 8760:
        raise ValueError(
            "The data_series must contain exactly 8760 values, you provided {len(data_series)}."
        )

    # Get the list of valid column names from epw._data
    valid_columns = [str(dataset.header.data_type) for dataset in epw._data]

    # Validate that the requested column exists
    if column_name not in valid_columns:
        raise ValueError(
            f"'{column_name}' is not a valid EPW column. Choose from: {valid_columns}"
        )

    # Find the index of the requested column
    column_index = valid_columns.index(column_name)

    # Update the EPW column data
    epw._data[column_index].values = data_series.tolist()

    return epw


def load_epw_to_df(epw_file_path, year: Optional[int] = None):
    """
    Load an EPW file and return a processed DataFrame with
    - Select columns from the EPW file
    - Augmented psychrometric properties (Humidity Ratio, Enthalpy)
    - Wind sectors (16 sectors)
    - Proper datetime index from EPW data

    Parameters:
    -----------
    epw_file_path : str or Path
        Path to the EPW file
    year : int, optional
        Year to use for the datetime index. If None, uses 2023 as default.
        TMY files use fictional years, so this allows specifying a realistic year.
    """
    epw = load_epw(epw_file_path)
    df = epw_to_df(epw, year=year)
    return df


def load_epw_with_location(epw_file_path, year: Optional[int] = None):
    """
    Load an EPW file and return both the DataFrame and location information.

    Parameters:
    -----------
    epw_file_path : str or Path
        Path to the EPW file
    year : int, optional
        Year to use for the datetime index. If None, uses 2023 as default.
        TMY files use fictional years, so this allows specifying a realistic year.

    Returns:
    --------
    Tuple[pd.DataFrame, float, float, int]
        (DataFrame, latitude, longitude, timezone_offset)
    """
    epw = load_epw(epw_file_path)
    df = epw_to_df(epw, year=year)
    latitude, longitude, timezone_offset = get_epw_location_info(epw)
    return df, latitude, longitude, timezone_offset
