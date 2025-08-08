# README_AI.md

## Purpose
Climate Utils is a Python package for processing climate data, EnergyPlus Weather (EPW) files, and environmental analysis. It provides wind analysis, solar calculations, and psychrometric computations for building energy modeling and renewable energy assessment.

## Core Concepts
- **EPW DataFrames**: Pandas DataFrames with explicit column names like `'Dry Bulb Temperature (°C)'`
- **StatePoint Objects**: Psychrometric state representation with automatic property calculation
- **Wind Resource Analysis**: Height adjustments, directional mapping, and statistical analysis
- **Solar Irradiation**: Multi-orientation surface calculations using direct/diffuse components
- **Type Safety**: TypedDict definitions for DataFrame validation and column requirements

## Entry Points (API Summary)

### EPW Processing
```python
def load_epw_to_df(epw_file_path: str) -> pd.DataFrame:
    """Load EPW file and return processed DataFrame with explicit columns."""

def load_epw_with_location(epw_file_path: str, year: int = None) -> tuple[pd.DataFrame, float, float, int]:
    """Load EPW and return (DataFrame, latitude, longitude, timezone_offset)."""

def epw_to_df(epw_object) -> pd.DataFrame:
    """Convert ladybug EPW object to DataFrame with enhanced properties."""

def get_epw_location_info(epw_object) -> tuple[float, float, int]:
    """Extract latitude, longitude, timezone from EPW object."""

def get_epw_datetime_index(epw_object, year: int = None) -> pd.DatetimeIndex:
    """Create proper datetime index from EPW data."""

def update_epw_column(epw_object, column_name: str, data_series: pd.Series):
    """Update specific EPW data column with new values."""

def create_blank_epw() -> EPW:
    """Create blank EPW object for custom weather data."""
```

### Wind Analysis
```python
def adjust_wind_speed(wind_speed, ref_height: float, new_height: float, 
                     shear_coef: float = 0.15):
    """Adjust wind speed between heights using power law."""

def analyze_wind_resource(wind_speed, wind_direction, height: float, 
                         target_height: float) -> dict:
    """Comprehensive wind resource analysis with Weibull fitting."""

def map_wind_direction_to_sector(wind_direction, num_sectors: int = 16):
    """Map wind directions to compass sectors."""
```

### Solar Calculations
```python
def get_surface_irradiation_orientations_epw(df_epw: pd.DataFrame, 
                                            orientations: list[float],
                                            latitude: float, longitude: float) -> pd.DataFrame:
    """Calculate solar irradiation for multiple surface orientations."""

def calculate_solar_angles_epw(df_epw: pd.DataFrame, latitude: float = None, 
                              longitude: float = None, timezone: int = None) -> tuple[pd.Series, pd.Series]:
    """Calculate solar zenith and azimuth angles. Returns (zenith, azimuth) series."""
```

### Psychrometric Analysis
```python
class StatePoint:
    def __init__(self, dry_bulb_temp: float, relative_humidity: float = None,
                 wet_bulb_temp: float = None, dew_point_temp: float = None,
                 humidity_ratio: float = None, pressure: float = 101325):
        """Create psychrometric state point from various input combinations."""
    
    @property
    def enthalpy(self) -> float: """Air enthalpy in kJ/kg."""
    @property  
    def specific_volume(self) -> float: """Specific volume in m³/kg."""

def create_state_point_from_epw(df_epw: pd.DataFrame) -> StatePoint:
    """Create StatePoint objects from EPW DataFrame."""
```

### Type Safety & Validation
```python
def validate_epw_dataframe(df: pd.DataFrame, required_columns: list[str] = None):
    """Validate DataFrame has required EPW columns."""

REQUIRED_EPW_COLUMNS = {
    'basic': ['Dry Bulb Temperature (°C)', 'Relative Humidity (%)', ...],
    'solar': ['Direct Normal Radiation (Wh/m²)', ...],
    'psychrometric': ['Atmospheric Station Pressure (Pa)', ...]
}
```

## Minimal Usage Examples

### Basic EPW Processing with Location
```python
from climate_utils import epw, solar, state_point

# Load EPW with location info
df, lat, lon, tz = epw.load_epw_with_location('weather.epw')

# Calculate solar angles for the site
zenith, azimuth = solar.calculate_solar_angles_epw(df, lat, lon, tz)
print(f"Max solar elevation: {90 - zenith.min():.1f}°")

# Create psychrometric state points
states = state_point.create_state_point_from_epw(df)
print(f"Mean enthalpy: {states.enthalpy.mean():.1f} kJ/kg")
```

### Wind Resource Analysis
```python
from climate_utils import wind_analysis

results = wind_analysis.analyze_wind_resource(
    wind_speed=df['Wind Speed (m/s)'],
    wind_direction=df['Wind Direction (°)'],
    height=10.0, target_height=80.0
)
print(f"Power density: {results['power_density']:.1f} W/m²")
```

### Solar Analysis with Angles
```python
from climate_utils import epw, solar

# Load EPW with location
df, lat, lon, tz = epw.load_epw_with_location('weather.epw')

# Calculate solar angles and surface irradiation
zenith, azimuth = solar.calculate_solar_angles_epw(df, lat, lon, tz)
solar_data = solar.get_surface_irradiation_orientations_epw(
    df, orientations=[180], latitude=lat, longitude=lon
)
print(f"Annual south irradiation: {solar_data['surface_irradiation_180'].sum():.0f} Wh/m²")
```

## Dependencies
- **ladybug-core**: EPW file processing
- **psychrolib**: ASHRAE psychrometric calculations  
- **pvlib**: Solar position and radiation modeling
- **pandas**: DataFrame operations
- **numpy**: Numerical computations