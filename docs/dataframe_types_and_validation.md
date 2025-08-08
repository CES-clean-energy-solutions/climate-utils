# DataFrame Types and Validation

This document explains how to document and enforce DataFrame column types and required columns in the `climate-utils` package.

## Overview

The `climate-utils` package uses several approaches to ensure type safety and data validation:

1. **Type Hints with TypedDict** - Define expected DataFrame structures
2. **Runtime Validation** - Check DataFrame columns at runtime
3. **Documentation** - Clear documentation of expected column names and types
4. **Testing** - Comprehensive tests to ensure validation works correctly

## 1. Type Definitions with TypedDict

### Basic Type Definition

```python
from typing import TypedDict
import pandas as pd

class EPWDataFrame(TypedDict):
    """Type definition for EPW DataFrame columns."""
    'Dry Bulb Temperature (°C)': pd.Series[float]
    'Relative Humidity (%)': pd.Series[float]
    'Wind Speed (m/s)': pd.Series[float]
    'Wind Direction (°)': pd.Series[float]
    'Direct Normal Radiation (Wh/m²)': pd.Series[float]
    'Diffuse Horizontal Radiation (Wh/m²)': pd.Series[float]
    'Global Horizontal Radiation (Wh/m²)': pd.Series[float]
```

### Specialized Type Definitions

```python
# For specific analysis types
EPWDataFrameBasic = TypedDict('EPWDataFrameBasic', {
    'Dry Bulb Temperature (°C)': pd.Series[float],
    'Relative Humidity (%)': pd.Series[float],
    'Wind Speed (m/s)': pd.Series[float],
    'Wind Direction (°)': pd.Series[float],
})

EPWDataFrameSolar = TypedDict('EPWDataFrameSolar', {
    'Direct Normal Radiation (Wh/m²)': pd.Series[float],
    'Diffuse Horizontal Radiation (Wh/m²)': pd.Series[float],
    'Global Horizontal Radiation (Wh/m²)': pd.Series[float],
})
```

## 2. Required Column Definitions

### Define Required Columns by Analysis Type

```python
REQUIRED_EPW_COLUMNS = {
    'basic': [
        'Dry Bulb Temperature (°C)',
        'Relative Humidity (%)',
        'Wind Speed (m/s)',
        'Wind Direction (°)',
    ],
    'solar': [
        'Direct Normal Radiation (Wh/m²)',
        'Diffuse Horizontal Radiation (Wh/m²)',
        'Global Horizontal Radiation (Wh/m²)',
    ],
    'psychrometric': [
        'Dry Bulb Temperature (°C)',
        'Relative Humidity (%)',
        'Atmospheric Station Pressure (Pa)',
    ],
    'wind_analysis': [
        'Wind Speed (m/s)',
        'Wind Direction (°)',
    ],
}
```

## 3. Runtime Validation Functions

### Basic Validation

```python
def validate_epw_dataframe(df: pd.DataFrame, required_columns: list[str] = None) -> None:
    """
    Validate that a DataFrame has the required EPW columns.

    Args:
        df: DataFrame to validate
        required_columns: List of required column names. If None, uses 'basic' columns.

    Raises:
        ValueError: If required columns are missing
        TypeError: If DataFrame is not a pandas DataFrame
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(df)}")

    if required_columns is None:
        required_columns = REQUIRED_EPW_COLUMNS['basic']

    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}. "
            f"Available columns: {list(df.columns)}"
        )
```

### Advanced Validation with Type Checking

```python
def validate_epw_dataframe_types(df: pd.DataFrame, column_info: dict) -> None:
    """
    Validate DataFrame column types.

    Args:
        df: DataFrame to validate
        column_info: Dictionary with column type information
    """
    for column, info in column_info.items():
        if column in df.columns:
            expected_type = info['type']
            if expected_type == 'float':
                if not pd.api.types.is_numeric_dtype(df[column]):
                    raise TypeError(f"Column {column} should be numeric, got {df[column].dtype}")
            elif expected_type == 'int':
                if not pd.api.types.is_integer_dtype(df[column]):
                    raise TypeError(f"Column {column} should be integer, got {df[column].dtype}")
```

## 4. Using Type Hints in Functions

### Function with Type Hints and Validation

```python
from typing import Dict, List, Optional
import pandas as pd
from .types import validate_epw_dataframe, REQUIRED_EPW_COLUMNS

def get_surface_irradiation_orientations_epw(
    df_epw: pd.DataFrame,
    orientations: Optional[List[float]] = None,
    albedo: float = 0.2,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    timezone: Optional[int] = None
) -> Dict[str, pd.Series]:
    """
    Calculate surface irradiation for different orientations from EPW data.

    Parameters:
    -----------
    df_epw : pd.DataFrame
        EPW weather data with columns for direct normal, diffuse horizontal,
        and global horizontal radiation. Must contain:
        - 'Direct Normal Radiation (Wh/m²)'
        - 'Diffuse Horizontal Radiation (Wh/m²)'
        - 'Global Horizontal Radiation (Wh/m²)'
    orientations : List[float], optional
        List of surface orientations in degrees (0 = North, 90 = East, etc.)
        Default: [0, 90, 180, 270] (N, E, S, W)
    albedo : float, default 0.2
        Ground albedo (reflectance)
    latitude : float, optional
        Site latitude in degrees. If None, will try to extract from EPW data
    longitude : float, optional
        Site longitude in degrees. If None, will try to extract from EPW data
    timezone : int, optional
        Site timezone offset in hours. If None, will try to extract from EPW data

    Returns:
    --------
    Dict[str, pd.Series]
        Dictionary with orientation angles as keys and irradiation series as values

    Raises:
    -------
    ValueError
        If required solar radiation columns are missing from the DataFrame
    """
    # Validate that the DataFrame has the required solar columns
    validate_epw_dataframe(df_epw, REQUIRED_EPW_COLUMNS['solar'])

    # Extract radiation data directly using exact column names
    dni = df_epw['Direct Normal Radiation (Wh/m²)']
    dhi = df_epw['Diffuse Horizontal Radiation (Wh/m²)']
    ghi = df_epw['Global Horizontal Radiation (Wh/m²)']

    # ... rest of function implementation
```

## 5. Column Information Documentation

### Comprehensive Column Documentation

```python
def get_epw_column_info() -> dict[str, dict[str, str]]:
    """
    Get information about EPW DataFrame columns.

    Returns:
        Dictionary mapping column names to their descriptions and units.
    """
    return {
        'Dry Bulb Temperature (°C)': {
            'description': 'Ambient air temperature',
            'unit': '°C',
            'type': 'float',
            'required': True
        },
        'Relative Humidity (%)': {
            'description': 'Relative humidity as percentage',
            'unit': '%',
            'type': 'float',
            'required': True
        },
        'Wind Speed (m/s)': {
            'description': 'Wind speed at measurement height',
            'unit': 'm/s',
            'type': 'float',
            'required': True
        },
        'Direct Normal Radiation (Wh/m²)': {
            'description': 'Direct normal solar radiation',
            'unit': 'Wh/m²',
            'type': 'float',
            'required': False
        },
        # ... more columns
    }
```

## 6. Testing DataFrame Validation

### Test Validation Functions

```python
import pytest
import pandas as pd

def test_validate_epw_dataframe_basic():
    """Test basic DataFrame validation."""
    # Valid DataFrame
    df_valid = pd.DataFrame({
        'Dry Bulb Temperature (°C)': [20.0, 25.0],
        'Relative Humidity (%)': [50.0, 60.0],
        'Wind Speed (m/s)': [2.0, 3.0],
        'Wind Direction (°)': [180.0, 270.0],
    })

    # Should not raise any exception
    validate_epw_dataframe(df_valid)

    # Invalid DataFrame - missing required column
    df_invalid = pd.DataFrame({
        'Dry Bulb Temperature (°C)': [20.0, 25.0],
        'Relative Humidity (%)': [50.0, 60.0],
        # Missing 'Wind Speed (m/s)' and 'Wind Direction (°)'
    })

    # Should raise ValueError
    with pytest.raises(ValueError, match="Missing required columns"):
        validate_epw_dataframe(df_invalid)

def test_validate_epw_dataframe_solar():
    """Test solar-specific DataFrame validation."""
    # Valid solar DataFrame
    df_solar = pd.DataFrame({
        'Direct Normal Radiation (Wh/m²)': [800.0, 900.0],
        'Diffuse Horizontal Radiation (Wh/m²)': [200.0, 150.0],
        'Global Horizontal Radiation (Wh/m²)': [1000.0, 1050.0],
    })

    # Should not raise any exception
    validate_epw_dataframe(df_solar, REQUIRED_EPW_COLUMNS['solar'])

    # Invalid solar DataFrame
    df_invalid_solar = pd.DataFrame({
        'Direct Normal Radiation (Wh/m²)': [800.0, 900.0],
        # Missing diffuse and global radiation
    })

    # Should raise ValueError
    with pytest.raises(ValueError, match="Missing required columns"):
        validate_epw_dataframe(df_invalid_solar, REQUIRED_EPW_COLUMNS['solar'])
```

## 7. Best Practices

### 1. Use Exact Column Names

Always use the exact column names as they appear in the DataFrame:

```python
# ✅ Good - Direct column access
dni = df_epw['Direct Normal Radiation (Wh/m²)']
temp = df_epw['Dry Bulb Temperature (°C)']

# ❌ Bad - Don't use loops or alternative names
for col in df_epw.columns:
    if 'direct' in col.lower():
        dni = df_epw[col]
```

### 2. Validate Early

Validate DataFrame structure at the beginning of functions:

```python
def my_function(df_epw: pd.DataFrame) -> pd.Series:
    # Validate first
    validate_epw_dataframe(df_epw, REQUIRED_EPW_COLUMNS['basic'])

    # Then use the data
    temp = df_epw['Dry Bulb Temperature (°C)']
    # ... rest of function
```

### 3. Document Required Columns

Always document required columns in function docstrings:

```python
def my_function(df_epw: pd.DataFrame) -> pd.Series:
    """
    Process EPW data.

    Parameters:
    -----------
    df_epw : pd.DataFrame
        EPW weather data. Must contain:
        - 'Dry Bulb Temperature (°C)'
        - 'Relative Humidity (%)'

    Returns:
    --------
    pd.Series
        Processed data
    """
```

### 4. Use Type Hints

Use type hints to make your code more readable and enable better IDE support:

```python
from typing import Dict, List, Optional
from .types import EPWDataFrameBasic

def process_basic_weather(df_epw: pd.DataFrame) -> Dict[str, float]:
    """Process basic weather data."""
    validate_epw_dataframe(df_epw, REQUIRED_EPW_COLUMNS['basic'])
    # ... implementation
```

## 8. Integration with MyPy

### MyPy Configuration

Add to your `pyproject.toml`:

```toml
[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
check_untyped_defs = true
```

### Running MyPy

```bash
# Check type hints
mypy src/climate_utils/

# Check with strict settings
mypy --strict src/climate_utils/
```

## 9. Example Usage

### Complete Example

```python
import pandas as pd
from climate_utils import (
    load_epw_to_df,
    validate_epw_dataframe,
    REQUIRED_EPW_COLUMNS,
    get_surface_irradiation_orientations_epw
)

# Load EPW data
df_epw = load_epw_to_df('weather.epw')

# Validate basic structure
validate_epw_dataframe(df_epw, REQUIRED_EPW_COLUMNS['basic'])

# Use for solar analysis (validates solar columns internally)
solar_results = get_surface_irradiation_orientations_epw(df_epw)

# Access validated data
temperature = df_epw['Dry Bulb Temperature (°C)']
humidity = df_epw['Relative Humidity (%)']
```

This approach ensures that:

1. **Type Safety**: MyPy can catch type errors at development time
2. **Runtime Validation**: Functions fail fast with clear error messages
3. **Documentation**: Clear documentation of expected data structures
4. **Testing**: Comprehensive tests ensure validation works correctly
5. **Maintainability**: Easy to update column requirements and validation rules