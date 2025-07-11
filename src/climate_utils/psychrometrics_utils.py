"""
Psychrometric utilities for climate analysis.

This module provides functions for calculating psychrometric properties
using the psychrolib library.
"""

import pandas as pd
import psychrolib

# Set unit system to SI
psychrolib.SetUnitSystem(psychrolib.SI)


def series_humidity_ratio(dry_bulb_temp: pd.Series, rel_humidity: pd.Series, pressure: pd.Series = None) -> pd.Series:
    """
    Calculate the humidity ratio (g/kg) given dry-bulb temperature (°C), relative humidity (%),
    and optional atmospheric pressure (Pa).

    Parameters:
    -----------
    dry_bulb_temp : pd.Series
        Dry bulb temperature in Celsius
    rel_humidity : pd.Series
        Relative humidity in percentage (0-100)
    pressure : pd.Series, optional
        Atmospheric pressure in Pascals. Defaults to 101325 Pa.

    Returns:
    --------
    pd.Series
        Humidity ratio in g/kg
    """
    if not isinstance(dry_bulb_temp, pd.Series) or not isinstance(rel_humidity, pd.Series):
        raise TypeError("dry_bulb_temp and rel_humidity must be Pandas Series.")

    # Convert RH from % to fraction
    rh_fraction = rel_humidity / 100.0

    # If pressure is None, use default atmospheric pressure
    if pressure is None:
        pressure = pd.Series(101325, index=dry_bulb_temp.index)  # Default pressure

    if isinstance(pressure, (int, float)):  # If pressure is a scalar, convert to a Series
        pressure = pd.Series(pressure, index=dry_bulb_temp.index)

    if not isinstance(pressure, pd.Series):
        raise TypeError("pressure must be a Pandas Series, int, float, or None.")

    # Apply psychrolib function row-wise
    humidity_ratio_kg_per_kg = dry_bulb_temp.index.to_series().apply(
        lambda idx: psychrolib.GetHumRatioFromRelHum(
            dry_bulb_temp.loc[idx], rh_fraction.loc[idx], pressure.loc[idx]
        )
    )

    # Convert kg/kg to g/kg
    humidity_ratio_g_per_kg = humidity_ratio_kg_per_kg * 1000

    return humidity_ratio_g_per_kg


def series_enthalpy_air(dry_bulb_temp: pd.Series, rel_humidity: pd.Series, pressure: pd.Series = None) -> pd.Series:
    """
    Calculate the enthalpy of moist air (J/kg) given dry-bulb temperature (°C), relative humidity (%),
    and optional atmospheric pressure (Pa).

    Parameters:
    -----------
    dry_bulb_temp : pd.Series
        Dry bulb temperature in Celsius
    rel_humidity : pd.Series
        Relative humidity in percentage (0-100)
    pressure : pd.Series, optional
        Atmospheric pressure in Pascals. Defaults to 101325 Pa.

    Returns:
    --------
    pd.Series
        Enthalpy of moist air in J/kg
    """
    if not isinstance(dry_bulb_temp, pd.Series) or not isinstance(rel_humidity, pd.Series):
        raise TypeError("dry_bulb_temp and rel_humidity must be Pandas Series.")

    # Convert RH from % to fraction
    rh_fraction = rel_humidity / 100.0

    # If pressure is None, use default atmospheric pressure
    if pressure is None:
        pressure = pd.Series(101325, index=dry_bulb_temp.index)  # Default pressure

    if isinstance(pressure, (int, float)):  # If pressure is a scalar, convert to a Series
        pressure = pd.Series(pressure, index=dry_bulb_temp.index)

    if not isinstance(pressure, pd.Series):
        raise TypeError("pressure must be a Pandas Series, int, float, or None.")

    # Apply psychrolib function row-wise
    enthalpy_j_per_kg = dry_bulb_temp.index.to_series().apply(
        lambda idx: psychrolib.GetMoistAirEnthalpy(
            dry_bulb_temp.loc[idx],
            psychrolib.GetHumRatioFromRelHum(dry_bulb_temp.loc[idx], rh_fraction.loc[idx], pressure.loc[idx])
        )
    )

    return enthalpy_j_per_kg