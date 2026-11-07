"""Tests for benchmark data builder and sources."""

import pytest
from omni.benchmark.builder import build_master_county_benchmark


def test_master_benchmark_build():
    gdf = build_master_county_benchmark()
    
    # Assert we have over 3,100 US counties with full polygon geometries
    assert len(gdf) >= 3100
    assert "geometry" in gdf.columns
    assert "fips" in gdf.columns
    assert "macro_region" in gdf.columns
    assert "median_hh_income" in gdf.columns
    assert "rucc_code" in gdf.columns
    assert "dem_margin_2020" in gdf.columns

    # Check macro-region coverage
    regions = set(gdf["macro_region"].unique())
    expected_regions = {"Northeast", "Midwest", "South / Southeast", "Southwest", "Northwest"}
    assert regions == expected_regions

    # Ensure no NaN values in essential analytical columns
    critical_cols = [
        "pop_2023", "pop_density_sq_km", "rucc_code",
        "median_hh_income", "poverty_pct", "dem_margin_2020",
        "swing_2012_2020", "racial_diversity_index"
    ]
    for col in critical_cols:
        assert gdf[col].isna().sum() == 0, f"Found NaNs in {col}"
