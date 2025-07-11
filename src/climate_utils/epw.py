"""
EPW (EnergyPlus Weather) file processing utilities.

This module provides functions for loading, parsing, and manipulating
EPW weather files for climate analysis.
"""

from pathlib import Path
import pandas as pd
from typing import Optional, Union

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


def epw_to_df(epw):
    """
    Load an EPW file and return a processed DataFrame with
    - Select columns from the EPW file
    - Augmented psychrometric properties (Humidity Ratio, Enthalpy)
    - Wind sectors (16 sectors)
    """
    # Extract relevant data columns
    data = {
        # "Year": [h[0] for h in epw.hourly_data],  # Extract year
        # "Month": [h[1] for h in epw.hourly_data],  # Extract month
        # "Day": [h[2] for h in epw.hourly_data],  # Extract day
        # "Hour": [h[3] for h in epw.hourly_data],  # Extract hour
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


    assert df['Relative Humidity (%)'].between(0, 100).all(), f"Invalid RH values found:\n{df[~df['Relative Humidity (%)'].between(0, 100)]}"

    # Compute psychrometric properties
    df['Humidity Ratio (g/kg)'] = series_humidity_ratio(
        df['Dry Bulb Temperature (°C)'], df['Relative Humidity (%)'], df['Atmospheric Pressure (Pa)']
    )
    df['Enthalpy (J/kg)'] = series_enthalpy_air(
        df['Dry Bulb Temperature (°C)'], df['Relative Humidity (%)'], df['Atmospheric Pressure (Pa)']
    )

    df['Sector'] = wind.map_wind_direction_to_sector(df['Wind Direction (°)'], 16)

    df['2 Sector'] = df['Wind Direction (°)'].apply(lambda x: 'N' if (x > 270 or x < 90) else 'S')

    # print(df['Sector'])
    # df['Wet Bulb Temperature (°C)'] = psychrometrics.series_wet_bulb_temperature(
    #     df['Dry Bulb Temperature (°C)'], df['Relative Humidity (%)'], df['Atmospheric Pressure (Pa)']
    # )

    # Set datetime index
    df.index = pd.date_range(start="2023-01-01 00:00", periods=8760, freq="h")

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
        raise ValueError("The data_series must contain exactly 8760 values, you provided {len(data_series)}.")

    # Get the list of valid column names from epw._data
    valid_columns = [str(dataset.header.data_type) for dataset in epw._data]

    # Validate that the requested column exists
    if column_name not in valid_columns:
        raise ValueError(f"'{column_name}' is not a valid EPW column. Choose from: {valid_columns}")

    # Find the index of the requested column
    column_index = valid_columns.index(column_name)

    # Update the EPW column data
    epw._data[column_index].values = data_series.tolist()

    return epw

def load_epw_to_df(epw_file_path):
    """
    Load an EPW file and return a processed DataFrame with
    - Select columns from the EPW file
    - Augmented psychrometric properties (Humidity Ratio, Enthalpy)
    - Wind sectors (16 sectors)
    """
    epw = load_epw(epw_file_path)
    df = epw_to_df(epw)
    return df