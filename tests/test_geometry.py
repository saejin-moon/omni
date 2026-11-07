"""Tests for true polygon geometry and point-in-polygon containment."""

import pytest
from shapely.geometry import Point
from omni.benchmark.builder import build_master_county_benchmark


def test_polygon_validity_and_containment():
    gdf = build_master_county_benchmark()
    
    # Test random sample of 20 counties
    sample = gdf.sample(n=20, random_state=42)
    
    for _, row in sample.iterrows():
        geom = row.geometry
        assert geom.is_valid or geom.buffer(0).is_valid
        
        # Bounding box coordinates
        minx, miny, maxx, maxy = geom.bounds
        assert minx == row["min_lon"]
        assert miny == row["min_lat"]
        assert maxx == row["max_lon"]
        assert maxy == row["max_lat"]
        
        # Centroid should be within or near bounds
        centroid = geom.centroid
        assert minx <= centroid.x <= maxx
        assert miny <= centroid.y <= maxy
        
        # A point far outside the bounding box must NOT be contained in polygon
        outside_pt = Point(minx - 1.0, miny - 1.0)
        assert not geom.contains(outside_pt)
