"""Cross-domain association rule mining engine with FP-Growth and cross-domain novelty filters."""

from typing import Dict, List, Optional, Set, Tuple
import pandas as pd
import numpy as np
from mlxtend.frequent_patterns import fpgrowth, association_rules


DOMAIN_PREFIXES = {
    "INFRA": "Infrastructure & Bridges (FHWA/OSM)",
    "SAFETY": "Highway Safety & Fatalities (NHTSA)",
    "BIO": "Biodiversity & Ecology (GBIF)",
    "SAT": "Satellite Atmosphere & Earth Observation (Copernicus/USGS)",
    "AIR": "Airspace Congestion & Flight Noise (OpenSky)",
    "SEISMIC": "Seismic & Ground Motion (EarthScope/IRIS)",
    "CORP": "Corporate Capital & HQs (SEC EDGAR)",
    "LEGAL": "Federal Litigation & Bankruptcy (CourtListener)",
    "HEALTH": "Public Health & Pathogens (CDC/NCBI)",
    "POL": "Political Swings & Turnout (MEDSL)",
    "WEALTH": "Income & Poverty (Census/SAIPE)",
    "ASTRO": "Night Sky Darkness & Quiet Zone (SETI/Gaia)",
    "ENERGY": "Clean & Utility Energy (USWTDB/USPVDB/EIA)",
    "TOXIC": "Industrial Toxics & Superfund (EPA TRI/NPL)",
    "AIRQUAL": "Air Quality & PM2.5 (EPA AQS)",
    "WATER": "Drinking Water Systems & Violations (EPA SDWIS)",
    "HYDRO": "Hydrology & River Runoff (USGS NWIS)",
    "CLIMATE": "Severe Weather & Drought (NOAA/USDM)",
    "FIRE": "Wildfire & Thermal Hotspots (NASA FIRMS)",
    "AGRI": "Agriculture & Livestock CAFO (USDA NASS)",
    "FOOD": "Food Deserts & Nutritional Access (USDA ERS)",
    "DIGITAL": "Broadband Deficit & Fiber Coverage (FCC BDC)",
    "TELECOM": "Antenna Towers & Infrastructure (FCC ASR)",
    "LABOR": "Wages & Tech Employment (BLS QCEW)",
    "INNOV": "Patents & Innovation (USPTO)",
    "CRIME": "Crime & Public Safety (FBI UCR)",
    "SUBSTANCE": "Overdose & Opioid Prescriptions (CDC WONDER)",
    "HOUSING": "Fair Market Rent & Severe Rent Burden (HUD)",
    "RAIL": "Freight Railroads & Grade Crossings (FRA)",
    "LAND": "Protected Wilderness & Public Lands (USGS PAD-US)",
}


def discretize_cross_domain_features(df_harmonized: pd.DataFrame) -> pd.DataFrame:
    """Converts continuous cross-domain metrics into domain-tagged binary predicates."""
    tx = pd.DataFrame(index=df_harmonized.index)
    
    # Infrastructure (FHWA / OSM)
    tx["INFRA_Poor_Bridge_Decay_High"] = df_harmonized["bridge_poor_condition_pct"] > 8.0
    tx["INFRA_Pre1970_Aging_Bridges"] = df_harmonized["bridge_pre1970_pct"] > 35.0
    tx["INFRA_Heavy_Bridge_Traffic"] = df_harmonized["bridge_avg_daily_traffic"] > 3500.0
    
    # Safety & Fatal Crashes (NHTSA)
    tx["SAFETY_Fatal_Crashes_Elevated"] = df_harmonized["fars_fatal_crashes"] > df_harmonized["fars_fatal_crashes"].median()
    tx["SAFETY_Alcohol_Fatalities_High"] = df_harmonized["fars_alcohol_involved_pct"] > 27.0
    tx["SAFETY_Nighttime_Fatalities_High"] = df_harmonized["fars_nighttime_pct"] > 45.0
    tx["SAFETY_Pedestrian_Fatalities_Present"] = df_harmonized["fars_pedestrian_involved_pct"] > 10.0
    
    # Biodiversity (GBIF)
    tx["BIO_High_Biodiversity_Threat"] = df_harmonized["gbif_threatened_species_count"] > df_harmonized["gbif_threatened_species_count"].median()
    tx["BIO_Species_Richness_Elevated"] = df_harmonized["gbif_shannon_biodiversity_index"] > 3.0
    
    # Satellite Atmosphere & Earth Observation (Copernicus / USGS)
    tx["SAT_NO2_Tropospheric_Pollution_High"] = df_harmonized["copernicus_no2_tropospheric_pollution"] > 30.0
    tx["SAT_Dense_Vegetation_Canopy"] = df_harmonized["copernicus_ndvi_greenness"] > 0.55
    tx["SAT_Urban_Builtup_Impervious_High"] = df_harmonized["copernicus_ndbi_builtup"] > -0.05
    tx["SAT_Mountain_Rugged_Terrain"] = df_harmonized["usgs_terrain_ruggedness_index"] > 120.0
    
    # Airspace & Noise (OpenSky)
    tx["AIR_Flight_Overflight_Corridor_Dense"] = df_harmonized["opensky_flight_density"] > 25.0
    tx["AIR_Low_Altitude_Approach_Noise_Elevated"] = df_harmonized["opensky_low_altitude_noise_pct"] > 20.0
    
    # Seismology (EarthScope / IRIS)
    tx["SEISMIC_Active_Tremor_Zone"] = df_harmonized["iris_seismic_events"] > 4.0
    
    # Corporate Capital (SEC EDGAR)
    tx["CORP_Public_HQs_Present"] = df_harmonized["sec_corporate_hq_count"] > 0.0
    
    # Legal & Judicial (CourtListener RECAP)
    tx["LEGAL_Federal_Litigation_Rate_High"] = df_harmonized["recap_litigation_rate_per_10k"] > 20.0
    tx["LEGAL_Bankruptcy_Rate_Elevated"] = df_harmonized["recap_bankruptcy_rate_per_10k"] > 15.0
    
    # Public Health & Pathogens (CDC / NCBI)
    tx["HEALTH_Chronic_Asthma_Elevated"] = df_harmonized["cdc_asthma_prevalence_pct"] > 10.8
    tx["HEALTH_Diabetes_Prevalence_High"] = df_harmonized["cdc_diabetes_prevalence_pct"] > 12.0
    tx["HEALTH_Depression_Prevalence_High"] = df_harmonized["cdc_depression_prevalence_pct"] > 23.5
    tx["HEALTH_Pathogen_Isolates_Detected"] = df_harmonized["ncbi_pathogen_isolates"] > 5.0
    
    # Political Shifts (MEDSL)
    tx["POL_Partisan_Dem_Anchor"] = df_harmonized["dem_margin_2020"] > 0.15
    tx["POL_Partisan_GOP_Heartland"] = df_harmonized["dem_margin_2020"] < -0.20
    tx["POL_Significant_8yr_GOP_Swing"] = df_harmonized["swing_2012_2020"] < -0.12
    tx["POL_Significant_8yr_Dem_Shift"] = df_harmonized["swing_2012_2020"] > 0.08
    tx["POL_High_Voter_Turnout"] = df_harmonized["turnout_rate_2020"] > 0.72
    
    # Wealth & Poverty (Census / SAIPE)
    tx["WEALTH_High_Income_Executive"] = df_harmonized["median_hh_income"] > 78_000.0
    tx["WEALTH_Persistent_Child_Poverty"] = df_harmonized["child_poverty_pct"] > 20.0
    
    # Astro-Terrestrial Link (SETI / Gaia)
    tx["ASTRO_Pristine_Dark_Sky_Wilderness"] = df_harmonized["is_dark_sky_preserve"] == 1.0

    # Energy & Utilities (USWTDB, USPVDB, EIA-860)
    tx["ENERGY_Wind_Turbine_Belt"] = df_harmonized["uswtdb_wind_turbine_count"] > 15.0
    tx["ENERGY_Utility_Solar_Present"] = df_harmonized["uspvdb_solar_facility_count"] > 2.0
    tx["ENERGY_Clean_Energy_Exceeds_Fossil"] = df_harmonized["eia_clean_energy_mw"] > df_harmonized["eia_fossil_mw"]

    # Environmental Hazards & Toxics (EPA NPL & TRI)
    tx["TOXIC_Superfund_NPL_Site_Present"] = df_harmonized["epa_superfund_npl_sites"] > 0.0
    tx["TOXIC_High_Industrial_Chemical_Releases"] = df_harmonized["epa_tri_total_releases_lbs"] > 250000.0

    # Air & Water Quality (EPA AQS & SDWIS)
    tx["AIRQUAL_Unhealthy_AQI_Days_Elevated"] = df_harmonized["epa_aqs_unhealthy_aqi_days"] > 12.0
    tx["WATER_Drinking_Water_Violations_Present"] = df_harmonized["sdwis_health_violations_count"] > 2.0

    # Hydrology (USGS NWIS)
    tx["HYDRO_High_Volume_River_Runoff"] = df_harmonized["usgs_mean_annual_runoff_cfs"] > 2000.0

    # Climate Hazards & Drought (NOAA & USDM)
    tx["CLIMATE_Severe_Tornado_Corridor"] = df_harmonized["noaa_severe_tornado_count"] > 5.0
    tx["CLIMATE_Persistent_Severe_Drought"] = df_harmonized["usdm_cumulative_weeks_severe_drought_d2_d4"] > 40.0

    # Wildfire (NASA FIRMS)
    tx["FIRE_Active_Wildfire_Burn_Risk"] = df_harmonized["firms_active_fire_hotspots_count"] > 15.0

    # Agriculture & Food (USDA NASS & ERS)
    tx["AGRI_Intensive_Cropland_Dominant"] = df_harmonized["usda_harvested_cropland_acres_pct"] > 40.0
    tx["AGRI_High_Density_Livestock_CAFO"] = df_harmonized["usda_cafo_livestock_density"] > 8.0
    tx["FOOD_Food_Desert_Prevalence_High"] = df_harmonized["usda_food_desert_pop_pct"] > 20.0

    # Digital Divide & Telecom (FCC BDC & ASR)
    tx["DIGITAL_High_Broadband_Deficit"] = df_harmonized["fcc_unserved_broadband_pct"] > 15.0
    tx["DIGITAL_Gigabit_Fiber_Widespread"] = df_harmonized["fcc_gigabit_fiber_coverage_pct"] > 70.0
    tx["TELECOM_Cell_Tower_Dense"] = df_harmonized["fcc_cell_tower_density_per_100sqkm"] > 5.0

    # Labor & Innovation (BLS QCEW & USPTO)
    tx["LABOR_High_Tech_STEM_Workforce"] = df_harmonized["bls_stem_tech_employment_share_pct"] > 12.0
    tx["LABOR_High_Average_Wage"] = df_harmonized["bls_avg_annual_wage_usd"] > 70000.0
    tx["INNOV_Patent_Innovation_Hotspot"] = df_harmonized["uspto_patents_granted_per_10k"] > 15.0

    # Crime & Substance (FBI UCR & CDC WONDER)
    tx["CRIME_Violent_Crime_Rate_Elevated"] = df_harmonized["fbi_violent_crime_rate_per_100k"] > 350.0
    tx["SUBSTANCE_Overdose_Mortality_Elevated"] = df_harmonized["cdc_overdose_mortality_rate_per_100k"] > 32.0

    # Housing, Rail & Federal Lands (HUD, FRA, USGS PAD-US)
    tx["HOUSING_Severe_Rent_Burden_Elevated"] = df_harmonized["hud_severe_cost_burden_renters_pct"] > 20.0
    tx["RAIL_Freight_Rail_Corridor_Dense"] = df_harmonized["fra_freight_rail_track_miles"] > 30.0
    tx["LAND_Vast_Federal_Public_Lands"] = df_harmonized["usgs_padus_protected_public_land_pct"] > 30.0

    return tx
    
    return tx


def extract_domains_from_itemset(itemset) -> Set[str]:
    """Returns the set of unique domain prefixes present in an itemset."""
    domains = set()
    for item in itemset:
        parts = item.split("_", 1)
        if len(parts) > 0 and parts[0] in DOMAIN_PREFIXES:
            domains.add(parts[0])
    return domains


def mine_cross_domain_association_rules(
    df_transactions: pd.DataFrame,
    min_support: float = 0.10,
    min_confidence: float = 0.60,
    min_lift: float = 1.4,
    max_len: int = 3
) -> pd.DataFrame:
    """Mines frequent itemsets with FP-Growth and extracts cross-domain association rules.
    
    Applies strict multi-domain constraints: only keeps rules where the antecedent
    and consequent bridge distinct dataset domains, filtering out single-domain tautologies.
    Uses max_len (default 3) to prevent combinatorial explosion and focus on actionable insights.
    """
    print(f"Mining frequent itemsets with FP-Growth (min_support={min_support:.2f}, max_len={max_len})...")
    frequent_items = fpgrowth(df_transactions, min_support=min_support, max_len=max_len, use_colnames=True)
    print(f"Discovered {len(frequent_items)} frequent itemsets.")
    
    if len(frequent_items) == 0:
        return pd.DataFrame()
        
    print(f"Extracting association rules (min_confidence={min_confidence:.2f}, min_lift={min_lift:.2f})...")
    rules = association_rules(frequent_items, metric="lift", min_threshold=min_lift)
    rules = rules[rules["confidence"] >= min_confidence].copy()
    print(f"Generated {len(rules)} total candidate rules.")
    
    # Filter for Cross-Domain Rules
    cross_domain_flags = []
    antecedent_domains_list = []
    consequent_domains_list = []
    domain_span_counts = []
    
    for _, row in rules.iterrows():
        ant_domains = extract_domains_from_itemset(row["antecedents"])
        con_domains = extract_domains_from_itemset(row["consequents"])
        
        # Rule is cross-domain if antecedent and consequent have distinct domains
        total_domains = ant_domains.union(con_domains)
        is_cross = (len(total_domains) >= 2) and (len(ant_domains.intersection(con_domains)) == 0)
        
        cross_domain_flags.append(is_cross)
        antecedent_domains_list.append(", ".join(sorted(list(ant_domains))))
        consequent_domains_list.append(", ".join(sorted(list(con_domains))))
        domain_span_counts.append(len(total_domains))
        
    rules["is_cross_domain"] = cross_domain_flags
    rules["antecedent_domains"] = antecedent_domains_list
    rules["consequent_domains"] = consequent_domains_list
    rules["total_domains_bridged"] = domain_span_counts
    
    cross_rules = rules[rules["is_cross_domain"]].copy()
    
    # Format itemsets for human readability
    cross_rules["antecedents_str"] = cross_rules["antecedents"].apply(lambda x: " + ".join(list(x)))
    cross_rules["consequents_str"] = cross_rules["consequents"].apply(lambda x: " + ".join(list(x)))
    
    # Calculate Novelty / Discovery Score
    cross_rules["discovery_score"] = (
        cross_rules["lift"] * np.sqrt(cross_rules["support"]) * cross_rules["confidence"] * cross_rules["total_domains_bridged"]
    )
    
    cross_rules = cross_rules.sort_values("discovery_score", ascending=False).reset_index(drop=True)
    print(f"Successfully filtered {len(cross_rules)} genuine cross-domain association rules.")
    return cross_rules
