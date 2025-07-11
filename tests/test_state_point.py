"""
Tests for state_point module functionality.
"""

import pytest
import pandas as pd
import numpy as np
from climate_utils.state_point import StatePoint, create_state_point_from_epw


class TestStatePoint:
    """Test cases for StatePoint functionality."""

    def test_state_point_creation_with_rh(self):
        """Test StatePoint creation with relative humidity."""
        # Test with scalar values
        sp = StatePoint(dry_bulb_temp=25.0, relative_humidity=0.6)

        assert isinstance(sp, StatePoint)
        assert sp.dry_bulb_temp.iloc[0] == pytest.approx(25.0)
        assert sp.relative_humidity.iloc[0] == pytest.approx(0.6)
        assert sp.humidity_ratio.iloc[0] > 0
        assert sp.enthalpy.iloc[0] > 0

    def test_state_point_creation_with_series(self):
        """Test StatePoint creation with pandas Series."""
        temps = pd.Series([20, 25, 30])
        rh = pd.Series([0.5, 0.6, 0.7])

        sp = StatePoint(dry_bulb_temp=temps, relative_humidity=rh)

        assert isinstance(sp, StatePoint)
        assert len(sp.dry_bulb_temp) == 3
        assert len(sp.relative_humidity) == 3
        assert all(sp.humidity_ratio > 0)
        assert all(sp.enthalpy > 0)

    def test_state_point_properties(self):
        """Test StatePoint property calculations."""
        sp = StatePoint(dry_bulb_temp=25.0, relative_humidity=0.6)

        # Test all properties exist and are reasonable
        assert hasattr(sp, 'humidity_ratio')
        assert hasattr(sp, 'relative_humidity')
        assert hasattr(sp, 'wet_bulb_temp')
        assert hasattr(sp, 'dew_point_temp')
        assert hasattr(sp, 'enthalpy')
        assert hasattr(sp, 'specific_volume')

        # Test property types
        assert isinstance(sp.humidity_ratio, pd.Series)
        assert isinstance(sp.relative_humidity, pd.Series)
        assert isinstance(sp.wet_bulb_temp, pd.Series)
        assert isinstance(sp.dew_point_temp, pd.Series)
        assert isinstance(sp.enthalpy, pd.Series)
        assert isinstance(sp.specific_volume, pd.Series)

    def test_state_point_validation(self):
        """Test StatePoint input validation."""
        # Test multiple humidity inputs (should raise error)
        with pytest.raises(ValueError):
            StatePoint(
                dry_bulb_temp=25.0,
                relative_humidity=0.6,
                humidity_ratio=0.01
            )

    def test_state_point_to_dataframe(self):
        """Test StatePoint conversion to DataFrame."""
        sp = StatePoint(dry_bulb_temp=25.0, relative_humidity=0.6)
        df = sp.to_dataframe()

        assert isinstance(df, pd.DataFrame)
        assert 'dry_bulb_temp' in df.columns
        assert 'humidity_ratio' in df.columns
        assert 'relative_humidity' in df.columns
        assert 'wet_bulb_temp' in df.columns
        assert 'dew_point_temp' in df.columns
        assert 'enthalpy' in df.columns
        assert 'specific_volume' in df.columns
        assert 'pressure' in df.columns
        assert len(df) == 1

    def test_state_point_repr(self):
        """Test StatePoint string representation."""
        sp = StatePoint(dry_bulb_temp=25.0, relative_humidity=0.6)
        repr_str = repr(sp)

        assert isinstance(repr_str, str)
        assert 'StatePoint' in repr_str
        assert '25.0°C' in repr_str
        assert '60.0%' in repr_str  # 0.6 * 100 = 60%

    def test_create_state_point_from_epw(self):
        """Test creating StatePoint from EPW data."""
        # Create sample EPW data
        df_epw = pd.DataFrame({
            'Dry Bulb Temperature (°C)': [20, 25, 30],
            'Relative Humidity (%)': [50, 60, 70]  # In percentage
        })

        sp = create_state_point_from_epw(df_epw)

        assert isinstance(sp, StatePoint)
        assert len(sp.dry_bulb_temp) == 3
        assert all(sp.relative_humidity <= 1.0)  # Should be converted to fraction
        assert sp.relative_humidity.iloc[0] == pytest.approx(0.5)  # 50% = 0.5

    def test_create_state_point_from_epw_alt_names(self):
        """Test creating StatePoint from EPW data with alternative column names."""
        # Test with alternative column names
        df_epw = pd.DataFrame({
            'Dry Bulb Temperature (°C)': [20, 25, 30],
            'Relative Humidity (%)': [50, 60, 70]  # In percentage
        })

        sp = create_state_point_from_epw(df_epw)

        assert isinstance(sp, StatePoint)
        assert len(sp.dry_bulb_temp) == 3
        assert sp.relative_humidity.iloc[0] == pytest.approx(0.5)

    def test_create_state_point_from_epw_missing_columns(self):
        """Test creating StatePoint from EPW data with missing columns."""
        # Test with missing temperature column
        df_epw = pd.DataFrame({
            'Relative Humidity (%)': [50, 60, 70]
        })

        with pytest.raises(KeyError):
            create_state_point_from_epw(df_epw)

        # Test with missing humidity column
        df_epw = pd.DataFrame({
            'Dry Bulb Temperature (°C)': [20, 25, 30]
        })

        with pytest.raises(KeyError):
            create_state_point_from_epw(df_epw)

    def test_state_point_pressure_calculation(self):
        """Test StatePoint pressure calculation from altitude."""
        sp = StatePoint(
            dry_bulb_temp=25.0,
            relative_humidity=0.6,
            altitude=1000.0  # 1000m altitude
        )

        # Pressure should be lower at altitude
        assert sp.pressure.iloc[0] < 101325.0  # Sea level pressure
        assert sp.pressure.iloc[0] > 80000.0   # Reasonable lower bound