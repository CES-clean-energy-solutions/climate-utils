# Climate Utils - Product Requirements Document

## Overview
**Climate Utils** is a shared Python package providing essential utilities for climate data processing, weather file manipulation, and environmental analysis. This package serves as the foundation for multiple climate-related applications.

## Purpose
Extract and consolidate utility functions from the microclimate project into a reusable, pip-installable package that can be shared across multiple projects including Weather Explorer and Energy Simulation applications.

## Target Users
- Climate data analysts
- Building energy simulation engineers
- Weather data processing applications
- Research teams working with EPW files and climate data

## Core Functionality

### 1. EPW (EnergyPlus Weather) File Processing
- **Source**: `lib/util/util_epw.py`
- **Functions**: Load, parse, validate, and convert EPW weather files
- **Key Features**:
  - Load EPW files to pandas DataFrames
  - Extract weather data for simulation
  - Validate EPW data quality
  - Convert between EPW formats

### 2. Wind Analysis
- **Source**: `lib/util/util_wind.py`, `lib/util/util_wind_analysis.py`
- **Functions**: Wind speed adjustments, directional analysis, sector mapping
- **Key Features**:
  - Wind speed height adjustments using shear coefficients
  - Wind direction to sector mapping
  - Wind analysis utilities

### 3. Solar Calculations
- **Source**: `lib/util/util_solar.py`
- **Functions**: Solar radiation calculations for different orientations
- **Key Features**:
  - Surface irradiation calculations
  - Orientation-specific solar analysis
  - Albedo considerations

### 4. Psychrometric Analysis
- **Source**: `lib/util/state_point.py`
- **Functions**: Psychrometric state point calculations
- **Key Features**:
  - State point creation and manipulation
  - Psychrometric property calculations

## Package Structure
```
climate-utils/
├── src/
│   └── climate_utils/
│       ├── __init__.py
│       ├── epw.py           # EPW file processing
│       ├── wind.py          # Wind analysis utilities
│       ├── solar.py         # Solar calculations
│       ├── state_point.py   # Psychrometric analysis
│       └── wind_analysis.py # Advanced wind analysis
├── tests/
├── docs/
├── pyproject.toml
└── README.md
```

## Dependencies
- **Core**: pandas, numpy, datetime
- **Optional**: psychrolib, ladybug-core (for extended EPW support)

## Installation Method
- Pip installable: `pip install climate-utils`
- Development install: `pip install -e .`

## Migration Strategy
1. Extract utility modules from `lib/util/`
2. Refactor imports to use proper package structure
3. Update function signatures for consistency
4. Add comprehensive tests
5. Create documentation and examples

## Success Criteria
- All utility functions work independently
- Weather Explorer can import and use climate-utils
- Energy Simulation can import and use climate-utils
- Package is pip-installable
- Comprehensive test coverage
- Clear documentation and examples

## Future Enhancements
- Support for additional weather file formats
- Extended psychrometric calculations
- Climate zone analysis tools
- Integration with weather APIs