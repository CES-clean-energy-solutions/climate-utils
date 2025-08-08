#!/usr/bin/env python3
"""
Example demonstrating DataFrame type validation and type hints in climate-utils.

This example shows how to:
1. Use type hints for DataFrame validation
2. Validate required columns at runtime
3. Handle validation errors gracefully
4. Use the different validation approaches
"""

import pandas as pd
import numpy as np
from climate_utils import (
    load_epw_to_df,
    validate_epw_dataframe,
    REQUIRED_EPW_COLUMNS,
    get_surface_irradiation_orientations_epw,
    get_epw_column_info
)


def example_basic_validation():
    """Example of basic DataFrame validation."""
    print("=== Basic DataFrame Validation ===")

    # Create a valid DataFrame
    df_valid = pd.DataFrame({
        'Dry Bulb Temperature (°C)': [20.0, 25.0, 30.0],
        'Relative Humidity (%)': [50.0, 60.0, 70.0],
        'Wind Speed (m/s)': [2.0, 3.0, 4.0],
        'Wind Direction (°)': [180.0, 270.0, 90.0],
    })

    print("✅ Valid DataFrame created")
    print(f"Columns: {list(df_valid.columns)}")

    # Validate basic columns
    try:
        validate_epw_dataframe(df_valid, REQUIRED_EPW_COLUMNS['basic'])
        print("✅ Basic validation passed")
    except ValueError as e:
        print(f"❌ Basic validation failed: {e}")

    # Create an invalid DataFrame (missing required columns)
    df_invalid = pd.DataFrame({
        'Dry Bulb Temperature (°C)': [20.0, 25.0, 30.0],
        'Relative Humidity (%)': [50.0, 60.0, 70.0],
        # Missing 'Wind Speed (m/s)' and 'Wind Direction (°)'
    })

    print(f"\n❌ Invalid DataFrame created")
    print(f"Columns: {list(df_invalid.columns)}")

    # This should fail
    try:
        validate_epw_dataframe(df_invalid, REQUIRED_EPW_COLUMNS['basic'])
        print("✅ Basic validation passed (unexpected)")
    except ValueError as e:
        print(f"❌ Basic validation failed as expected: {e}")


def example_solar_validation():
    """Example of solar-specific DataFrame validation."""
    print("\n=== Solar DataFrame Validation ===")

    # Create a valid solar DataFrame
    df_solar = pd.DataFrame({
        'Direct Normal Radiation (Wh/m²)': [800.0, 900.0, 1000.0],
        'Diffuse Horizontal Radiation (Wh/m²)': [200.0, 150.0, 100.0],
        'Global Horizontal Radiation (Wh/m²)': [1000.0, 1050.0, 1100.0],
    })

    print("✅ Valid solar DataFrame created")
    print(f"Columns: {list(df_solar.columns)}")

    # Validate solar columns
    try:
        validate_epw_dataframe(df_solar, REQUIRED_EPW_COLUMNS['solar'])
        print("✅ Solar validation passed")
    except ValueError as e:
        print(f"❌ Solar validation failed: {e}")

    # Create an invalid solar DataFrame
    df_invalid_solar = pd.DataFrame({
        'Direct Normal Radiation (Wh/m²)': [800.0, 900.0, 1000.0],
        # Missing diffuse and global radiation
    })

    print(f"\n❌ Invalid solar DataFrame created")
    print(f"Columns: {list(df_invalid_solar.columns)}")

    # This should fail
    try:
        validate_epw_dataframe(df_invalid_solar, REQUIRED_EPW_COLUMNS['solar'])
        print("✅ Solar validation passed (unexpected)")
    except ValueError as e:
        print(f"❌ Solar validation failed as expected: {e}")


def example_function_with_validation():
    """Example of using validation in functions."""
    print("\n=== Function with Validation ===")

    # Create a DataFrame with solar data
    df_solar = pd.DataFrame({
        'Direct Normal Radiation (Wh/m²)': [800.0] * 24,
        'Diffuse Horizontal Radiation (Wh/m²)': [200.0] * 24,
        'Global Horizontal Radiation (Wh/m²)': [1000.0] * 24,
    })

    print("✅ Created DataFrame for solar analysis")

    # This function validates internally
    try:
        results = get_surface_irradiation_orientations_epw(df_solar)
        print("✅ Solar analysis completed successfully")
        print(f"Results: {list(results.keys())}")
    except ValueError as e:
        print(f"❌ Solar analysis failed: {e}")

    # Try with invalid DataFrame
    df_invalid = pd.DataFrame({
        'Direct Normal Radiation (Wh/m²)': [800.0] * 24,
        # Missing required columns
    })

    print(f"\n❌ Created invalid DataFrame for solar analysis")

    try:
        results = get_surface_irradiation_orientations_epw(df_invalid)
        print("✅ Solar analysis completed (unexpected)")
    except ValueError as e:
        print(f"❌ Solar analysis failed as expected: {e}")


def example_column_info():
    """Example of getting column information."""
    print("\n=== Column Information ===")

    column_info = get_epw_column_info()

    print("Available EPW columns:")
    for column, info in column_info.items():
        required = "Required" if info['required'] else "Optional"
        print(f"  {column}:")
        print(f"    Description: {info['description']}")
        print(f"    Unit: {info['unit']}")
        print(f"    Type: {info['type']}")
        print(f"    Status: {required}")
        print()


def example_required_columns():
    """Example of different required column sets."""
    print("\n=== Required Column Sets ===")

    print("Available column sets:")
    for analysis_type, columns in REQUIRED_EPW_COLUMNS.items():
        print(f"  {analysis_type}:")
        for col in columns:
            print(f"    - {col}")
        print()


def example_real_epw_file():
    """Example with a real EPW file if available."""
    print("\n=== Real EPW File Example ===")

    try:
        # Try to load the test EPW file
        df_epw = load_epw_to_df('tests/USA_CA_San.Francisco.Intl.AP.724940_TMYx.epw')

        print("✅ Successfully loaded EPW file")
        print(f"DataFrame shape: {df_epw.shape}")
        print(f"Columns: {list(df_epw.columns)}")

        # Validate basic structure
        try:
            validate_epw_dataframe(df_epw, REQUIRED_EPW_COLUMNS['basic'])
            print("✅ Basic validation passed")
        except ValueError as e:
            print(f"❌ Basic validation failed: {e}")

        # Validate solar structure
        try:
            validate_epw_dataframe(df_epw, REQUIRED_EPW_COLUMNS['solar'])
            print("✅ Solar validation passed")
        except ValueError as e:
            print(f"❌ Solar validation failed: {e}")

        # Try solar analysis
        try:
            results = get_surface_irradiation_orientations_epw(df_epw)
            print("✅ Solar analysis completed")
            print(f"Available orientations: {list(results.keys())}")
        except ValueError as e:
            print(f"❌ Solar analysis failed: {e}")

    except FileNotFoundError:
        print("❌ EPW file not found - skipping real file example")
    except Exception as e:
        print(f"❌ Error loading EPW file: {e}")


def main():
    """Run all examples."""
    print("DataFrame Type Validation Examples")
    print("=" * 50)

    example_basic_validation()
    example_solar_validation()
    example_function_with_validation()
    example_column_info()
    example_required_columns()
    example_real_epw_file()

    print("\n" + "=" * 50)
    print("Examples completed!")


if __name__ == "__main__":
    main()