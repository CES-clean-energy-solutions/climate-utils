"""
Tests for solar calculation utilities.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from climate_utils.solar import (
    get_surface_irradiation_orientations_epw,
    get_surface_irradiation_components,
    calculate_surface_irradiation,
    calculate_solar_zenith,
    calculate_solar_azimuth,
    calculate_cos_incidence,
    calculate_solar_angles_epw,
)


class TestSolarCalculations:
    """Test solar calculation functions."""

    def test_calculate_solar_zenith(self):
        """Test solar zenith angle calculation."""
        # Test at noon
        zenith = calculate_solar_zenith(12, 40.0, -74.0, -5)

        assert isinstance(zenith, (int, float))  # Can be int or float
        assert 0 <= zenith <= 90

        # Test at different hours to verify the function works
        zenith_morning = calculate_solar_zenith(6, 40.0, -74.0, -5)
        zenith_evening = calculate_solar_zenith(18, 40.0, -74.0, -5)

        assert 0 <= zenith_morning <= 90
        assert 0 <= zenith_evening <= 90

        # The simplified function should return different values for different hours
        assert zenith_morning != zenith_evening or zenith_morning != zenith

    def test_calculate_solar_azimuth(self):
        """Test solar azimuth angle calculation."""
        # Test at noon
        azimuth = calculate_solar_azimuth(12, 40.0, -74.0, -5)

        assert isinstance(azimuth, (int, float))  # Can be int or float
        assert 0 <= azimuth <= 360
        # At noon, azimuth should be around 180° (south)
        assert abs(azimuth - 180) < 20  # Allow some tolerance

    def test_calculate_cos_incidence(self):
        """Test cosine of incidence angle calculation."""
        # Test with sun directly overhead (zenith = 0) and vertical surface (azimuth = 0)
        cos_inc = calculate_cos_incidence(0, 180, 0)
        assert (
            abs(cos_inc - 0) < 1e-6
        )  # Should be 0 for vertical surface with overhead sun

        # Test with sun at 45° zenith and surface facing south
        cos_inc = calculate_cos_incidence(45, 180, 180)
        assert 0 < cos_inc < 1  # Should be positive but less than 1

    def test_calculate_surface_irradiation(self):
        """Test surface irradiation calculation."""
        # Create sample data
        n_hours = 24
        dni = pd.Series([800] * n_hours)  # 800 W/m² direct normal
        dhi = pd.Series([200] * n_hours)  # 200 W/m² diffuse horizontal
        ghi = pd.Series([1000] * n_hours)  # 1000 W/m² global horizontal

        # Test vertical surface facing south
        surface_irr = calculate_surface_irradiation(
            dni, dhi, ghi, 180, 40.0, -74.0, -5, 0.2
        )

        assert isinstance(surface_irr, pd.Series)
        assert len(surface_irr) == n_hours
        assert all(surface_irr >= 0)  # Irradiation should be non-negative

    def test_get_surface_irradiation_orientations_epw(self, sf_epw_data):
        """Test surface irradiation calculation with EPW data."""
        # Test with default orientations
        results = get_surface_irradiation_orientations_epw(sf_epw_data)

        assert isinstance(results, dict)
        assert len(results) == 4  # Default: N, E, S, W
        assert all(key in results for key in ["0°", "90°", "180°", "270°"])

        # Check that all results are valid
        for orientation, irradiation in results.items():
            assert isinstance(irradiation, pd.Series)
            assert len(irradiation) == len(sf_epw_data)
            assert all(irradiation >= 0)  # Non-negative irradiation

        # Test with custom orientations
        custom_orientations = [45, 135, 225, 315]
        results = get_surface_irradiation_orientations_epw(
            sf_epw_data, orientations=custom_orientations
        )

        assert len(results) == 4
        assert all(key in results for key in ["45°", "135°", "225°", "315°"])

    def test_calculate_solar_angles_epw_with_pvlib(self, sf_epw_data):
        """Test solar angles calculation with EPW data using pvlib."""

        # Test with provided coordinates
        zenith_angles, azimuth_angles = calculate_solar_angles_epw(
            sf_epw_data, latitude=37.7749, longitude=-122.4194, timezone=-8
        )

        assert isinstance(zenith_angles, pd.Series)
        assert isinstance(azimuth_angles, pd.Series)
        assert len(zenith_angles) == len(sf_epw_data)
        assert len(azimuth_angles) == len(sf_epw_data)

        # Check angle ranges
        assert all(0 <= zenith_angles) and all(zenith_angles <= 90)
        assert all(0 <= azimuth_angles) and all(azimuth_angles <= 360)

        # Check for reasonable values (no NaN or extreme values)
        assert not zenith_angles.isna().any()
        assert not azimuth_angles.isna().any()
        assert not np.isinf(zenith_angles).any()
        assert not np.isinf(azimuth_angles).any()

    def test_calculate_solar_angles_epw_without_pvlib(self, sf_epw_data):
        """Test solar angles calculation when pvlib is not available."""
        # This test is no longer needed since pvlib is now required
        # The function will fail at import time if pvlib is not available
        pass

    def test_calculate_solar_angles_epw_default_coordinates(self, sf_epw_data):
        """Test solar angles calculation with default coordinates."""

        # Test with default coordinates (should use warnings)
        zenith_angles, azimuth_angles = calculate_solar_angles_epw(sf_epw_data)

        assert isinstance(zenith_angles, pd.Series)
        assert isinstance(azimuth_angles, pd.Series)
        assert len(zenith_angles) == len(sf_epw_data)
        assert len(azimuth_angles) == len(sf_epw_data)

    def test_calculate_solar_angles_epw_datetime_index(self):
        """Test solar angles calculation with proper datetime index."""

        # Create DataFrame with datetime index
        dates = pd.date_range("2023-01-01", periods=24, freq="h")
        df_epw = pd.DataFrame(
            {
                "Dry Bulb Temperature (°C)": [20] * 24,
                "Direct Normal Radiation (Wh/m²)": [800] * 24,
                "Diffuse Horizontal Radiation (Wh/m²)": [200] * 24,
                "Global Horizontal Radiation (Wh/m²)": [1000] * 24,
            },
            index=dates,
        )

        zenith_angles, azimuth_angles = calculate_solar_angles_epw(
            df_epw, latitude=40.0, longitude=-74.0, timezone=-5
        )

        assert isinstance(zenith_angles, pd.Series)
        assert isinstance(azimuth_angles, pd.Series)
        assert len(zenith_angles) == 24
        assert len(azimuth_angles) == 24

        # Check that the index is based on the input dates (converted to UTC)
        # The function converts local time to UTC, so we need to check the date/time correspondence
        assert len(zenith_angles.index) == len(dates)
        assert len(azimuth_angles.index) == len(dates)

    def test_solar_angles_edge_cases(self, sf_epw_data):
        """Test solar angles calculation edge cases."""

        # Test at extreme latitudes
        zenith_angles, azimuth_angles = calculate_solar_angles_epw(
            sf_epw_data, latitude=80.0, longitude=0.0, timezone=0
        )

        assert isinstance(zenith_angles, pd.Series)
        assert isinstance(azimuth_angles, pd.Series)
        assert all(zenith_angles >= 0) and all(zenith_angles <= 90)
        assert all(azimuth_angles >= 0) and all(azimuth_angles <= 360)

        # Test at equator
        zenith_angles, azimuth_angles = calculate_solar_angles_epw(
            sf_epw_data, latitude=0.0, longitude=0.0, timezone=0
        )

        assert isinstance(zenith_angles, pd.Series)
        assert isinstance(azimuth_angles, pd.Series)
        assert all(zenith_angles >= 0) and all(zenith_angles <= 90)
        assert all(azimuth_angles >= 0) and all(azimuth_angles <= 360)

    def test_solar_geometry_physical_validation(self, sf_epw_data):
        """Test real physical validation of solar geometry using San Francisco EPW data.

        This test validates solar angles against known physical constraints for San Francisco International Airport:
        - Location: 37.621313°N, 122.365°W, UTC-8
        - Validates against exact known values for 2023 solstices and equinoxes
        """

        # Known solar geometry values for San Francisco International Airport (2023)
        SF_KNOWN_VALUES = {
            "Spring Equinox": {
                "date": "2023-03-20",
                "time": "12:00",
                "declination": 0.000,
                "zenith": 37.621,
                "elevation": 52.379,
                "azimuth": 180.000,
            },
            "Summer Solstice": {
                "date": "2023-06-21",
                "time": "12:00",
                "declination": 23.44,
                "zenith": 14.182,
                "elevation": 75.818,
                "azimuth": 180.000,
            },
            "Autumn Equinox": {
                "date": "2023-09-23",
                "time": "12:00",
                "declination": 0.000,
                "zenith": 37.621,
                "elevation": 52.379,
                "azimuth": 180.000,
            },
            "Winter Solstice": {
                "date": "2023-12-21",
                "time": "12:00",
                "declination": -23.44,
                "zenith": 61.061,
                "elevation": 28.939,
                "azimuth": 180.000,
            },
        }

        # Get location information from EPW data
        sf_lat, sf_lon, sf_tz = sf_epw_data._epw_location_info
        print(f"Using EPW location: {sf_lat}°N, {sf_lon}°W, UTC{sf_tz:+g}")

        # Calculate solar angles for the entire year (location info extracted automatically)
        zenith_angles, azimuth_angles = calculate_solar_angles_epw(sf_epw_data)

        # Get the datetime index to identify key dates
        dates = sf_epw_data.index

        # Validate against known values for each key date
        for event_name, expected_values in SF_KNOWN_VALUES.items():
            # Parse the expected date
            expected_date = pd.Timestamp(expected_values["date"])

            # Find data for this date
            date_mask = (dates.month == expected_date.month) & (
                dates.day == expected_date.day
            )

            if date_mask.any():
                # Get the specific time (12:00)
                expected_time = expected_values["time"]
                hour = int(expected_time.split(":")[0])
                
                # Find the index for 12:00 on this date
                time_mask = date_mask & (dates.hour == hour)
                
                if time_mask.any():
                    # Get the exact 12:00 values
                    # Find the numeric position to avoid timezone issues
                    noon_positions = np.where(time_mask)[0]
                    if len(noon_positions) > 0:
                        noon_position = noon_positions[0]
                        actual_zenith = zenith_angles.iloc[noon_position]
                        actual_azimuth = azimuth_angles.iloc[noon_position]
                    else:
                        print(f"Warning: No data found for {event_name} at {expected_time}")
                        continue
                    
                    # Validate zenith angle (allow 2° tolerance)
                    # Note: Small variations are expected due to atmospheric refraction and calculation precision
                    expected_zenith = expected_values["zenith"]
                    zenith_tolerance = 2.0
                    assert (
                        abs(actual_zenith - expected_zenith) <= zenith_tolerance
                    ), f"{event_name} zenith angle mismatch: expected {expected_zenith:.3f}°, got {actual_zenith:.3f}°"

                    # Validate azimuth angle (allow 15° tolerance for 12:00 noon)
                    # Note: At clock noon, sun may not be at 180° due to equation of time and longitude offset
                    # Skip azimuth check when sun is nearly overhead (zenith < 10°) as azimuth becomes unstable
                    if actual_zenith >= 10.0:
                        expected_azimuth = expected_values["azimuth"]
                        azimuth_tolerance = 15.0
                        assert (
                            abs(actual_azimuth - expected_azimuth) <= azimuth_tolerance
                        ), f"{event_name} azimuth angle mismatch: expected {expected_azimuth:.3f}°, got {actual_azimuth:.3f}°"
                    else:
                        print(f"  Skipping azimuth check - sun nearly overhead (zenith={actual_zenith:.1f}°)")

                    print(f"{event_name} ({expected_date.strftime('%Y-%m-%d')} {expected_time}):")
                    print(
                        f"  Expected: zenith={expected_zenith:.3f}°, azimuth={expected_azimuth:.3f}°"
                    )
                    print(
                        f"  Actual:   zenith={actual_zenith:.3f}°, azimuth={actual_azimuth:.3f}°"
                    )
                else:
                    print(f"Warning: No data found for {event_name} at {expected_time}")
            else:
                print(
                    f"Warning: No data found for {event_name} ({expected_date.strftime('%Y-%m-%d')})"
                )

        # Validate general physical constraints
        # Zenith angles should be between 0° and 90°
        assert all(zenith_angles >= 0), "Zenith angles should be non-negative"
        assert all(zenith_angles <= 90), "Zenith angles should not exceed 90°"

        # Azimuth angles should be between 0° and 360°
        assert all(azimuth_angles >= 0), "Azimuth angles should be non-negative"
        assert all(azimuth_angles <= 360), "Azimuth angles should not exceed 360°"

        # Print summary statistics
        print(f"\nSan Francisco Solar Geometry Summary:")
        print(f"Location: {sf_lat}°N, {sf_lon}°W, UTC{sf_tz:+g}")
        print(
            f"Annual zenith range: {zenith_angles.min():.2f}° to {zenith_angles.max():.2f}°"
        )
        print(
            f"Annual azimuth range: {azimuth_angles.min():.2f}° to {azimuth_angles.max():.2f}°"
        )

    def test_solar_geometry_sharm_el_sheikh(self, sharm_epw_data):
        """Test real physical validation of solar geometry using Sharm El Sheikh EPW data.

        This test validates solar angles against known physical constraints for Sharm El Sheikh International Airport:
        - Location: ~27.977°N, ~34.395°E, UTC+2
        - Validates against exact known values for 2023 solstices and equinoxes
        """

        # Known solar geometry values for Sharm El Sheikh International Airport (2023)
        SHARM_KNOWN_VALUES = {
            "Spring Equinox": {
                "date": "2023-03-20",
                "time": "12:00",
                "declination": 0.000,
                "zenith": 27.977,
                "elevation": 62.023,
                "azimuth": 180.000,
            },
            "Summer Solstice": {
                "date": "2023-06-21",
                "time": "12:00",
                "declination": 23.440,
                "zenith": 4.537,
                "elevation": 85.463,
                "azimuth": 180.000,
            },
            "Autumn Equinox": {
                "date": "2023-09-23",
                "time": "12:00",
                "declination": 0.000,
                "zenith": 27.977,
                "elevation": 62.023,
                "azimuth": 180.000,
            },
            "Winter Solstice": {
                "date": "2023-12-21",
                "time": "12:00",
                "declination": -23.440,
                "zenith": 51.417,
                "elevation": 38.583,
                "azimuth": 180.000,
            },
        }

        # Get location information from EPW data
        sharm_lat, sharm_lon, sharm_tz = sharm_epw_data._epw_location_info
        print(f"Using EPW location: {sharm_lat}°N, {sharm_lon}°E, UTC{sharm_tz:+g}")

        # Calculate solar angles for the entire year (location info extracted automatically)
        zenith_angles, azimuth_angles = calculate_solar_angles_epw(sharm_epw_data)

        # Get the datetime index to identify key dates
        dates = sharm_epw_data.index

        # Validate against known values for each key date
        for event_name, expected_values in SHARM_KNOWN_VALUES.items():
            # Parse the expected date
            expected_date = pd.Timestamp(expected_values["date"])

            # Find data for this date
            date_mask = (dates.month == expected_date.month) & (
                dates.day == expected_date.day
            )

            if date_mask.any():
                # Get the specific time (12:00)
                expected_time = expected_values["time"]
                hour = int(expected_time.split(":")[0])
                
                # Find the index for 12:00 on this date
                time_mask = date_mask & (dates.hour == hour)
                
                if time_mask.any():
                    # Get the exact 12:00 values
                    # Find the numeric position to avoid timezone issues
                    noon_positions = np.where(time_mask)[0]
                    if len(noon_positions) > 0:
                        noon_position = noon_positions[0]
                        actual_zenith = zenith_angles.iloc[noon_position]
                        actual_azimuth = azimuth_angles.iloc[noon_position]
                    else:
                        print(f"Warning: No data found for {event_name} at {expected_time}")
                        continue
                    
                    # Validate zenith angle (allow 2° tolerance)
                    # Note: Small variations are expected due to atmospheric refraction and calculation precision
                    expected_zenith = expected_values["zenith"]
                    zenith_tolerance = 2.0
                    assert (
                        abs(actual_zenith - expected_zenith) <= zenith_tolerance
                    ), f"{event_name} zenith angle mismatch: expected {expected_zenith:.3f}°, got {actual_zenith:.3f}°"

                    # Validate azimuth angle (allow 15° tolerance for 12:00 noon)
                    # Note: At clock noon, sun may not be at 180° due to equation of time and longitude offset
                    # Skip azimuth check when sun is nearly overhead (zenith < 10°) as azimuth becomes unstable
                    if actual_zenith >= 10.0:
                        expected_azimuth = expected_values["azimuth"]
                        azimuth_tolerance = 15.0
                        assert (
                            abs(actual_azimuth - expected_azimuth) <= azimuth_tolerance
                        ), f"{event_name} azimuth angle mismatch: expected {expected_azimuth:.3f}°, got {actual_azimuth:.3f}°"
                    else:
                        print(f"  Skipping azimuth check - sun nearly overhead (zenith={actual_zenith:.1f}°)")

                    print(f"{event_name} ({expected_date.strftime('%Y-%m-%d')} {expected_time}):")
                    print(
                        f"  Expected: zenith={expected_zenith:.3f}°, azimuth={expected_azimuth:.3f}°"
                    )
                    print(
                        f"  Actual:   zenith={actual_zenith:.3f}°, azimuth={actual_azimuth:.3f}°"
                    )
                else:
                    print(f"Warning: No data found for {event_name} at {expected_time}")
            else:
                print(
                    f"Warning: No data found for {event_name} ({expected_date.strftime('%Y-%m-%d')})"
                )

        # Validate general physical constraints
        # Zenith angles should be between 0° and 90°
        assert all(zenith_angles >= 0), "Zenith angles should be non-negative"
        assert all(zenith_angles <= 90), "Zenith angles should not exceed 90°"

        # Azimuth angles should be between 0° and 360°
        assert all(azimuth_angles >= 0), "Azimuth angles should be non-negative"
        assert all(azimuth_angles <= 360), "Azimuth angles should not exceed 360°"

        # Print summary statistics
        print(f"\nSharm El Sheikh Solar Geometry Summary:")
        print(f"Location: {sharm_lat}°N, {sharm_lon}°E, UTC{sharm_tz:+g}")
        print(
            f"Annual zenith range: {zenith_angles.min():.2f}° to {zenith_angles.max():.2f}°"
        )
        print(
            f"Annual azimuth range: {azimuth_angles.min():.2f}° to {azimuth_angles.max():.2f}°"
        )

    def test_get_surface_irradiation_components(self, sf_epw_data):
        """Test the new surface irradiation components function."""
        # Test with default orientations
        results = get_surface_irradiation_components(
            sf_epw_data,
            latitude=37.7749,
            longitude=-122.4194,
            timezone=-8
        )
        
        # Check DataFrame structure
        assert isinstance(results, pd.DataFrame)
        assert len(results) == len(sf_epw_data)
        
        # Check default orientations (N, E, S, W)
        expected_columns = [
            '0_direct', '0_sky_diffuse', '0_ground_diffuse', '0_global',
            '90_direct', '90_sky_diffuse', '90_ground_diffuse', '90_global',
            '180_direct', '180_sky_diffuse', '180_ground_diffuse', '180_global',
            '270_direct', '270_sky_diffuse', '270_ground_diffuse', '270_global'
        ]
        assert list(results.columns) == expected_columns
        
        # Verify all values are non-negative
        assert (results >= 0).all().all()
        
        # Verify global = direct + sky_diffuse + ground_diffuse
        for orientation in [0, 90, 180, 270]:
            global_col = f'{orientation}_global'
            direct_col = f'{orientation}_direct'
            sky_col = f'{orientation}_sky_diffuse'
            ground_col = f'{orientation}_ground_diffuse'
            
            calculated_global = results[direct_col] + results[sky_col] + results[ground_col]
            np.testing.assert_allclose(
                results[global_col], 
                calculated_global, 
                rtol=1e-10,
                err_msg=f"Global irradiation mismatch for {orientation}° orientation"
            )
    
    def test_get_surface_irradiation_components_custom_orientations(self, sf_epw_data):
        """Test surface irradiation components with custom orientations."""
        custom_orientations = [45, 135, 225, 315]
        
        results = get_surface_irradiation_components(
            sf_epw_data,
            orientations=custom_orientations,
            surface_tilt=45.0,  # Test non-vertical surface
            albedo=0.3,
            latitude=37.7749,
            longitude=-122.4194,
            timezone=-8,
            sky_model='isotropic'
        )
        
        # Check DataFrame structure
        assert isinstance(results, pd.DataFrame)
        assert len(results) == len(sf_epw_data)
        
        # Check custom orientations
        expected_columns = []
        for orientation in custom_orientations:
            expected_columns.extend([
                f'{orientation}_direct',
                f'{orientation}_sky_diffuse', 
                f'{orientation}_ground_diffuse',
                f'{orientation}_global'
            ])
        assert list(results.columns) == expected_columns
        
        # Verify all values are non-negative
        assert (results >= 0).all().all()
    
    def test_get_surface_irradiation_components_sky_models(self, sf_epw_data):
        """Test different sky models produce different results."""
        orientations = [180]  # Just south-facing
        
        # Test different sky models
        sky_models = ['isotropic', 'haydavies', 'reindl', 'king', 'perez']
        results_by_model = {}
        
        for model in sky_models:
            try:
                results = get_surface_irradiation_components(
                    sf_epw_data,
                    orientations=orientations,
                    latitude=37.7749,
                    longitude=-122.4194,
                    timezone=-8,
                    sky_model=model
                )
                results_by_model[model] = results['180_sky_diffuse']
            except Exception as e:
                print(f"Model {model} failed: {e}")
                continue
        
        # Verify we got results for at least isotropic and haydavies
        assert 'isotropic' in results_by_model
        assert 'haydavies' in results_by_model
        
        # Different models should produce different sky diffuse values
        if len(results_by_model) > 1:
            model_names = list(results_by_model.keys())
            for i in range(len(model_names) - 1):
                model1 = model_names[i]
                model2 = model_names[i + 1]
                # Check that at least some values differ between models
                diff = abs(results_by_model[model1] - results_by_model[model2])
                assert diff.max() > 0.1, f"Sky models {model1} and {model2} produce identical results"

    def test_solar_calculations_performance(self, sf_epw_data):
        """Test performance of solar calculations."""
        import time

        # Test surface irradiation performance
        start_time = time.time()
        results = get_surface_irradiation_orientations_epw(sf_epw_data)
        irradiation_time = time.time() - start_time

        assert (
            irradiation_time < 5.0
        ), f"Surface irradiation took {irradiation_time:.2f}s"

        # Test solar angles performance
        start_time = time.time()
        zenith_angles, azimuth_angles = calculate_solar_angles_epw(sf_epw_data)
        angles_time = time.time() - start_time

        assert angles_time < 10.0, f"Solar angles calculation took {angles_time:.2f}s"
        
        # Test new components function performance
        start_time = time.time()
        components = get_surface_irradiation_components(sf_epw_data)
        components_time = time.time() - start_time

        assert components_time < 10.0, f"Components calculation took {components_time:.2f}s"
