# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Testing
```bash
# Run all tests
pytest tests/

# Run tests with verbose output
pytest -v tests/

# Run specific test file
pytest tests/test_epw.py
pytest tests/test_integration.py

# Run tests with coverage
pytest --cov=src/climate_utils tests/

# Run single test function
pytest tests/test_epw.py::test_load_epw_to_df
```

### Code Quality
```bash
# Format code with Black
black src/ tests/

# Check code style with flake8
flake8 src/ tests/

# Run type checking with mypy
mypy src/climate_utils/

# Run all quality checks together
black src/ tests/ && flake8 src/ tests/ && mypy src/climate_utils/
```

### Package Management
```bash
# Install package in development mode
pip install -e .

# Install with development dependencies
pip install -e .[dev]

# Install with extended features
pip install -e .[extended]

# Build package
python -m build
```

## Architecture Overview

### Core Package Structure
The climate-utils package is organized into specialized modules for different aspects of climate data analysis:

- **epw.py**: EPW (EnergyPlus Weather) file processing using ladybug-core
- **wind.py**: Basic wind utilities (speed adjustments, direction mapping)
- **wind_analysis.py**: Advanced wind resource analysis and statistics
- **solar.py**: Solar radiation calculations using pvlib
- **state_point.py**: Psychrometric analysis using psychrolib
- **psychrometrics_utils.py**: Low-level psychrometric utilities
- **types.py**: TypedDict definitions and validation for DataFrame structures

### Data Flow Architecture
1. **EPW Loading**: `epw.py` loads EPW files and converts to pandas DataFrames with explicit column names
2. **Data Processing**: Modules process DataFrames using standardized column names (e.g., `'Dry Bulb Temperature (°C)'`)
3. **Analysis**: Specialized modules perform domain-specific calculations
4. **Integration**: Results can be combined or exported for further analysis

### Key Design Patterns

#### Explicit DataFrame Column Names
All modules use descriptive, unit-aware column names:
```python
'Dry Bulb Temperature (°C)'
'Wind Speed (m/s)'
'Direct Normal Radiation (Wh/m²)'
'Relative Humidity (%)'
```

#### Module Interdependencies
- `state_point.py` depends on `psychrometrics_utils.py` for calculations
- `solar.py` uses EPW DataFrames from `epw.py`
- `wind_analysis.py` extends functionality from `wind.py`
- All modules can work with DataFrames from `epw.py`

#### Error Handling Strategy
- Input validation at module entry points
- Graceful handling of missing or invalid data
- Clear error messages with context about expected data formats

### Testing Architecture
- **Real EPW Data**: Tests use actual EPW files (San Francisco, Sharm El Sheikh)
- **Fixtures**: `conftest.py` provides shared fixtures for EPW data loading
- **Integration Tests**: `test_integration.py` tests cross-module functionality
- **Unit Tests**: Individual module tests focus on specific functionality

### Key Dependencies
- **ladybug-core**: EPW file reading and weather data structures
- **psychrolib**: Industry-standard psychrometric calculations
- **pvlib**: Solar position and radiation calculations
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computations

## Module-Specific Notes

### EPW Processing (`epw.py`)
- Uses ladybug-core for EPW file parsing
- Converts to pandas DataFrames with explicit column names
- Automatically calculates psychrometric properties
- Handles missing data indicators (999, 9999)

### Wind Analysis (`wind.py`, `wind_analysis.py`)
- `wind.py`: Basic utilities for speed adjustment and direction mapping
- `wind_analysis.py`: Advanced analysis including Weibull fitting and power density
- Both modules handle height adjustments using power law or logarithmic profiles

### Solar Calculations (`solar.py`)
- Uses pvlib for solar position calculations
- Calculates surface irradiation for multiple orientations
- Handles direct, diffuse, and reflected radiation components
- Requires latitude, longitude, and timezone information

### Psychrometric Analysis (`state_point.py`)
- Uses psychrolib for industry-standard calculations
- StatePoint class provides object-oriented interface
- Supports multiple input methods (RH, wet bulb, dew point, humidity ratio)
- Automatic property calculations for all psychrometric variables

### Type Safety (`types.py`)
- Provides TypedDict definitions for DataFrame structures
- Validation functions for required columns
- Column metadata and documentation
- Support for different analysis types (basic, solar, psychrometric)

## Common Development Workflows

### Adding New EPW Columns
1. Update `types.py` with new column definition
2. Modify `epw.py` to process the new column
3. Add validation in relevant analysis modules
4. Update tests with new column expectations

### Adding New Analysis Functions
1. Choose appropriate module based on domain
2. Use explicit DataFrame column names from `types.py`
3. Add input validation using validation functions
4. Write comprehensive tests including edge cases
5. Update module's `__all__` export list

### Working with Real EPW Data
- Use fixtures from `conftest.py` for consistent test data
- San Francisco EPW: temperate oceanic climate
- Sharm El Sheikh EPW: hot desert climate
- Both files provide diverse testing scenarios

## File Locations
- Source code: `src/climate_utils/`
- Tests: `tests/`
- Documentation: `docs/`
- Examples: `examples/`
- Test EPW files: `tests/*.epw`