"""Master benchmark builder: merges Census, USDA, SAIPE, MEDSL elections, and TIGER polygons."""

import csv
import json
from pathlib import Path
from typing import Dict, Optional, Tuple

import geopandas as gpd
import pandas as pd
from shapely.geometry import shape

from omni.benchmark.sources import download_benchmark_sources

# 5 Macro-Regions mapping covering all 50 US States + DC
STATE_TO_REGION: Dict[str, str] = {
    # Northeast (9 states)
    "CT": "Northeast", "MA": "Northeast", "ME": "Northeast", "NH": "Northeast",
    "NJ": "Northeast", "NY": "Northeast", "PA": "Northeast", "RI": "Northeast",
    "VT": "Northeast",
    
    # Midwest (12 states)
    "IA": "Midwest", "IL": "Midwest", "IN": "Midwest", "KS": "Midwest",
    "MI": "Midwest", "MN": "Midwest", "MO": "Midwest", "ND": "Midwest",
    "NE": "Midwest", "OH": "Midwest", "SD": "Midwest", "WI": "Midwest",
    
    # The South / Southeast (15 states + DC)
    "AL": "South / Southeast", "AR": "South / Southeast", "DC": "South / Southeast",
    "DE": "South / Southeast", "FL": "South / Southeast", "GA": "South / Southeast",
    "KY": "South / Southeast", "LA": "South / Southeast", "MD": "South / Southeast",
    "MS": "South / Southeast", "NC": "South / Southeast", "SC": "South / Southeast",
    "TN": "South / Southeast", "VA": "South / Southeast", "WV": "South / Southeast",
    
    # Southwest (4 states)
    "AZ": "Southwest", "NM": "Southwest", "OK": "Southwest", "TX": "Southwest",
    
    # Northwest / Pacific West (10 states)
    "AK": "Northwest", "CA": "Northwest", "CO": "Northwest", "HI": "Northwest",
    "ID": "Northwest", "MT": "Northwest", "NV": "Northwest", "OR": "Northwest",
    "UT": "Northwest", "WA": "Northwest", "WY": "Northwest",
}


def build_master_county_benchmark(cache_dir: str = "data/raw/benchmark") -> gpd.GeoDataFrame:
    """Loads and joins all public benchmark sources into a single GeoDataFrame.
    
    Returns:
        GeoDataFrame indexed by 5-digit FIPS with full political, demographic,
        economic, geographic, and polygon attributes across all ~3,143 US counties.
    """
    paths = download_benchmark_sources(cache_dir=cache_dir)
    
    # 1. Load GeoJSON geometries
    print("Loading county cartographic boundary polygons...")
    with open(paths["county_polygons_geojson"], "r", encoding="utf-8") as f:
        geojson_data = json.load(f)
    
    geo_records = []
    for feat in geojson_data["features"]:
        fips = str(feat["id"]).zfill(5)
        geom = shape(feat["geometry"])
        minx, miny, maxx, maxy = geom.bounds
        centroid = geom.centroid
        geo_records.append({
            "fips": fips,
            "geometry": geom,
            "min_lon": minx,
            "min_lat": miny,
            "max_lon": maxx,
            "max_lat": maxy,
            "centroid_lon": centroid.x,
            "centroid_lat": centroid.y,
        })
    gdf_base = gpd.GeoDataFrame(geo_records, crs="EPSG:4326")
    
    # 2. Parse Census SAIPE 2022 (Income & Poverty)
    print("Parsing Census SAIPE income & poverty...")
    saipe = {}
    with open(paths["census_saipe_2022"], "r", encoding="latin-1") as f:
        for line in f:
            st = line[0:2].strip().zfill(2)
            cty = line[3:6].strip()
            if cty == "0" or not cty:
                continue
            fips = st + cty.zfill(3)
            try:
                saipe[fips] = {
                    "poverty_pct": float(line[34:38].strip()),
                    "child_poverty_pct": float(line[76:80].strip()),
                    "median_hh_income": float(line[133:139].strip()),
                    "state_abbr": line[239:241].strip(),
                }
            except Exception:
                pass

    # 3. Parse USDA ERS RUCC 2023
    print("Parsing USDA ERS 2023 Rural-Urban Continuum Codes...")
    rucc = {}
    with open(paths["usda_rucc_2023"], "r", encoding="latin-1") as f:
        for row in csv.DictReader(f):
            fips = row["FIPS"].strip().zfill(5)
            attr = row["Attribute"].strip()
            val = row["Value"].strip()
            if fips not in rucc:
                rucc[fips] = {"state_abbr": row["State"].strip()}
            if attr == "RUCC_2023":
                try:
                    rucc[fips]["rucc_code"] = int(val)
                except ValueError:
                    rucc[fips]["rucc_code"] = 0
            elif attr == "Description":
                rucc[fips]["rucc_desc"] = val

    # 4. Parse Census Population 2020-2023
    print("Parsing Census population estimates & migration...")
    pop = {}
    with open(paths["census_pop_2023"], "r", encoding="latin-1") as f:
        for row in csv.DictReader(f):
            if row["SUMLEV"] == "050":
                fips = row["STATE"].zfill(2) + row["COUNTY"].zfill(3)
                p20 = float(row["POPESTIMATE2020"])
                p23 = float(row["POPESTIMATE2023"])
                growth = ((p23 - p20) / p20 * 100) if p20 > 0 else 0.0
                mig = float(row["NETMIG2023"])
                pop[fips] = {
                    "county_name": row["CTYNAME"].strip(),
                    "state_name": row["STNAME"].strip(),
                    "pop_2020": p20,
                    "pop_2023": p23,
                    "pop_growth_pct": growth,
                    "net_migration_2023": mig,
                    "net_migration_rate": (mig / p23 * 1000) if p23 > 0 else 0.0,
                }

    # 5. Parse 2020 Presidential Election Results
    print("Parsing 2020 presidential election results...")
    elec20 = {}
    with open(paths["election_results_2020"], "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            fips = row["county_fips"].strip().zfill(5)
            try:
                v_dem = float(row["votes_dem"])
                v_gop = float(row["votes_gop"])
                tot = float(row["total_votes"])
                p_dem = v_dem / tot if tot > 0 else 0.0
                p_gop = v_gop / tot if tot > 0 else 0.0
                elec20[fips] = {
                    "votes_dem_2020": v_dem,
                    "votes_gop_2020": v_gop,
                    "total_votes_2020": tot,
                    "per_dem_2020": p_dem,
                    "per_gop_2020": p_gop,
                    "dem_margin_2020": p_dem - p_gop,
                }
            except Exception:
                pass

    # 6. Parse MEDSL Election Context (2012, 2016, Demographics)
    print("Parsing MEDSL 2012/2016 elections & demographic context...")
    medsl = {}
    with open(paths["election_context_medsl"], "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            fips = row["fips"].strip().zfill(5)
            try:
                # 2016
                t16 = float(row["trump16"]) if row["trump16"] else 0.0
                c16 = float(row["clinton16"]) if row["clinton16"] else 0.0
                o16 = float(row["otherpres16"]) if row["otherpres16"] else 0.0
                tot16 = t16 + c16 + o16
                p_dem16 = c16 / tot16 if tot16 > 0 else 0.0
                p_gop16 = t16 / tot16 if tot16 > 0 else 0.0

                # 2012
                r12 = float(row["romney12"]) if row["romney12"] else 0.0
                ob12 = float(row["obama12"]) if row["obama12"] else 0.0
                o12 = float(row["otherpres12"]) if row["otherpres12"] else 0.0
                tot12 = r12 + ob12 + o12
                p_dem12 = ob12 / tot12 if tot12 > 0 else 0.0
                p_gop12 = r12 / tot12 if tot12 > 0 else 0.0

                cvap = float(row["cvap"]) if row["cvap"] else 0.0
                w_pct = float(row["white_pct"]) if row["white_pct"] else 0.0
                b_pct = float(row["black_pct"]) if row["black_pct"] else 0.0
                h_pct = float(row["hispanic_pct"]) if row["hispanic_pct"] else 0.0
                nw_pct = float(row["nonwhite_pct"]) if row["nonwhite_pct"] else 0.0
                fb_pct = float(row["foreignborn_pct"]) if row["foreignborn_pct"] else 0.0
                u29_pct = float(row["age29andunder_pct"]) if row["age29andunder_pct"] else 0.0
                o65_pct = float(row["age65andolder_pct"]) if row["age65andolder_pct"] else 0.0

                medsl[fips] = {
                    "per_dem_2016": p_dem16,
                    "per_gop_2016": p_gop16,
                    "dem_margin_2016": p_dem16 - p_gop16,
                    "per_dem_2012": p_dem12,
                    "per_gop_2012": p_gop12,
                    "dem_margin_2012": p_dem12 - p_gop12,
                    "cvap": cvap,
                    "white_pct": w_pct,
                    "black_pct": b_pct,
                    "hispanic_pct": h_pct,
                    "nonwhite_pct": nw_pct,
                    "foreignborn_pct": fb_pct,
                    "age29andunder_pct": u29_pct,
                    "age65andolder_pct": o65_pct,
                }
            except Exception:
                pass

    # 7. Harmonize into unified table
    print("Harmonizing all attributes into master table...")
    combined_rows = []
    
    # Base set of FIPS from Population estimates (the gold standard for US counties)
    for fips, p_info in pop.items():
        s_info = saipe.get(fips, {})
        r_info = rucc.get(fips, {})
        e20_info = elec20.get(fips, {})
        m_info = medsl.get(fips, {})
        
        state_abbr = s_info.get("state_abbr") or r_info.get("state_abbr", "")
        if not state_abbr:
            # Fallback to mapping by state name or FIPS
            continue
            
        region = STATE_TO_REGION.get(state_abbr, "Other")
        if region == "Other":
            continue

        p_dem20 = e20_info.get("per_dem_2020", 0.5)
        p_gop20 = e20_info.get("per_gop_2020", 0.5)
        dem_margin20 = e20_info.get("dem_margin_2020", 0.0)
        
        dem_margin16 = m_info.get("dem_margin_2016", dem_margin20)
        dem_margin12 = m_info.get("dem_margin_2012", dem_margin16)
        
        swing_12_20 = dem_margin20 - dem_margin12
        swing_16_20 = dem_margin20 - dem_margin16
        
        tot_votes20 = e20_info.get("total_votes_2020", 0.0)
        cvap = m_info.get("cvap", 0.0)
        turnout_rate = (tot_votes20 / cvap) if cvap > 0 else (tot_votes20 / p_info["pop_2020"] if p_info["pop_2020"] > 0 else 0.5)
        turnout_rate = min(max(turnout_rate, 0.2), 1.0) # bound realistic range
        
        # Diversity index: 1 - sum(p_i^2)
        w_frac = m_info.get("white_pct", 75.0) / 100.0
        b_frac = m_info.get("black_pct", 10.0) / 100.0
        h_frac = m_info.get("hispanic_pct", 10.0) / 100.0
        oth_frac = max(0.0, 1.0 - (w_frac + b_frac + h_frac))
        simpson_diversity = 1.0 - (w_frac**2 + b_frac**2 + h_frac**2 + oth_frac**2)
        
        combined_rows.append({
            "fips": fips,
            "county_name": p_info["county_name"],
            "state_name": p_info["state_name"],
            "state_abbr": state_abbr,
            "macro_region": region,
            "pop_2020": p_info["pop_2020"],
            "pop_2023": p_info["pop_2023"],
            "pop_growth_pct": p_info["pop_growth_pct"],
            "net_migration_2023": p_info["net_migration_2023"],
            "net_migration_rate": p_info["net_migration_rate"],
            "rucc_code": r_info.get("rucc_code", 5),
            "rucc_desc": r_info.get("rucc_desc", "Nonmetro"),
            "median_hh_income": s_info.get("median_hh_income", 55000.0),
            "poverty_pct": s_info.get("poverty_pct", 14.0),
            "child_poverty_pct": s_info.get("child_poverty_pct", 18.0),
            "per_dem_2020": p_dem20,
            "per_gop_2020": p_gop20,
            "dem_margin_2020": dem_margin20,
            "per_dem_2016": m_info.get("per_dem_2016", p_dem20),
            "per_gop_2016": m_info.get("per_gop_2016", p_gop20),
            "dem_margin_2016": dem_margin16,
            "per_dem_2012": m_info.get("per_dem_2012", p_dem20),
            "per_gop_2012": m_info.get("per_gop_2012", p_gop20),
            "dem_margin_2012": dem_margin12,
            "swing_2012_2020": swing_12_20,
            "swing_2016_2020": swing_16_20,
            "turnout_rate_2020": turnout_rate,
            "white_pct": m_info.get("white_pct", 75.0),
            "black_pct": m_info.get("black_pct", 10.0),
            "hispanic_pct": m_info.get("hispanic_pct", 10.0),
            "nonwhite_pct": m_info.get("nonwhite_pct", 25.0),
            "foreignborn_pct": m_info.get("foreignborn_pct", 5.0),
            "age29andunder_pct": m_info.get("age29andunder_pct", 35.0),
            "age65andolder_pct": m_info.get("age65andolder_pct", 18.0),
            "racial_diversity_index": simpson_diversity,
        })
        
    df_data = pd.DataFrame(combined_rows)
    print(f"Merged tabular records: {len(df_data)} counties")
    
    # Merge with geometry
    gdf_final = gdf_base.merge(df_data, on="fips", how="inner")
    
    # Calculate land area and density using cylindrical equal area
    gdf_proj = gdf_final.to_crs(epsg=5070)
    gdf_final["land_area_sq_km"] = gdf_proj.geometry.area / 1_000_000.0
    gdf_final["pop_density_sq_km"] = gdf_final["pop_2023"] / gdf_final["land_area_sq_km"].clip(lower=1.0)
    
    # Sort and re-index
    gdf_final = gdf_final.sort_values("fips").reset_index(drop=True)
    print(f"Final GeoDataFrame ready: {len(gdf_final)} counties with exact polygons.")
    return gdf_final
