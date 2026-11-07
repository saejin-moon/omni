"""Tests for discretization and cross-domain association rule mining."""

import pytest
import pandas as pd
from omni.benchmark.builder import build_master_county_benchmark
from omni.selection.stratifier import select_nationwide_cohort
from omni.adapters.hub import build_harmonized_cross_domain_feature_store
from omni.mining.engine import discretize_cross_domain_features, mine_cross_domain_association_rules


def test_cross_domain_mining():
    gdf = build_master_county_benchmark()
    cohort = select_nationwide_cohort(gdf, n_per_region=30)
    assert len(cohort) == 150
    
    # Harmonize features
    feature_store = build_harmonized_cross_domain_feature_store(cohort)
    
    # Discretize
    tx = discretize_cross_domain_features(feature_store)
    assert len(tx) == 150
    assert tx.shape[1] >= 50
    assert tx.dtypes.unique()[0] == bool
    
    # Mine association rules
    rules = mine_cross_domain_association_rules(
        tx, min_support=0.10, min_confidence=0.55, min_lift=1.3, max_len=3
    )
    
    # Assert rules discovered and cross-domain enforcement holds
    assert len(rules) > 0
    assert "discovery_score" in rules.columns
    assert "total_domains_bridged" in rules.columns
    
    for _, row in rules.head(10).iterrows():
        assert row["total_domains_bridged"] >= 2
        assert row["lift"] >= 1.3
        assert row["confidence"] >= 0.55

    # Check presence of new domain prefixes in mined rules
    all_bridged = " ".join(rules["antecedent_domains"].tolist() + rules["consequent_domains"].tolist())
    assert any(d in all_bridged for d in ["ENERGY", "TOXIC", "CLIMATE", "INNOV", "DIGITAL", "WATER", "LAND"])
