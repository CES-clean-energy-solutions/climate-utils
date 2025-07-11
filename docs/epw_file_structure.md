# EPW File Structure and Column Mappings

## Overview

EnergyPlus Weather (EPW) files contain hourly weather data for building energy simulations. This document explains the structure of EPW files and how ladybug-core processes them.

## EPW File Format

EPW files are CSV-formatted files with specific header sections followed by hourly data. The file structure is:

1. **Header Section** (lines 1-8): Location, design conditions, ground temperatures, etc.
2. **Data Section** (line 9+): Hourly weather data with 35 columns

## Header Section Structure

### Line 1: LOCATION
```
LOCATION,San.Francisco.Intl.AP,CA,USA,SRC-TMYx,724940,37.62000,-122.3650,-8.0,5.0
```
- Location name, state, country, data source, WMO number, latitude, longitude, timezone, elevation

### Line 2: DESIGN CONDITIONS
Contains heating and cooling design day information

### Line 3: TYPICAL/EXTREME PERIODS
Defines typical and extreme weather weeks

### Line 4: GROUND TEMPERATURES
Monthly ground temperature data at different depths

### Line 5: HOLIDAYS/DAYLIGHT SAVINGS
Daylight saving time information

### Line 6: COMMENTS 1
Additional information about the weather data

### Line 7: COMMENTS 2
More comments about the weather data

### Line 8: DATA PERIODS
Defines the data period and format

## Data Section Structure

The data section contains hourly weather data with exactly 35 columns (fields 0-34). Each row represents one hour of weather data.

### Column Mappings (Field Numbers)

| Field | Column Name | Type | Unit | Description | Missing Value | Climate Utils DataFrame Column |
|:-----:|-------------|:----:|:----:|-------------|:-------------:|-------------------------------|
| 0 | Year | int | yr | Year | - | - |
| 1 | Month | int | mon | Month (1-12) | - | - |
| 2 | Day | int | day | Day of month (1-31) | - | - |
| 3 | Hour | int | hr | Hour (1-24) | - | - |
| 4 | Minute | int | min | Minute (0-59) | - | - |
| 5 | Uncertainty Flags | str | flag | Data quality flags | - | - |
| 6 | Dry Bulb Temperature | float | °C | Air temperature | 99.9 | `Dry Bulb Temperature (°C)` |
| 7 | Dew Point Temperature | float | °C | Dew point temperature | 99.9 | `Dew Point Temperature (°C)` |
| 8 | Relative Humidity | int | % | Relative humidity (0-110%) | 999 | `Relative Humidity (%)` |
| 9 | Atmospheric Station Pressure | int | Pa | Barometric pressure | 999999 | `Atmospheric Pressure (Pa)` |
| 10 | Extraterrestrial Horizontal Radiation | int | Wh/m² | Solar radiation at top of atmosphere | 9999 | - |
| 11 | Extraterrestrial Direct Normal Radiation | int | Wh/m² | Direct solar at top of atmosphere | 9999 | - |
| 12 | Horizontal Infrared Radiation Intensity | int | W/m² | Infrared radiation from sky | 9999 | - |
| 13 | Global Horizontal Radiation | int | Wh/m² | Total horizontal solar radiation | 9999 | `Global Horizontal Radiation (Wh/m²)` |
| 14 | Direct Normal Radiation | int | Wh/m² | Direct beam solar radiation | 9999 | `Direct Normal Radiation (Wh/m²)` |
| 15 | Diffuse Horizontal Radiation | int | Wh/m² | Diffuse sky radiation | 9999 | `Diffuse Horizontal Radiation (Wh/m²)` |
| 16 | Global Horizontal Illuminance | int | lux | Total horizontal illuminance | 999999 | - |
| 17 | Direct Normal Illuminance | int | lux | Direct beam illuminance | 999999 | - |
| 18 | Diffuse Horizontal Illuminance | int | lux | Diffuse sky illuminance | 999999 | - |
| 19 | Zenith Luminance | int | cd/m² | Sky brightness at zenith | 9999 | - |
| 20 | Wind Direction | int | degrees | Wind direction (0-360°) | 999 | `Wind Direction (°)` |
| 21 | Wind Speed | float | m/s | Wind speed | 999 | `Wind Speed (m/s)` |
| 22 | Total Sky Cover | int | tenths | Total cloud cover (0-10) | 99 | `Sky Cover (Total) (tenths)` |
| 23 | Opaque Sky Cover | int | tenths | Opaque cloud cover (0-10) | 99 | `Sky Cover (Opaque) (tenths)` |
| 24 | Visibility | float | km | Visibility | 9999 | `Visibility (km)` |
| 25 | Ceiling Height | int | m | Cloud ceiling height | 99999 | `Ceiling Height (m)` |
| 26 | Present Weather Observation | int | code | Weather observation code | 9 | - |
| 27 | Present Weather Codes | int | code | Weather codes | 999999999 | - |
| 28 | Precipitable Water | int | mm | Atmospheric water content | 999 | `Precipitable Water (mm)` |
| 29 | Aerosol Optical Depth | float | - | Atmospheric clarity | 999 | - |
| 30 | Snow Depth | int | cm | Snow depth on ground | 999 | `Snow Depth (cm)` |
| 31 | Days Since Last Snowfall | int | days | Days since snow | 99 | - |
| 32 | Albedo | float | - | Ground reflectivity | 999 | - |
| 33 | Liquid Precipitation Depth | float | mm | Rainfall amount | 999 | - |
| 34 | Liquid Precipitation Quantity | float | - | Rainfall intensity | 99 | - |

## Ladybug-Core EPW Object Structure

### Data Access Methods

Ladybug-core provides properties to access each weather field:

```python
import ladybug.epw

# Load EPW file
epw = ladybug.epw.EPW('path/to/file.epw')

# Access weather data
dry_bulb_temp = epw.dry_bulb_temperature  # Field 6
relative_humidity = epw.relative_humidity  # Field 8
wind_speed = epw.wind_speed  # Field 21
wind_direction = epw.wind_direction  # Field 20
direct_normal_radiation = epw.direct_normal_radiation  # Field 14
diffuse_horizontal_radiation = epw.diffuse_horizontal_radiation  # Field 15
global_horizontal_radiation = epw.global_horizontal_radiation  # Field 13
```

### Data Structure

Each property returns a `HourlyContinuousCollection` object containing:
- Values: The actual weather data
- Datetimes: Corresponding timestamps
- Header: Metadata about the data type and units

### Field Access by Number

You can also access any field by its number:

```python
# Access any field by number (0-34)
field_6_data = epw._get_data_by_field(6)  # Dry bulb temperature
field_8_data = epw._get_data_by_field(8)  # Relative humidity
```

## Column Name Mappings

### Ladybug Property Names vs EPW Column Names vs Climate Utils DataFrame Columns

| Ladybug Property | EPW Field | EPW Column Name | Climate Utils DataFrame Column | Description |
|:----------------:|:---------:|-----------------|:-------------------------------|:------------|
| `dry_bulb_temperature` | 6 | Dry Bulb Temperature | `Dry Bulb Temperature (°C)` | Air temperature in °C |
| `dew_point_temperature` | 7 | Dew Point Temperature | `Dew Point Temperature (°C)` | Dew point in °C |
| `relative_humidity` | 8 | Relative Humidity | `Relative Humidity (%)` | RH in % |
| `atmospheric_station_pressure` | 9 | Atmospheric Station Pressure | `Atmospheric Pressure (Pa)` | Pressure in Pa |
| `global_horizontal_radiation` | 13 | Global Horizontal Radiation | `Global Horizontal Radiation (Wh/m²)` | Total horizontal solar in Wh/m² |
| `direct_normal_radiation` | 14 | Direct Normal Radiation | `Direct Normal Radiation (Wh/m²)` | Direct beam solar in Wh/m² |
| `diffuse_horizontal_radiation` | 15 | Diffuse Horizontal Radiation | `Diffuse Horizontal Radiation (Wh/m²)` | Diffuse sky solar in Wh/m² |
| `wind_direction` | 20 | Wind Direction | `Wind Direction (°)` | Wind direction in degrees |
| `wind_speed` | 21 | Wind Speed | `Wind Speed (m/s)` | Wind speed in m/s |
| `total_sky_cover` | 22 | Total Sky Cover | `Sky Cover (Total) (tenths)` | Cloud cover in tenths |
| `opaque_sky_cover` | 23 | Opaque Sky Cover | `Sky Cover (Opaque) (tenths)` | Opaque cloud cover in tenths |
| `visibility` | 24 | Visibility | `Visibility (km)` | Visibility in km |
| `ceiling_height` | 25 | Ceiling Height | `Ceiling Height (m)` | Cloud ceiling height in m |
| `precipitable_water` | 28 | Precipitable Water | `Precipitable Water (mm)` | Atmospheric water content in mm |
| `snow_depth` | 30 | Snow Depth | `Snow Depth (cm)` | Snow depth in cm |

## Data Validation

### Missing Values
Each field has specific missing value indicators:
- Temperature fields: 99.9
- Humidity: 999
- Pressure: 999999
- Radiation: 9999
- Wind: 999
- Sky cover: 99

### Value Ranges
- Temperature: -70°C to 70°C
- Humidity: 0% to 110%
- Wind direction: 0° to 360°
- Wind speed: 0 to 40 m/s
- Sky cover: 0 to 10 tenths

## Integration with Climate Utils

The `climate_utils.epw` module provides functions to:
1. Load EPW files using ladybug-core
2. Convert EPW data to pandas DataFrames
3. Add calculated psychrometric properties
4. Map wind directions to sectors
5. Process weather data for analysis

### Climate Utils DataFrame Structure

The `epw_to_df()` function creates a DataFrame with the following columns:

#### Original EPW Data Columns
- `Dry Bulb Temperature (°C)` - Air temperature
- `Dew Point Temperature (°C)` - Dew point temperature
- `Relative Humidity (%)` - Relative humidity (0-100%)
- `Atmospheric Pressure (Pa)` - Barometric pressure
- `Global Horizontal Radiation (Wh/m²)` - Total horizontal solar radiation
- `Direct Normal Radiation (Wh/m²)` - Direct beam solar radiation
- `Diffuse Horizontal Radiation (Wh/m²)` - Diffuse sky radiation
- `Wind Direction (°)` - Wind direction (0-360°)
- `Wind Speed (m/s)` - Wind speed
- `Sky Cover (Total) (tenths)` - Total cloud cover (0-10)
- `Sky Cover (Opaque) (tenths)` - Opaque cloud cover (0-10)
- `Precipitable Water (mm)` - Atmospheric water content
- `Snow Depth (cm)` - Snow depth on ground
- `Visibility (km)` - Visibility
- `Ceiling Height (m)` - Cloud ceiling height

#### Calculated Psychrometric Properties
- `Humidity Ratio (g/kg)` - Calculated humidity ratio
- `Enthalpy (J/kg)` - Calculated air enthalpy

#### Wind Analysis Columns
- `Sector` - Wind direction mapped to 16 compass sectors (1-16)
- `2 Sector` - Wind direction mapped to 2 sectors ('N', 'S')

#### Index
- **Datetime Index**: Hourly timestamps starting from "2023-01-01 00:00" for 8760 hours

### Example Usage

```python
from climate_utils import epw

# Load EPW file and convert to DataFrame
df = epw.load_epw_to_df('path/to/file.epw')

# Access weather data using exact column names
temp = df['Dry Bulb Temperature (°C)']
humidity = df['Relative Humidity (%)']
wind_speed = df['Wind Speed (m/s)']
wind_direction = df['Wind Direction (°)']

# Access calculated properties
humidity_ratio = df['Humidity Ratio (g/kg)']
enthalpy = df['Enthalpy (J/kg)']
wind_sectors = df['Sector']

# DataFrame has 8760 rows (one per hour) and datetime index
print(f"DataFrame shape: {df.shape}")  # (8760, 17)
print(f"Date range: {df.index[0]} to {df.index[-1]}")
```

## Common Issues and Solutions

### Column Name Mismatches
- **Issue**: Code expects "friendly" column names but ladybug uses different property names
- **Solution**: Use ladybug property names or create mapping functions

### Missing Data Handling
- **Issue**: EPW files may contain missing values (999, 99.9, etc.)
- **Solution**: Filter out missing values or replace with appropriate defaults

### Data Type Conversions
- **Issue**: Some fields are integers in EPW but floats in ladybug
- **Solution**: Use ladybug's data access methods which handle conversions automatically

## References

- [EnergyPlus Weather File Data Dictionary](https://bigladdersoftware.com/epx/docs/9-6/auxiliary-programs/energyplus-weather-file-epw-data-dictionary.html)
- [Ladybug-Core EPW Documentation](https://www.ladybug.tools/ladybug-core/docs/ladybug.epw.html)
- [EPW File Format Specification](https://energyplus.net/weather)