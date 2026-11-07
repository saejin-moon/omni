"""Regional stratification and archetypal county selection engine."""

from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
import geopandas as gpd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import h3

STRATIFICATION_FEATURES = [
    "pop_2023",
    "pop_density_sq_km",
    "rucc_code",
    "median_hh_income",
    "poverty_pct",
    "child_poverty_pct",
    "pop_growth_pct",
    "net_migration_rate",
    "dem_margin_2020",
    "swing_2012_2020",
    "turnout_rate_2020",
    "racial_diversity_index",
    "nonwhite_pct",
    "age29andunder_pct",
    "age65andolder_pct",
]


def classify_archetype_label(row: pd.Series, is_centroid: bool = False) -> str:
    """Assigns an intuitive, descriptive archetype label based on feature signatures."""
    if is_centroid:
        return "Regional Statistical Centroid (Archetypal Average)"

    # Urban Core
    if row["rucc_code"] == 1 and row["pop_2023"] > 500_000:
        return "Mega-Urban Economic Center"
    
    # Affluent Suburb
    if row["rucc_code"] in [1, 2, 3] and row["median_hh_income"] > 85_000:
        return "Affluent High-Tech / Executive Suburb"
        
    # University / Youth Town
    if row["age29andunder_pct"] > 42.0:
        return "University / Higher-Ed Innovation Hub"

    # Rapid Growth Exurb
    if row["pop_growth_pct"] > 4.0 or row["net_migration_rate"] > 15.0:
        return "Rapid-Growth Exurban / Sunbelt Corridor"

    # Persistent Poverty
    if row["poverty_pct"] > 21.0 or row["child_poverty_pct"] > 26.0:
        return "Persistent-Poverty Distressed Rural"

    # Majority Minority
    if row["nonwhite_pct"] > 50.0:
        return "Diverse Majority-Minority Community"

    # Swing Bellwether
    if abs(row["dem_margin_2020"]) < 0.06 or abs(row["swing_2012_2020"]) > 0.18:
        return "Swing Bellwether / Polar Pivot County"

    # Working Class Industrial
    if row["rucc_code"] in [2, 3, 4] and row["median_hh_income"] < 65_000:
        return "Working-Class Industrial / Post-Industrial Hub"

    # Agriculture Heartland
    if row["rucc_code"] in [6, 7, 8, 9] and row["pop_density_sq_km"] < 25.0:
        return "Intensive Agricultural / Rural Heartland"

    # Remote Frontier
    if row["pop_density_sq_km"] < 5.0:
        return "Remote Frontier / Wilderness"

    # Mid-Sized Metro
    if row["rucc_code"] in [2, 3]:
        return "Mid-Sized Regional Anchor Metro"

    return "Rural-Urban Transition Community"


def generate_county_h3_cells(geom, resolution: int = 7) -> List[str]:
    """Generates Uber H3 hexagon cells covering the interior of the polygon.
    
    Falls back to lower resolution if county is extremely large (e.g. Western counties),
    keeping cell counts manageable (~50 to 500 cells per county).
    """
    try:
        # Convert shapely geometry to GeoJSON dict
        geo_dict = geom.__geo_interface__
        
        # Test cell count estimate
        cells = list(h3.polygon_to_cells(h3.geojson_to_h3shape(geo_dict), res=resolution))
        if len(cells) > 800:
            # Step down resolution for giant counties
            cells = list(h3.polygon_to_cells(h3.geojson_to_h3shape(geo_dict), res=resolution - 1))
        elif len(cells) == 0:
            # Step up resolution for tiny counties
            cells = list(h3.polygon_to_cells(h3.geojson_to_h3shape(geo_dict), res=resolution + 1))
        return cells
    except Exception:
        # Fallback to centroid cell
        c = geom.centroid
        return [h3.latlng_to_cell(c.y, c.x, resolution)]


def select_regional_archetypes(
    gdf_region: gpd.GeoDataFrame,
    n_counties: int = 15,
    h3_resolution: int = 7,
    random_state: int = 42
) -> gpd.GeoDataFrame:
    """Selects n_counties distinct archetypal counties for a given macro-region.
    
    Applies PCA dimensionality reduction and K-Medoids/K-Means clustering
    to guarantee spanning the full socioeconomic, density, and political spectrum.
    """
    df = gdf_region.copy()
    
    # Feature preparation with log transforms on power-law features
    X = df[STRATIFICATION_FEATURES].copy()
    X["log_pop"] = np.log10(X["pop_2023"].clip(lower=100.0))
    X["log_density"] = np.log10(X["pop_density_sq_km"].clip(lower=0.1))
    X_feat = X.drop(columns=["pop_2023", "pop_density_sq_km"])
    
    # Standardize
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_feat)
    
    # PCA to 4 components
    pca = PCA(n_components=4, random_state=random_state)
    X_pca = pca.fit_transform(X_scaled)
    
    # 1. Identify Regional Statistical Centroid (closest to 0 in standardized PCA space)
    dists_to_origin = np.linalg.norm(X_pca, axis=1)
    centroid_idx = int(np.argmin(dists_to_origin))
    
    # 2. Cluster remaining counties into (n_counties - 1) diverse archetypes
    n_clusters = n_counties - 1
    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    kmeans.fit(X_pca)
    
    selected_indices = [centroid_idx]
    
    for c_i in range(n_clusters):
        center = kmeans.cluster_centers_[c_i]
        dists = np.linalg.norm(X_pca - center, axis=1)
        for s_idx in np.argsort(dists):
            if s_idx not in selected_indices:
                selected_indices.append(int(s_idx))
                break
                
    selected_gdf = df.iloc[selected_indices].copy()
    
    # Attach PCA coordinates
    selected_gdf["pca_dim1"] = X_pca[selected_indices, 0]
    selected_gdf["pca_dim2"] = X_pca[selected_indices, 1]
    selected_gdf["pca_dim3"] = X_pca[selected_indices, 2]
    selected_gdf["pca_dim4"] = X_pca[selected_indices, 3]
    
    # Assign Archetypes
    archetypes = []
    is_centroid_list = []
    for i, (_, row) in enumerate(selected_gdf.iterrows()):
        is_cent = (i == 0)
        is_centroid_list.append(is_cent)
        label = classify_archetype_label(row, is_centroid=is_cent)
        archetypes.append(label)
        
    selected_gdf["is_regional_centroid"] = is_centroid_list
    selected_gdf["archetype_label"] = archetypes
    
    # Generate H3 Polyfill cells
    print(f"Generating H3 polyfill hexagons for {len(selected_gdf)} counties in {gdf_region['macro_region'].iloc[0]}...")
    h3_cells_list = []
    h3_cell_count_list = []
    wkt_list = []
    
    for _, row in selected_gdf.iterrows():
        geom = row.geometry
        cells = generate_county_h3_cells(geom, resolution=h3_resolution)
        h3_cells_list.append(cells)
        h3_cell_count_list.append(len(cells))
        wkt_list.append(geom.wkt)
        
    selected_gdf["h3_cells"] = h3_cells_list
    selected_gdf["h3_cell_count"] = h3_cell_count_list
    selected_gdf["wkt_polygon"] = wkt_list
    
    return selected_gdf.reset_index(drop=True)


def select_nationwide_cohort(
    gdf_benchmark: gpd.GeoDataFrame,
    n_per_region: int = 30,
    h3_resolution: int = 7
) -> gpd.GeoDataFrame:
    """Selects n_per_region representative archetypes for each of the 5 macro-regions (default 30 per region = 150 total).
    
    Returns:
        GeoDataFrame containing the representative counties with exact polygons,
        H3 cells, bounding boxes, and archetype labels.
    """
    regions = ["Northeast", "Midwest", "South / Southeast", "Southwest", "Northwest"]
    regional_dfs = []
    
    for reg in regions:
        print(f"\n--- Stratifying {reg} (target: {n_per_region} counties) ---")
        gdf_reg = gdf_benchmark[gdf_benchmark["macro_region"] == reg].copy()
        selected_reg = select_regional_archetypes(
            gdf_reg, n_counties=n_per_region, h3_resolution=h3_resolution
        )
        regional_dfs.append(selected_reg)
        
    cohort = pd.concat(regional_dfs, ignore_index=True)
    cohort_gdf = gpd.GeoDataFrame(cohort, crs="EPSG:4326")
    print(f"\nSuccessfully selected {len(cohort_gdf)} archetypal counties across 5 macro-regions.")
    return cohort_gdf


def select_nationwide_cohort_75(
    gdf_benchmark: gpd.GeoDataFrame,
    n_per_region: int = 15,
    h3_resolution: int = 7
) -> gpd.GeoDataFrame:
    """Backwards-compatible alias for 75-county cohort."""
    return select_nationwide_cohort(gdf_benchmark, n_per_region=n_per_region, h3_resolution=h3_resolution)
