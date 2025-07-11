"""
Psychrometric state point calculations for climate analysis.

This module provides a StatePoint class for calculating and manipulating
psychrometric properties of air.
"""

import pandas as pd
import numpy as np
from typing import Optional, Union, Dict, Any
import math


class StatePoint:
    """
    A class representing a psychrometric state point with various air properties.

    This class provides methods to calculate and manipulate psychrometric
    properties of air such as temperature, humidity, enthalpy, etc.
    """

    def __init__(
        self,
        dry_bulb_temp: Union[float, pd.Series],
        humidity_ratio: Optional[Union[float, pd.Series]] = None,
        relative_humidity: Optional[Union[float, pd.Series]] = None,
        wet_bulb_temp: Optional[Union[float, pd.Series]] = None,
        dew_point_temp: Optional[Union[float, pd.Series]] = None,
        pressure: Union[float, pd.Series] = 101325.0,
        altitude: Optional[Union[float, pd.Series]] = None
    ):
        """
        Initialize a StatePoint with air properties.

        Parameters:
        -----------
        dry_bulb_temp : float or pd.Series
            Dry bulb temperature in Celsius
        humidity_ratio : float or pd.Series, optional
            Humidity ratio in kg/kg
        relative_humidity : float or pd.Series, optional
            Relative humidity as a fraction (0-1)
        wet_bulb_temp : float or pd.Series, optional
            Wet bulb temperature in Celsius
        dew_point_temp : float or pd.Series, optional
            Dew point temperature in Celsius
        pressure : float or pd.Series, default 101325.0
            Atmospheric pressure in Pa
        altitude : float or pd.Series, optional
            Altitude in meters (used to calculate pressure if not provided)
        """
        # First, determine the length from dry_bulb_temp
        if isinstance(dry_bulb_temp, pd.Series):
            length = len(dry_bulb_temp)
        else:
            length = 1

        self.dry_bulb_temp = self._ensure_series(dry_bulb_temp, length)
        self.pressure = self._ensure_series(pressure, length)

        # Calculate pressure from altitude if provided
        if altitude is not None:
            altitude_series = self._ensure_series(altitude, length)
            self.pressure = self._calculate_pressure_from_altitude(altitude_series)

        # Initialize other properties
        self._humidity_ratio = None
        self._relative_humidity = None
        self._wet_bulb_temp = None
        self._dew_point_temp = None
        self._enthalpy = None
        self._specific_volume = None

        # Set the provided properties and calculate others
        self._set_properties(
            humidity_ratio=humidity_ratio,
            relative_humidity=relative_humidity,
            wet_bulb_temp=wet_bulb_temp,
            dew_point_temp=dew_point_temp,
            length=length
        )

    def _ensure_series(self, value: Union[float, pd.Series], length: int = 1) -> pd.Series:
        """Convert scalar to series if needed."""
        if isinstance(value, pd.Series):
            return value
        else:
            # Use the same index as dry_bulb_temp if available
            if hasattr(self, 'dry_bulb_temp') and isinstance(self.dry_bulb_temp, pd.Series):
                return pd.Series([value] * len(self.dry_bulb_temp), index=self.dry_bulb_temp.index)
            else:
                return pd.Series([value] * length)

    def _calculate_pressure_from_altitude(self, altitude: pd.Series) -> pd.Series:
        """Calculate atmospheric pressure from altitude using standard atmosphere."""
        # Standard atmosphere model
        return 101325.0 * np.exp(-altitude / 7400.0)

    def _set_properties(
        self,
        humidity_ratio: Optional[Union[float, pd.Series]] = None,
        relative_humidity: Optional[Union[float, pd.Series]] = None,
        wet_bulb_temp: Optional[Union[float, pd.Series]] = None,
        dew_point_temp: Optional[Union[float, pd.Series]] = None,
        length: int = 1
    ):
        """Set properties and calculate dependent ones."""
        # Count how many properties are provided
        provided = sum([
            humidity_ratio is not None,
            relative_humidity is not None,
            wet_bulb_temp is not None,
            dew_point_temp is not None
        ])

        if provided > 1:
            raise ValueError("Only one of humidity_ratio, relative_humidity, wet_bulb_temp, or dew_point_temp should be provided")

        if provided == 0:
            # Default to dry air
            self._humidity_ratio = pd.Series(0.0, index=self.dry_bulb_temp.index)
            self._calculate_all_properties()
        else:
            if humidity_ratio is not None:
                self._humidity_ratio = self._ensure_series(humidity_ratio, length)
            elif relative_humidity is not None:
                rh = self._ensure_series(relative_humidity, length)
                self._humidity_ratio = self._calculate_humidity_ratio_from_rh(rh)
            elif wet_bulb_temp is not None:
                wbt = self._ensure_series(wet_bulb_temp, length)
                self._humidity_ratio = self._calculate_humidity_ratio_from_wet_bulb(wbt)
            elif dew_point_temp is not None:
                dpt = self._ensure_series(dew_point_temp, length)
                self._humidity_ratio = self._calculate_humidity_ratio_from_dew_point(dpt)

            self._calculate_all_properties()

    def _calculate_humidity_ratio_from_rh(self, relative_humidity: pd.Series) -> pd.Series:
        """Calculate humidity ratio from relative humidity."""
        # Saturation vapor pressure at dry bulb temperature
        pws = self._calculate_saturation_vapor_pressure(self.dry_bulb_temp)

        # Actual vapor pressure
        pw = relative_humidity * pws

        # Humidity ratio
        return 0.62198 * pw / (self.pressure - pw)

    def _calculate_humidity_ratio_from_wet_bulb(self, wet_bulb_temp: pd.Series) -> pd.Series:
        """Calculate humidity ratio from wet bulb temperature."""
        # Saturation vapor pressure at wet bulb temperature
        pws_wb = self._calculate_saturation_vapor_pressure(wet_bulb_temp)

        # Saturation humidity ratio at wet bulb temperature
        ws_wb = 0.62198 * pws_wb / (self.pressure - pws_wb)

        # Enthalpy at wet bulb temperature
        h_wb = 1.006 * wet_bulb_temp + ws_wb * (2501 + 1.86 * wet_bulb_temp)

        # Enthalpy at dry bulb temperature
        h_db = 1.006 * self.dry_bulb_temp

        # Humidity ratio
        return (h_wb - h_db) / (2501 + 1.86 * self.dry_bulb_temp)

    def _calculate_humidity_ratio_from_dew_point(self, dew_point_temp: pd.Series) -> pd.Series:
        """Calculate humidity ratio from dew point temperature."""
        # Saturation vapor pressure at dew point temperature
        pws_dp = self._calculate_saturation_vapor_pressure(dew_point_temp)

        # Humidity ratio
        return 0.62198 * pws_dp / (self.pressure - pws_dp)

    def _calculate_saturation_vapor_pressure(self, temperature: pd.Series) -> pd.Series:
        """Calculate saturation vapor pressure using Magnus formula."""
        # Magnus formula for saturation vapor pressure (Pa)
        return 610.78 * np.exp(17.2694 * temperature / (temperature + 238.3))

    def _calculate_all_properties(self):
        """Calculate all psychrometric properties."""
        # Relative humidity
        pws = self._calculate_saturation_vapor_pressure(self.dry_bulb_temp)
        pw = self._humidity_ratio * self.pressure / (0.62198 + self._humidity_ratio)
        self._relative_humidity = pw / pws

        # Dew point temperature (iterative calculation simplified)
        self._dew_point_temp = self._calculate_dew_point_temperature()

        # Wet bulb temperature (iterative calculation simplified)
        self._wet_bulb_temp = self._calculate_wet_bulb_temperature()

        # Enthalpy
        self._enthalpy = 1.006 * self.dry_bulb_temp + self._humidity_ratio * (2501 + 1.86 * self.dry_bulb_temp)

        # Specific volume
        self._specific_volume = (287.055 * (self.dry_bulb_temp + 273.15) * (1 + 1.6078 * self._humidity_ratio)) / self.pressure

    def _calculate_dew_point_temperature(self) -> pd.Series:
        """Calculate dew point temperature."""
        # Simplified calculation - in practice, use iterative method
        pw = self._humidity_ratio * self.pressure / (0.62198 + self._humidity_ratio)

        # Inverse of Magnus formula
        dew_point = 238.3 * np.log(pw / 610.78) / (17.2694 - np.log(pw / 610.78))

        return dew_point

    def _calculate_wet_bulb_temperature(self) -> pd.Series:
        """Calculate wet bulb temperature."""
        # Simplified calculation - in practice, use iterative method
        # This is an approximation
        return self.dry_bulb_temp - (1 - self._relative_humidity) * 5

    @property
    def humidity_ratio(self) -> pd.Series:
        """Get humidity ratio in kg/kg."""
        return self._humidity_ratio

    @property
    def relative_humidity(self) -> pd.Series:
        """Get relative humidity as a fraction (0-1)."""
        return self._relative_humidity

    @property
    def wet_bulb_temp(self) -> pd.Series:
        """Get wet bulb temperature in Celsius."""
        return self._wet_bulb_temp

    @property
    def dew_point_temp(self) -> pd.Series:
        """Get dew point temperature in Celsius."""
        return self._dew_point_temp

    @property
    def enthalpy(self) -> pd.Series:
        """Get enthalpy in kJ/kg."""
        return self._enthalpy

    @property
    def specific_volume(self) -> pd.Series:
        """Get specific volume in m³/kg."""
        return self._specific_volume

    def to_dataframe(self) -> pd.DataFrame:
        """Convert state point to DataFrame."""
        return pd.DataFrame({
            'dry_bulb_temp': self.dry_bulb_temp,
            'humidity_ratio': self._humidity_ratio,
            'relative_humidity': self._relative_humidity,
            'wet_bulb_temp': self._wet_bulb_temp,
            'dew_point_temp': self._dew_point_temp,
            'enthalpy': self._enthalpy,
            'specific_volume': self._specific_volume,
            'pressure': self.pressure
        })

    def __repr__(self) -> str:
        """String representation of the StatePoint."""
        if len(self.dry_bulb_temp) == 1:
            return f"StatePoint(T={self.dry_bulb_temp.iloc[0]:.1f}°C, RH={self._relative_humidity.iloc[0]*100:.1f}%)"
        else:
            return f"StatePoint({len(self.dry_bulb_temp)} points, T={self.dry_bulb_temp.mean():.1f}°C avg)"


def create_state_point_from_epw(df_epw: pd.DataFrame) -> StatePoint:
    """
    Create a StatePoint from EPW weather data.

    Parameters:
    -----------
    df_epw : pd.DataFrame
        EPW weather data with temperature and humidity columns

    Returns:
    --------
    StatePoint
        StatePoint object with psychrometric properties
    """
    # Extract data directly using exact column names
    dry_bulb_temp = df_epw['Dry Bulb Temperature (°C)']
    relative_humidity = df_epw['Relative Humidity (%)']

    # Convert relative humidity to fraction if in percentage
    if relative_humidity.max() > 1:
        relative_humidity = relative_humidity / 100

    return StatePoint(
        dry_bulb_temp=dry_bulb_temp,
        relative_humidity=relative_humidity
    )