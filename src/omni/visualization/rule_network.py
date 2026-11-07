"""Visualizations for association mining discoveries, cross-domain correlations, and rule networks."""

from typing import List, Optional, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np


def setup_style():
    sns.set_theme(style="whitegrid", palette="deep")
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Helvetica", "Arial"]
    plt.rcParams["axes.edgecolor"] = "#cccccc"
    plt.rcParams["axes.linewidth"] = 0.8


def plot_cross_domain_correlation_matrix(df_harmonized: pd.DataFrame) -> plt.Figure:
    """Generates a comprehensive cross-domain correlation heatmap across all public dataset domains."""
    setup_style()
    
    analysis_cols = [
        # Infrastructure (FHWA / FRA)
        "bridge_poor_condition_pct", "bridge_avg_daily_traffic", "fra_freight_rail_track_miles",
        # Fatal Crashes (NHTSA)
        "fars_fatal_crashes", "fars_alcohol_involved_pct",
        # Biodiversity & Land (GBIF / USGS PAD-US)
        "gbif_threatened_species_count", "usgs_padus_protected_public_land_pct",
        # Atmosphere & Energy (Copernicus / USWTDB / EPA AQS)
        "copernicus_no2_tropospheric_pollution", "uswtdb_rated_capacity_mw", "epa_aqs_unhealthy_aqi_days",
        # Airspace & Seismology (OpenSky / IRIS)
        "opensky_flight_density", "iris_seismic_events",
        # Climate & Hydrology (USDM / NOAA / NWIS)
        "usdm_cumulative_weeks_severe_drought_d2_d4", "noaa_severe_tornado_count", "usgs_mean_annual_runoff_cfs",
        # Agriculture & Food (USDA NASS / ERS)
        "usda_harvested_cropland_acres_pct", "usda_food_desert_pop_pct",
        # Toxics & Water (EPA TRI / SDWIS)
        "epa_tri_total_releases_lbs", "sdwis_health_violations_count",
        # Telecom & Digital (FCC BDC / ASR)
        "fcc_unserved_broadband_pct", "fcc_gigabit_fiber_coverage_pct",
        # Innovation & Labor (USPTO / BLS / SEC)
        "uspto_patents_granted_per_10k", "bls_stem_tech_employment_share_pct", "sec_corporate_hq_count",
        # Crime & Substance (FBI / CDC)
        "fbi_violent_crime_rate_per_100k", "cdc_overdose_mortality_rate_per_100k",
        # Public Health & Housing (CDC / HUD)
        "cdc_asthma_prevalence_pct", "hud_severe_cost_burden_renters_pct",
        # Politics & Wealth
        "dem_margin_2020", "swing_2012_2020", "median_hh_income", "poverty_pct"
    ]
    
    valid_cols = [c for c in analysis_cols if c in df_harmonized.columns]
    corr = df_harmonized[valid_cols].corr()
    
    fig, ax = plt.subplots(figsize=(22, 18))
    mask = np.triu(np.ones_like(corr, dtype=bool))
    
    cmap = sns.diverging_palette(230, 20, as_cmap=True)
    sns.heatmap(
        corr, mask=mask, cmap=cmap, vmax=0.85, vmin=-0.85, center=0,
        square=True, linewidths=0.5, cbar_kws={"shrink": 0.8},
        annot=True, fmt=".2f", annot_kws={"size": 6.8}, ax=ax
    )
    
    ax.set_title(
        "Cross-Domain Correlation Matrix Across All 42 Public Datasets (Energy, Climate, Health, Tech & Society)",
        fontsize=16, fontweight="bold", pad=15
    )
    plt.tight_layout()
    return fig


def plot_top_association_rules_bar(rules_df: pd.DataFrame, top_n: int = 12) -> plt.Figure:
    """Generates a ranked horizontal bar chart of the highest-lift cross-domain association rules."""
    setup_style()
    top_rules = rules_df.head(top_n).copy()
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    y_pos = np.arange(len(top_rules))
    lifts = top_rules["lift"].values
    
    # Color bars by confidence
    confidences = top_rules["confidence"].values
    colors = plt.cm.viridis(confidences / max(confidences))
    
    bars = ax.barh(y_pos, lifts, color=colors, edgecolor="black", linewidth=0.8, height=0.65)
    
    # Labels
    rule_labels = []
    for _, r in top_rules.iterrows():
        ant = r["antecedents_str"][:38] + "..." if len(r["antecedents_str"]) > 38 else r["antecedents_str"]
        con = r["consequents_str"][:32] + "..." if len(r["consequents_str"]) > 32 else r["consequents_str"]
        rule_labels.append(f"[{r['antecedent_domains']}] {ant}  ==>  [{r['consequent_domains']}] {con}")
        
    ax.set_yticks(y_pos)
    ax.set_yticklabels(rule_labels, fontsize=9.5, fontweight="bold")
    ax.invert_yaxis()
    ax.set_xlabel("Rule Lift (Strength of Cross-Domain Association Beyond Chance)", fontsize=11, fontweight="bold")
    ax.set_title("Top Discovered Cross-Domain Association Rules (Ranked by Lift & Confidence)", fontsize=14, fontweight="bold")
    
    # Add data annotations on bars
    for i, bar in enumerate(bars):
        lift_val = lifts[i]
        conf_val = confidences[i]
        supp_val = top_rules["support"].iloc[i]
        ax.text(
            bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2,
            f"Lift: {lift_val:.2f} | Conf: {conf_val:.1%} | Supp: {supp_val:.1%}",
            va="center", fontsize=8.5, fontweight="bold", color="#333333"
        )
        
    ax.set_xlim(0, max(lifts) * 1.35)
    plt.tight_layout()
    return fig


def plot_colocation_scatter(
    df_harmonized: pd.DataFrame,
    x_col: str,
    y_col: str,
    size_col: str,
    hue_col: str,
    title: str,
    x_label: str,
    y_label: str
) -> plt.Figure:
    """Scatter plot highlighting non-obvious colocation relationships between two disparate domains."""
    setup_style()
    fig, ax = plt.subplots(figsize=(12, 8))
    
    scatter = sns.scatterplot(
        data=df_harmonized, x=x_col, y=y_col, size=size_col, hue=hue_col,
        sizes=(40, 280), alpha=0.75, palette="tab10", ax=ax, edgecolor="black", linewidth=0.7
    )
    
    # Annotate outlier representative counties
    for _, row in df_harmonized.head(10).iterrows():
        ax.annotate(
            f"{row['county_name']}, {row['state_abbr']}",
            (row[x_col], row[y_col]),
            xytext=(6, 4), textcoords="offset points", fontsize=8.5, fontweight="bold"
        )
        
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.set_xlabel(x_label, fontsize=11)
    ax.set_ylabel(y_label, fontsize=11)
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    return fig
