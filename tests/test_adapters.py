"""Tests for dataset adapters and cross-domain feature store."""

import pytest
import geopandas as gpd
from omni.benchmark.builder import build_master_county_benchmark
from omni.selection.stratifier import select_nationwide_cohort_75
from omni.adapters.hub import build_harmonized_cross_domain_feature_store


def test_cross_domain_adapters():
    gdf = build_master_county_benchmark()
    cohort = select_nationwide_cohort_75(gdf, n_per_region=15)
    
    # Run on sample of cohort for fast unit testing
    sample_cohort = cohort.head(10).copy()
    feature_store = build_harmonized_cross_domain_feature_store(sample_cohort)
    
    # Assert shape and key columns
    assert len(feature_store) == 10
    
    expected_columns = [
        "bridge_poor_condition_pct",
        "fars_fatal_crashes",
        "gbif_threatened_species_count",
        "copernicus_no2_tropospheric_pollution",
        "opensky_flight_density",
        "sec_corporate_hq_count",
        "recap_litigation_rate_per_10k",
        "cdc_asthma_prevalence_pct",
        # New 22 datasets indicators
        "uswtdb_wind_turbine_count",
        "uspvdb_solar_facility_count",
        "eia_total_power_plants",
        "epa_superfund_npl_sites",
        "epa_tri_total_releases_lbs",
        "epa_aqs_unhealthy_aqi_days",
        "sdwis_health_violations_count",
        "usgs_streamgage_count",
        "noaa_severe_tornado_count",
        "usdm_cumulative_weeks_severe_drought_d2_d4",
        "firms_active_fire_hotspots_count",
        "usda_harvested_cropland_acres_pct",
        "usda_food_desert_pop_pct",
        "fcc_unserved_broadband_pct",
        "fcc_cell_tower_density_per_100sqkm",
        "bls_avg_annual_wage_usd",
        "uspto_patents_granted_per_10k",
        "fbi_violent_crime_rate_per_100k",
        "cdc_overdose_mortality_rate_per_100k",
        "hud_severe_cost_burden_renters_pct",
        "fra_freight_rail_track_miles",
        "usgs_padus_protected_public_land_pct",
    ]
    for col in expected_columns:
        assert col in feature_store.columns
        assert feature_store[col].isna().sum() == 0
