#!/usr/bin/env python3
"""
Simple test script for solar angle calculations.
"""

import pandas as pd
import numpy as np
from climate_utils.solar import calculate_solar_angles_epw

def test_solar_angles():
    """Test the solar angle calculation function with sample data."""
    
    # Create sample EPW data (24 hours)
    sample_data = {
        'Dry Bulb Temperature (°C)': [20] * 24,  # Constant temperature
        'Direct Normal Radiation (Wh/m²)': [100] * 24,
        'Diffuse Horizontal Radiation (Wh/m²)': [50] * 24,
        'Global Horizontal Radiation (Wh/m²)': [150] * 24
    }
    
    df_epw = pd.DataFrame(sample_data)
    
    # Test coordinates (New York City)
    latitude = 40.7128
    longitude = -74.0060
    timezone = -5
    
    try:
        # Calculate solar angles
        zenith_angles, azimuth_angles = calculate_solar_angles_epw(
            df_epw=df_epw,
            latitude=latitude,
            longitude=longitude,
            timezone=timezone
        )
        
        # Basic validation
        print("✅ Solar angle calculation successful!")
        print(f"✅ Zenith angles: {len(zenith_angles)} values, range: {zenith_angles.min():.1f}° to {zenith_angles.max():.1f}°")
        print(f"✅ Azimuth angles: {len(azimuth_angles)} values, range: {azimuth_angles.min():.1f}° to {azimuth_angles.max():.1f}°")
        
        # Check for reasonable values
        assert 0 <= zenith_angles.min() <= zenith_angles.max() <= 90, "Zenith angles should be between 0 and 90 degrees"
        assert 0 <= azimuth_angles.min() <= azimuth_angles.max() <= 360, "Azimuth angles should be between 0 and 360 degrees"
        print("✅ Angle ranges are within expected bounds")
        
        # Show sample values
        print("\nSample solar angles (first 6 hours):")
        print("Hour | Zenith | Azimuth")
        print("-----|--------|--------")
        for i in range(6):
            print(f"{i:4d} | {zenith_angles.iloc[i]:6.1f}° | {azimuth_angles.iloc[i]:7.1f}°")
            
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Install pvlib with: pip install pvlib")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_solar_angles()
    if success:
        print("\n🎉 All tests passed! The solar angle calculation is working correctly.")
    else:
        print("\n❌ Tests failed. Please check the error messages above.") 