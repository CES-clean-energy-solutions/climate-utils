# Climate Utils

A comprehensive Python package for climate data processing, weather file manipulation, and environmental analysis with robust EPW file support.

## Overview

Climate Utils provides essential utilities for working with climate data, EnergyPlus Weather (EPW) files, and environmental analysis. This package serves as the foundation for multiple climate-related applications with a focus on accuracy, reliability, and ease of use.

## Features

- **EPW File Processing**: Load, parse, and validate EnergyPlus Weather files with comprehensive data mapping
- **Wind Analysis**: Wind speed adjustments, directional analysis, sector mapping, and resource assessment
- **Solar Calculations**: Solar radiation calculations for different orientations and surface types
- **Psychrometric Analysis**: State point calculations and psychrometric properties using industry-standard libraries
- **Comprehensive Documentation**: Detailed EPW file structure documentation and column mappings
- **Robust Testing**: Extensive test suite with real EPW data integration

## Installation

### From GitHub (Development)
```bash
pip install git+https://github.com/your-org/climate-utils.git
```

### From PyPI (When Available)
```bash
pip install climate-utils
```

For extended features:
```bash
pip install climate-utils[extended]
```

## Quick Start

```python
import pandas as pd
from climate_utils import epw, wind, solar, state_point, wind_analysis

# Load EPW weather file
df_epw = epw.load_epw_to_df('path/to/weather.epw')

# Create psychrometric state points from EPW data
state_points = state_point.create_state_point_from_epw(df_epw)

# Adjust wind speed for height differences
adjusted_wind = wind.adjust_wind_speed(
    wind_speed=df_epw['Wind Speed (m/s)'],
    ref_height=10,
    new_height=50,
    shear_coef=0.15
)

# Map wind directions to sectors
wind_sectors = wind.map_wind_direction_to_sector(
    df_epw['Wind Direction (°)'],
    num_sectors=16
)

# Calculate solar radiation for different orientations
solar_data = solar.get_surface_irradiation_orientations_epw(
    df_epw,
    orientations=[0, 90, 180, 270]  # N, E, S, W
)

# Advanced wind analysis
wind_analysis_results = wind_analysis.analyze_wind_resource(
    wind_speed=df_epw['Wind Speed (m/s)'],
    wind_direction=df_epw['Wind Direction (°)'],
    height=10.0,
    target_height=80.0
)
```

## Package Structure

```
climate-utils/
├── src/climate_utils/
│   ├── __init__.py              # Main package interface
│   ├── epw.py                  # EPW file processing
│   ├── wind.py                 # Basic wind utilities
│   ├── wind_analysis.py        # Advanced wind analysis
│   ├── solar.py                # Solar calculations
│   ├── state_point.py          # Psychrometric analysis
│   └── psychrometrics_utils.py # Psychrometric calculations
├── tests/                      # Comprehensive test suite
│   ├── test_epw.py            # EPW processing tests
│   ├── test_wind.py           # Wind analysis tests
│   ├── test_solar.py          # Solar calculation tests
│   ├── test_state_point.py    # Psychrometric tests
│   └── test_integration.py    # Integration tests with real EPW data
├── docs/                       # Documentation
│   └── epw_file_structure.md  # Comprehensive EPW file documentation
├── pyproject.toml             # Package configuration
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

## Module Overview

### Core Modules

#### `epw.py` - EPW File Processing
**Purpose**: Load, parse, and manipulate EnergyPlus Weather (EPW) files with precise column mapping.

**Key Functions**:
- `load_epw(epw_file_path)` - Load EPW file using ladybug-core
- `epw_to_df(epw)` - Convert EPW object to pandas DataFrame with explicit column names
- `load_epw_to_df(epw_file_path)` - Load EPW file and return processed DataFrame
- `create_blank_epw()` - Create blank EPW object for custom data
- `update_epw_column(epw, column_name, data_series)` - Update specific EPW data columns

**Features**:
- **Explicit DataFrame Columns**: Uses precise column names like `'Dry Bulb Temperature (°C)'`, `'Wind Speed (m/s)'`
- Automatic psychrometric property calculations (humidity ratio, enthalpy)
- Wind direction sector mapping (16 sectors)
- Data validation and error handling
- Support for custom EPW data insertion
- Comprehensive EPW file structure documentation

#### `wind.py` - Basic Wind Utilities
**Purpose**: Basic wind speed adjustments and direction mapping.

**Key Functions**:
- `adjust_wind_speed(wind_speed, ref_height, new_height, shear_coef)` - Adjust wind speed for height differences
- `map_wind_direction_to_sector(wind_direction, num_sectors)` - Map wind directions to compass sectors

**Features**:
- Power law wind profile calculations
- Support for 4, 8, and 16 compass sectors
- Handles scalar and pandas Series inputs
- Robust error handling for edge cases

#### `wind_analysis.py` - Advanced Wind Analysis
**Purpose**: Comprehensive wind resource analysis and statistics.

**Key Functions**:
- `adjust_wind_speed_height(wind_speed, from_height, to_height, shear_coefficient)` - Height adjustment with multiple methods
- `calculate_wind_rose_data(wind_speed, wind_direction, speed_bins, direction_bins)` - Generate wind rose data
- `calculate_wind_statistics(wind_speed, wind_direction, time_period)` - Comprehensive wind statistics
- `analyze_wind_resource(wind_speed, wind_direction, height, target_height, shear_coefficient)` - Complete wind resource analysis

**Features**:
- Logarithmic and power law wind profiles
- Wind rose data generation for visualization
- Statistical analysis (mean, std, percentiles)
- Weibull distribution fitting
- Power density calculations

#### `solar.py` - Solar Calculations
**Purpose**: Solar radiation calculations for different surface orientations.

**Key Functions**:
- `get_surface_irradiation_orientations_epw(df_epw, orientations, albedo, latitude, longitude, timezone)` - Calculate surface irradiation for multiple orientations
- `calculate_surface_irradiation(dni, dhi, ghi, surface_azimuth, latitude, longitude, timezone, albedo)` - Calculate irradiation for specific orientation
- `calculate_solar_angles_epw(df_epw, latitude, longitude, timezone)` - Calculate solar zenith and azimuth angles

**Features**:
- **Direct DataFrame Access**: Uses explicit column names like `'Direct Normal Radiation (Wh/m²)'`
- Support for multiple surface orientations
- Direct, diffuse, and reflected radiation components
- Configurable ground albedo
- Solar position calculations (simplified)

#### `state_point.py` - Psychrometric Analysis
**Purpose**: Psychrometric state point calculations and property analysis using industry-standard psychrolib.

**Key Functions**:
- `StatePoint(dry_bulb_temp, relative_humidity, ...)` - Main class for psychrometric calculations
- `create_state_point_from_epw(df_epw)` - Create StatePoint from EPW weather data

**StatePoint Properties**:
- `humidity_ratio` - Humidity ratio in kg/kg
- `relative_humidity` - Relative humidity as fraction (0-1)
- `wet_bulb_temp` - Wet bulb temperature in Celsius
- `dew_point_temp` - Dew point temperature in Celsius
- `enthalpy` - Enthalpy in kJ/kg
- `specific_volume` - Specific volume in m³/kg

**Features**:
- **Direct DataFrame Access**: Uses explicit column names like `'Dry Bulb Temperature (°C)'`
- Multiple input methods (relative humidity, wet bulb, dew point, humidity ratio)
- Automatic property calculations using psychrolib
- Support for altitude-based pressure calculations
- DataFrame conversion and export
- Robust floating-point precision handling

### Utility Functions

#### Wind Analysis
- **Height Adjustments**: Convert wind speeds between different measurement heights
- **Direction Mapping**: Convert wind directions to compass sectors
- **Statistical Analysis**: Calculate mean, standard deviation, and percentiles
- **Resource Assessment**: Comprehensive wind resource evaluation

#### Solar Analysis
- **Surface Irradiation**: Calculate solar radiation on tilted surfaces
- **Orientation Analysis**: Compare different surface orientations
- **Component Separation**: Direct, diffuse, and reflected radiation

#### Psychrometric Analysis
- **State Point Creation**: Create psychrometric state points from various inputs
- **Property Calculations**: Automatic calculation of all psychrometric properties
- **EPW Integration**: Direct integration with EPW weather data using explicit column names

#### EPW Processing
- **File Loading**: Load and parse EPW weather files using ladybug-core
- **Data Processing**: Convert to pandas DataFrames with explicit column names and enhanced properties
- **Custom Data**: Create and modify EPW files for custom analysis
- **Comprehensive Documentation**: Detailed EPW file structure and column mapping documentation

## Key Improvements

### DataFrame Column Names
All modules now use explicit, descriptive DataFrame column names that match the EPW file structure:
- `'Dry Bulb Temperature (°C)'`
- `'Relative Humidity (%)'`
- `'Wind Speed (m/s)'`
- `'Wind Direction (°)'`
- `'Direct Normal Radiation (Wh/m²)'`
- `'Diffuse Horizontal Radiation (Wh/m²)'`

### Comprehensive Documentation
- **EPW File Structure**: Complete documentation of EPW file format, header lines, and data columns
- **Column Mappings**: Detailed mapping between EPW field numbers, ladybug property names, and DataFrame columns
- **Data Validation**: Information about missing value indicators and data validation

### Robust Testing
- **28 Comprehensive Tests**: Covering all modules with real EPW data integration
- **Integration Tests**: Tests using actual EPW files to ensure real-world compatibility
- **Floating Point Precision**: Robust handling of floating-point precision issues
- **Error Handling**: Comprehensive error testing for edge cases

### Dependencies
- **ladybug-core**: Required dependency for EPW file processing
- **psychrolib**: Industry-standard psychrometric calculations
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computations

## Development

### Running Tests
```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest -v tests/

# Run specific test file
pytest tests/test_integration.py
```

### Building Documentation
```bash
# Install development dependencies
pip install -e .[dev]

# Run tests
pytest tests/
```

## Documentation

- **EPW File Structure**: See `docs/epw_file_structure.md` for comprehensive EPW file documentation
- **API Reference**: Full API documentation available at: [climate-utils.readthedocs.io](https://climate-utils.readthedocs.io)

## Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests.

## License

MIT License - see LICENSE file for details.