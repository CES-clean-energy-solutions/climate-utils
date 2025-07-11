"""
Integration tests for climate-utils using real EPW data.

These tests verify that all modules work together correctly with actual weather data.
"""

import pytest
import pandas as pd
import numpy as np
from climate_utils import (
    epw, wind, wind_analysis, solar, state_point,
    load_epw_to_df, adjust_wind_speed, map_wind_direction_to_sector,
    get_surface_irradiation_orientations_epw, StatePoint, create_state_point_from_epw
)


class TestIntegration:
    """Integration tests using real EPW data."""

    def test_epw_loading_and_processing(self, sf_epw_data):
        """Test that EPW file loads and processes correctly."""
        # Check basic structure
        assert isinstance(sf_epw_data, pd.DataFrame)
        assert len(sf_epw_data) == 8760  # Standard EPW has 8760 hours

        # Check required columns exist
        required_cols = [
            'Dry Bulb Temperature (°C)',
            'Relative Humidity (%)',
            'Wind Speed (m/s)',
            'Wind Direction (°)',
            'Humidity Ratio (g/kg)',
            'Enthalpy (J/kg)',
            'Sector'
        ]

        for col in required_cols:
            assert col in sf_epw_data.columns, f"Missing column: {col}"

        # Check data ranges are reasonable
        assert sf_epw_data['Dry Bulb Temperature (°C)'].min() > -50
        assert sf_epw_data['Dry Bulb Temperature (°C)'].max() < 60
        assert sf_epw_data['Relative Humidity (%)'].min() >= 0
        assert sf_epw_data['Relative Humidity (%)'].max() <= 100
        assert sf_epw_data['Wind Speed (m/s)'].min() >= 0

        # Check psychrometric calculations
        assert sf_epw_data['Humidity Ratio (g/kg)'].min() >= 0
        assert sf_epw_data['Enthalpy (J/kg)'].min() > 0

        # Check wind sectors
        assert all(sector in ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                             'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
                  for sector in sf_epw_data['Sector'].unique())

    def test_wind_analysis_integration(self, sf_epw_data):
        """Test wind analysis with real EPW data."""
        wind_speed = sf_epw_data['Wind Speed (m/s)']
        wind_direction = sf_epw_data['Wind Direction (°)']

        # Test basic wind speed adjustment
        adjusted_speed = adjust_wind_speed(
            wind_speed, ref_height=10, new_height=80, shear_coef=0.14
        )

        assert isinstance(adjusted_speed, pd.Series)
        assert len(adjusted_speed) == 8760
        # Check that non-zero wind speeds are increased at higher elevation
        non_zero_mask = wind_speed > 0
        if non_zero_mask.any():
            assert all(adjusted_speed[non_zero_mask] > wind_speed[non_zero_mask])
        # Check that zero wind speeds remain zero
        zero_mask = wind_speed == 0
        if zero_mask.any():
            assert all(adjusted_speed[zero_mask] == 0)

        # Test wind direction mapping
        sectors = map_wind_direction_to_sector(wind_direction, num_sectors=16)
        assert isinstance(sectors, pd.Series)
        assert len(sectors) == 8760

        # Test advanced wind analysis
        wind_analysis_results = wind_analysis.analyze_wind_resource(
            wind_speed=wind_speed,
            wind_direction=wind_direction,
            height=10.0,
            target_height=80.0,
            shear_coefficient=0.14
        )

        assert isinstance(wind_analysis_results, dict)
        assert 'basic_statistics' in wind_analysis_results
        assert 'adjusted_statistics' in wind_analysis_results
        assert 'wind_rose_data' in wind_analysis_results
        assert 'weibull_parameters' in wind_analysis_results

        # Check statistics are reasonable
        stats = wind_analysis_results['basic_statistics']
        assert stats['mean_speed'] > 0
        assert stats['max_speed'] > stats['mean_speed']
        assert stats['calm_percentage'] >= 0

    def test_solar_analysis_integration(self, sf_epw_data):
        """Test solar analysis with real EPW data."""
        # Test surface irradiation calculations
        orientations = [0, 90, 180, 270]  # N, E, S, W

        solar_results = get_surface_irradiation_orientations_epw(
            sf_epw_data,
            orientations=orientations,
            albedo=0.2
        )

        assert isinstance(solar_results, dict)
        assert len(solar_results) == 4

        for orientation in orientations:
            key = f"{orientation}°"
            assert key in solar_results
            assert isinstance(solar_results[key], pd.Series)
            assert len(solar_results[key]) == 8760
            assert all(solar_results[key] >= 0)  # Irradiation should be non-negative

    def test_state_point_integration(self, sf_epw_data):
        """Test state point analysis with real EPW data."""
        # Test creating state points from EPW data
        state_points = create_state_point_from_epw(sf_epw_data)

        assert isinstance(state_points, StatePoint)
        assert len(state_points.dry_bulb_temp) == 8760
        assert len(state_points.relative_humidity) == 8760

        # Check psychrometric properties are reasonable
        assert (state_points.humidity_ratio >= 0).all()
        assert (state_points.enthalpy > 0).all()
        eps = 1e-8
        assert (state_points.relative_humidity <= 1.0 + eps).all()
        assert (state_points.relative_humidity >= 0.0 - eps).all()

        # Test with a subset of data for detailed analysis
        subset_data = sf_epw_data.head(100)
        subset_state_points = create_state_point_from_epw(subset_data)

        assert len(subset_state_points.dry_bulb_temp) == 100

        # Test DataFrame conversion
        df = subset_state_points.to_dataframe()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 100
        assert 'dry_bulb_temp' in df.columns
        assert 'humidity_ratio' in df.columns
        assert 'enthalpy' in df.columns

    def test_full_workflow_integration(self, sf_epw_data):
        """Test complete workflow from EPW data to final analysis."""
        # Step 1: Load and process EPW data
        assert len(sf_epw_data) == 8760

        # Step 2: Create state points
        state_points = create_state_point_from_epw(sf_epw_data)

        # Step 3: Analyze wind
        wind_results = wind_analysis.analyze_wind_resource(
            wind_speed=sf_epw_data['Wind Speed (m/s)'],
            wind_direction=sf_epw_data['Wind Direction (°)'],
            height=10.0,
            target_height=80.0
        )

        # Step 4: Analyze solar
        solar_results = get_surface_irradiation_orientations_epw(
            sf_epw_data,
            orientations=[0, 90, 180, 270]
        )

        # Step 5: Verify all results are consistent
        assert len(state_points.dry_bulb_temp) == len(sf_epw_data)
        assert len(wind_results['adjusted_wind_speed']) == len(sf_epw_data)
        assert len(solar_results['0°']) == len(sf_epw_data)

        # Step 6: Check data quality
        assert not state_points.dry_bulb_temp.isna().any()
        assert not wind_results['adjusted_wind_speed'].isna().any()
        assert not solar_results['0°'].isna().any()

    def test_data_consistency(self, sf_epw_data):
        """Test that all calculated data is consistent."""
        # Check that temperature and humidity data is consistent
        temp = sf_epw_data['Dry Bulb Temperature (°C)']
        rh = sf_epw_data['Relative Humidity (%)']

        # Create state points and verify consistency
        state_points = create_state_point_from_epw(sf_epw_data)

        # Check that relative humidity is properly converted
        eps = 1e-8
        if not (state_points.relative_humidity <= 1.0 + eps).all():
            print('Max relative humidity:', state_points.relative_humidity.max())
            print('Values > 1.0:', state_points.relative_humidity[state_points.relative_humidity > 1.0 + eps])
        assert (state_points.relative_humidity <= 1.0 + eps).all(), f"Relative humidity out of bounds: max={state_points.relative_humidity.max()}"
        if not (state_points.relative_humidity >= 0.0 - eps).all():
            print('Min relative humidity:', state_points.relative_humidity.min())
            print('Values < 0.0:', state_points.relative_humidity[state_points.relative_humidity < 0.0 - eps])
        assert (state_points.relative_humidity >= 0.0 - eps).all(), f"Relative humidity out of bounds: min={state_points.relative_humidity.min()}"
        # Check that humidity ratio is positive
        if not (state_points.humidity_ratio >= 0).all():
            print('Min humidity ratio:', state_points.humidity_ratio.min())
            print('Values < 0:', state_points.humidity_ratio[state_points.humidity_ratio < 0])
        assert (state_points.humidity_ratio >= 0).all(), f"Humidity ratio out of bounds: min={state_points.humidity_ratio.min()}"

        # Check that enthalpy increases with temperature (generally)
        temp_enthalpy_corr = temp.corr(state_points.enthalpy)
        assert temp_enthalpy_corr > 0.5  # Should be strongly correlated

    def test_performance_with_large_dataset(self, sf_epw_data):
        """Test performance with the full 8760-hour dataset."""
        import time

        # Test wind analysis performance
        start_time = time.time()
        wind_results = wind_analysis.analyze_wind_resource(
            wind_speed=sf_epw_data['Wind Speed (m/s)'],
            wind_direction=sf_epw_data['Wind Direction (°)'],
            height=10.0,
            target_height=80.0
        )
        wind_time = time.time() - start_time

        # Test solar analysis performance
        start_time = time.time()
        solar_results = get_surface_irradiation_orientations_epw(
            sf_epw_data,
            orientations=[0, 90, 180, 270]
        )
        solar_time = time.time() - start_time

        # Test state point creation performance
        start_time = time.time()
        state_points = create_state_point_from_epw(sf_epw_data)
        state_time = time.time() - start_time

        # All operations should complete in reasonable time (< 10 seconds each)
        assert wind_time < 10.0, f"Wind analysis took {wind_time:.2f}s"
        assert solar_time < 10.0, f"Solar analysis took {solar_time:.2f}s"
        assert state_time < 10.0, f"State point creation took {state_time:.2f}s"

        print(f"Performance: Wind={wind_time:.2f}s, Solar={solar_time:.2f}s, State={state_time:.2f}s")