"""
Example of using get_surface_irradiation_components to analyze solar radiation
components for different orientations.
"""

import pandas as pd
from climate_utils import load_epw_with_location, get_surface_irradiation_components

# Load EPW data with location information
epw_file = "../tests/San_Francisco_Intl_Ap_724940_TMY3.epw"
df_epw, lat, lon, tz = load_epw_with_location(epw_file)

print(f"Location: {lat:.2f}°N, {lon:.2f}°W, UTC{tz:+g}")

# Calculate solar components for cardinal directions
components = get_surface_irradiation_components(
    df_epw,
    orientations=[0, 90, 180, 270],  # N, E, S, W
    surface_tilt=90.0,  # Vertical surfaces
    albedo=0.2,
    latitude=lat,
    longitude=lon,
    timezone=tz,
    sky_model='haydavies'
)

# Print sample data for a specific day (July 1st at noon)
sample_date = '2023-07-01 12:00:00'
if sample_date in components.index:
    print(f"\nSolar radiation components for {sample_date}:")
    print("-" * 60)
    
    for orientation in [0, 90, 180, 270]:
        direction = {0: "North", 90: "East", 180: "South", 270: "West"}[orientation]
        print(f"\n{direction} ({orientation}°):")
        print(f"  Direct:        {components.loc[sample_date, f'{orientation}_direct']:.1f} W/m²")
        print(f"  Sky diffuse:   {components.loc[sample_date, f'{orientation}_sky_diffuse']:.1f} W/m²")
        print(f"  Ground diffuse: {components.loc[sample_date, f'{orientation}_ground_diffuse']:.1f} W/m²")
        print(f"  Global:        {components.loc[sample_date, f'{orientation}_global']:.1f} W/m²")

# Calculate annual totals
print("\nAnnual radiation totals (kWh/m²):")
print("-" * 60)

for orientation in [0, 90, 180, 270]:
    direction = {0: "North", 90: "East", 180: "South", 270: "West"}[orientation]
    
    # Convert from Wh to kWh
    annual_direct = components[f'{orientation}_direct'].sum() / 1000
    annual_sky = components[f'{orientation}_sky_diffuse'].sum() / 1000
    annual_ground = components[f'{orientation}_ground_diffuse'].sum() / 1000
    annual_global = components[f'{orientation}_global'].sum() / 1000
    
    print(f"\n{direction} ({orientation}°):")
    print(f"  Direct:        {annual_direct:7.1f} kWh/m² ({annual_direct/annual_global*100:4.1f}%)")
    print(f"  Sky diffuse:   {annual_sky:7.1f} kWh/m² ({annual_sky/annual_global*100:4.1f}%)")
    print(f"  Ground diffuse: {annual_ground:7.1f} kWh/m² ({annual_ground/annual_global*100:4.1f}%)")
    print(f"  Global:        {annual_global:7.1f} kWh/m²")

# Test different sky models
print("\nComparing sky models for South-facing surface:")
print("-" * 60)

sky_models = ['isotropic', 'haydavies', 'reindl']
model_results = {}

for model in sky_models:
    try:
        result = get_surface_irradiation_components(
            df_epw,
            orientations=[180],  # South only
            surface_tilt=90.0,
            albedo=0.2,
            latitude=lat,
            longitude=lon,
            timezone=tz,
            sky_model=model
        )
        model_results[model] = result['180_sky_diffuse'].sum() / 1000
    except Exception as e:
        print(f"Model {model} failed: {e}")

for model, sky_total in model_results.items():
    print(f"{model:12s}: {sky_total:7.1f} kWh/m² sky diffuse")

# Export sample hourly data
print("\nExporting sample data to CSV...")
sample_data = components[['0_global', '90_global', '180_global', '270_global']].loc['2023-07-01']
sample_data.columns = ['North', 'East', 'South', 'West']
sample_data.to_csv('solar_components_july1.csv')
print("Saved to solar_components_july1.csv")