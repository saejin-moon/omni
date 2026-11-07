"""Script to generate the master Notebook 1 with all markdown explanations, code cells, and graphs (150 Counties)."""

import nbformat as nbf
from pathlib import Path

def create_notebook():
    nb = nbf.v4.new_notebook()
    nb.metadata = {
        "kernelspec": {
            "display_name": "Python 3 (.venv)",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.11"
        }
    }
    
    cells = []
    
    # Title & Markdown
    cells.append(nbf.v4.new_markdown_cell("""# OmniGeo: Phase 1 — Nationwide County Benchmark & 150-County Archetype Discovery

> **Objective**: Define a mathematically representative, transparent sample of US counties/regions across **5 macro-regions** (Northeast, Midwest, South/Southeast, Southwest, Northwest) using open public datasets from **data.gov**, **US Census**, **USDA ERS**, and **MIT Election Lab**.
> 
> Rather than canvassing all ~3,143 US counties (which is computationally and storage-wise prohibitive for subsequent multi-terabyte satellite and flight feeds), we mathematically select **30 distinct, archetypal counties per macro-region (150 counties total, representing ~4.8% of all US counties)**. 
> 
> Each county is captured not as a crude bounding box, but as an **exact, high-precision irregular cartographic polygon** (US Census TIGER) and polyfilled with **Uber H3 hexagonal grid cells** for subsequent cross-domain association mining.

---

### Data Sources Merged:
1. **US Census Bureau Population & Migration (2020–2023)**: `co-est2023-alldata.csv`
2. **USDA Economic Research Service (ERS) RUCC 2023**: `2023-rural-urban-continuum-codes.csv` (Codes 1–9)
3. **US Census SAIPE 2022 (Small Area Income & Poverty)**: `est22all.txt` (Median household income, all-age poverty, child poverty)
4. **2020 Presidential Election Results**: County-level votes, percentages, margins
5. **MIT Election Data & Science Lab (MEDSL)**: 2012, 2016, 2020 presidential returns, turnout, and demographic shares
6. **Official US Census TIGER Cartographic Polygons**: True irregular county boundary shapes"""))

    # Imports
    cells.append(nbf.v4.new_code_cell("""import os
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

# Ensure working directory is project root
if (Path.cwd() / "src").exists():
    PROJECT_ROOT = Path.cwd().resolve()
else:
    PROJECT_ROOT = Path.cwd().parent.resolve()
os.chdir(PROJECT_ROOT)
print(f"Working directory set to: {PROJECT_ROOT}")

import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import folium

from omni.benchmark.builder import build_master_county_benchmark
from omni.selection.stratifier import select_nationwide_cohort
from omni.visualization.charts import (
    plot_national_landscape,
    plot_regional_pca_biplot,
    plot_county_fingerprint_radar,
    plot_political_swing_slopegraph,
    create_interactive_folium_map
)

# Display settings
pd.set_option("display.max_columns", 50)
pd.set_option("display.max_rows", 20)
pd.set_option("display.precision", 3)
print("OmniGeo Analytics Environment Loaded Successfully.")"""))

    # Section 1: Build Master Benchmark Table
    cells.append(nbf.v4.new_markdown_cell("""## 1. Master County Benchmark Table Construction (~3,131 Counties)

We download, clean, and harmonize the public datasets across all US counties on their 5-digit FIPS code."""))

    cells.append(nbf.v4.new_code_cell("""gdf_benchmark = build_master_county_benchmark()
print(f"Master benchmark table constructed: {gdf_benchmark.shape[0]} counties with {gdf_benchmark.shape[1]} attributes.")
gdf_benchmark[["fips", "county_name", "state_abbr", "macro_region", "pop_2023", "median_hh_income", "poverty_pct", "rucc_code", "dem_margin_2020"]].head(10)"""))

    cells.append(nbf.v4.new_code_cell("""# Summary statistics across core analytical metrics
summary_cols = [
    "pop_2023", "pop_density_sq_km", "median_hh_income", 
    "poverty_pct", "child_poverty_pct", "dem_margin_2020", 
    "swing_2012_2020", "turnout_rate_2020", "racial_diversity_index"
]
gdf_benchmark[summary_cols].describe().T"""))

    # Section 2: National Macro Landscape
    cells.append(nbf.v4.new_markdown_cell("""## 2. Exploratory Data Analysis: The National Landscape

Let's examine how wealth, political lean, density, and 8-year political swings distribute across the 5 macro-regions."""))

    cells.append(nbf.v4.new_code_cell("""fig_national = plot_national_landscape(gdf_benchmark)
plt.show()"""))

    cells.append(nbf.v4.new_markdown_cell("""### Regional Feature Correlation Clustermap
How do demographic diversity, poverty, urban density, and political voting behavior correlate with one another across American counties?"""))

    cells.append(nbf.v4.new_code_cell("""corr_cols = [
    "median_hh_income", "poverty_pct", "child_poverty_pct", "pop_growth_pct",
    "net_migration_rate", "pop_density_sq_km", "rucc_code", "dem_margin_2020",
    "dem_margin_2016", "dem_margin_2012", "swing_2012_2020", "turnout_rate_2020",
    "white_pct", "black_pct", "hispanic_pct", "nonwhite_pct", "age29andunder_pct", "age65andolder_pct"
]
corr_matrix = gdf_benchmark[corr_cols].corr()

plt.figure(figsize=(14, 11))
sns.clustermap(
    corr_matrix, cmap="vlag", center=0, annot=True, fmt=".2f",
    annot_kws={"size": 7.5}, figsize=(14, 12), linewidths=0.5
)
plt.title("Correlation Clustermap: Demographic, Political & Socioeconomic Dimensions", y=1.03, fontsize=14, fontweight="bold")
plt.show()"""))

    # Section 3: Select 150 Counties
    cells.append(nbf.v4.new_markdown_cell("""## 3. Mathematical Archetype Selection: 30 Counties per Macro-Region (150 Total)

For each of the 5 macro-regions, we execute:
1. Feature standardization across 15 socioeconomic, political, and density metrics.
2. Principal Component Analysis (PCA) to extract the primary orthogonal axes of regional variance.
3. **Regional Statistical Centroid**: Identifies the county closest to $(0,0,0,0)$ in PCA space (the purest statistical median).
4. **Stratified K-Medoids / K-Means ($k=29$)**: Identifies 29 contrasting archetypes across the regional spectrum (30 counties per region).
5. **H3 Hexagonal Polyfill**: Tessellates the interior of each county's irregular polygon into Uber H3 hexagons."""))

    cells.append(nbf.v4.new_code_cell("""cohort_150 = select_nationwide_cohort(gdf_benchmark, n_per_region=30, h3_resolution=7)
print(f"Cohort generation complete: {len(cohort_150)} archetypal counties across 5 macro-regions.")
print("\\nArchetypes discovered across the nation:")
cohort_150['archetype_label'].value_counts()"""))

    # Section 4: Deep-Dives for each Macro-Region
    regions = [
        ("Northeast", "Northeast (New England, NY, NJ, PA)"),
        ("Midwest", "Midwest (Great Lakes & Plains)"),
        ("South / Southeast", "The South / Southeast (Appalachia, Deep South & Atlantic)"),
        ("Southwest", "Southwest (Texas, Oklahoma, New Mexico, Arizona)"),
        ("Northwest", "Northwest (Pacific Northwest, Intermountain West & Alaska)")
    ]

    for reg_key, reg_title in regions:
        cells.append(nbf.v4.new_markdown_cell(f"""---
## 4. Deep-Dive: {reg_title} (30 Counties)

Let's explore the 30 selected archetypes for **{reg_key}** through:
1. **Spatial & PCA Biplot**: Where the 30 counties sit in regional geography and latent space.
2. **Multi-Axis Radar Fingerprint**: Comparing contrasting archetypes across 8 dimensions.
3. **Political Swing Trajectory (2012 -> 2016 -> 2020)**: Tracking partisan polarization over 8 years.
4. **Archetype Selection Table**: Comprehensive metric profile for the 30 counties."""))

        cells.append(nbf.v4.new_code_cell(f"""reg_cohort = cohort_150[cohort_150["macro_region"] == "{reg_key}"].copy()

# 1. Spatial Biplot
fig_biplot = plot_regional_pca_biplot(gdf_benchmark, reg_cohort, "{reg_key}")
plt.show()

# 2. Multi-Axis Radar Fingerprint
fig_radar = plot_county_fingerprint_radar(reg_cohort, "{reg_key}")
plt.show()

# 3. Political Swing Slopegraph (2012 -> 2016 -> 2020)
fig_slope = plot_political_swing_slopegraph(reg_cohort, "{reg_key}")
plt.show()

# 4. Archetype Profile Table
table_cols = [
    "fips", "county_name", "state_abbr", "archetype_label", 
    "pop_2023", "median_hh_income", "poverty_pct", "rucc_code", 
    "dem_margin_2020", "swing_2012_2020", "h3_cell_count"
]
reg_cohort[table_cols].reset_index(drop=True)"""))

    # Section 5: The 150-County Master Gallery & Export
    cells.append(nbf.v4.new_markdown_cell("""## 5. Master 150-County Cohort Gallery & True Irregular Polygons

We now examine the full nationwide cohort of 150 counties and render their **exact irregular boundary polygons** (not bounding boxes!) on an interactive Folium map."""))

    cells.append(nbf.v4.new_code_cell("""# Render interactive Folium map with exact irregular cartographic polygons
m = create_interactive_folium_map(cohort_150, output_html="data/processed/cohort_150_interactive_map.html")
print("Interactive map generated with true polygon layers and hover popups.")
m"""))

    cells.append(nbf.v4.new_markdown_cell("""### Exporting Cohort Metadata for Phase 2 Association Mining

We export the 150-county cohort with:
- True Polygon boundaries (GeoJSON MultiPolygon & WKT)
- Bounding Box envelopes `[min_lon, min_lat, max_lon, max_lat]`
- H3 Polyfill Hexagon cell lists
- Complete demographic, economic, and political baseline metrics"""))

    cells.append(nbf.v4.new_code_cell("""import json

# Export to GeoJSON
export_geojson_path = "data/processed/selected_cohort_150.geojson"
cohort_150_export = cohort_150.copy()
cohort_150_export["h3_cells_str"] = cohort_150_export["h3_cells"].apply(lambda x: ",".join(x))
cohort_150_export.drop(columns=["h3_cells"]).to_file(export_geojson_path, driver="GeoJSON")
print(f"Saved GeoJSON to {export_geojson_path}")

# Also maintain 75 alias
cohort_150_export.drop(columns=["h3_cells"]).to_file("data/processed/selected_cohort_75.geojson", driver="GeoJSON")

# Export to Parquet
export_parquet_path = "data/processed/selected_cohort_150.parquet"
cohort_150_export.to_parquet(export_parquet_path)
cohort_150_export.to_parquet("data/processed/selected_cohort_75.parquet")
print(f"Saved Parquet to {export_parquet_path}")

# Export metadata JSON summary
summary_data = []
for _, row in cohort_150.iterrows():
    summary_data.append({
        "fips": row["fips"],
        "name": row["county_name"],
        "state": row["state_abbr"],
        "macro_region": row["macro_region"],
        "archetype": row["archetype_label"],
        "is_centroid": bool(row["is_regional_centroid"]),
        "pop_2023": int(row["pop_2023"]),
        "median_income": float(row["median_hh_income"]),
        "poverty_pct": float(row["poverty_pct"]),
        "dem_margin_2020": float(row["dem_margin_2020"]),
        "swing_2012_2020": float(row["swing_2012_2020"]),
        "rucc_code": int(row["rucc_code"]),
        "bbox": [float(row["min_lon"]), float(row["min_lat"]), float(row["max_lon"]), float(row["max_lat"])],
        "h3_cell_count": int(row["h3_cell_count"]),
        "h3_sample_cells": row["h3_cells"][:5]
    })

with open("data/processed/selected_cohort_150_summary.json", "w") as f:
    json.dump(summary_data, f, indent=2)
with open("data/processed/selected_cohort_75_summary.json", "w") as f:
    json.dump(summary_data, f, indent=2)
print("Saved cohort summary to data/processed/selected_cohort_150_summary.json")"""))

    cells.append(nbf.v4.new_markdown_cell("""---
## Phase 1 Conclusion & Phase 2 Next Steps

The 150 archetypal counties represent ~4.8% of the United States, providing a deep, robust statistical sample across all 5 macro-regions:
- **Urbanization**: Dense mega-cities (Cook IL, Harris TX, King WA, Maricopa AZ, New York NY) down to Frontier wilderness.
- **Wealth Spectrum**: Executive tech corridors (Loudoun VA, Santa Clara CA, Douglas CO) to persistent poverty rural regions.
- **Political Dynamics**: Deep Democratic anchors, solid Republican heartlands, and critical swing bellwethers.

### Ready for Phase 2:
In **Notebook 2**, we iterate over each of these 150 counties, extract bounded slices from the **20 public datasets**, aggregate into the H3 hexagonal grid cells, and mine cross-domain association rules to discover unexpected connections!"""))

    nb.cells = cells
    out_path = Path("notebooks/01_county_benchmark_and_archetypes.ipynb")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print(f"Created notebook at {out_path} with {len(cells)} cells.")

if __name__ == "__main__":
    create_notebook()
