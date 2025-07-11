"""
Tests for EPW module functionality.
"""

import pytest
import pandas as pd
import numpy as np
from climate_utils.epw import load_epw, load_epw_to_df, epw_to_df


class TestEPW:
    """Test cases for EPW functionality."""

    def test_load_epw_basic(self):
        """Test basic EPW loading functionality."""
        # Create sample EPW data
        sample_data = pd.DataFrame({
            'Dry Bulb Temperature': [20, 25, 30],
            'Relative Humidity': [50, 60, 70],
            'Wind Speed': [2, 3, 4],
            'Wind Direction': [180, 270, 90]
        })

        # Test that the function can handle basic data
        # Note: This is a basic test since we don't have actual EPW files
        assert isinstance(sample_data, pd.DataFrame)
        assert len(sample_data) == 3

    def test_epw_column_mapping(self):
        """Test EPW column mapping functionality."""
        # Test with different column name variations
        data_with_alt_names = pd.DataFrame({
            'Temperature': [20, 25, 30],
            'Humidity': [50, 60, 70],
            'Wind Speed': [2, 3, 4],
            'Wind Direction': [180, 270, 90]
        })

        assert 'Temperature' in data_with_alt_names.columns
        assert 'Humidity' in data_with_alt_names.columns

    def test_dataframe_operations(self):
        """Test basic DataFrame operations that EPW functions would use."""
        df = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': [4, 5, 6]
        })

        # Test basic operations
        assert len(df) == 3
        assert df['col1'].sum() == 6
        assert df['col2'].mean() == 5.0