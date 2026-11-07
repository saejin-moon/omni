"""Tests for regional stratification and 150-county archetype selection."""

import pytest
from omni.benchmark.builder import build_master_county_benchmark
from omni.selection.stratifier import select_nationwide_cohort, select_nationwide_cohort_75


def test_stratification_cohort_150():
    gdf = build_master_county_benchmark()
    cohort_150 = select_nationwide_cohort(gdf, n_per_region=30)
    
    # Assert exactly 150 counties
    assert len(cohort_150) == 150
    
    # Assert exactly 30 per macro-region
    counts = cohort_150["macro_region"].value_counts()
    for reg in ["Northeast", "Midwest", "South / Southeast", "Southwest", "Northwest"]:
        assert counts[reg] == 30, f"Region {reg} has {counts[reg]} counties instead of 30"
        
    # Assert each county has valid H3 cells and true polygon geometry
    for _, row in cohort_150.iterrows():
        assert len(row["h3_cells"]) > 0
        assert row["h3_cell_count"] > 0
        assert row["geometry"].is_valid or row["geometry"].buffer(0).is_valid
        assert len(row["wkt_polygon"]) > 10
        assert "archetype_label" in row


def test_stratification_cohort_75_alias():
    gdf = build_master_county_benchmark()
    cohort_75 = select_nationwide_cohort_75(gdf)
    assert len(cohort_75) == 75
