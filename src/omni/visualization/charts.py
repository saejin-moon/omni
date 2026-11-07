"""Comprehensive visualization suite for exploratory data analysis, PCA biplots, radar charts, and maps."""

from typing import List, Optional, Tuple
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium import plugins
from sklearn.preprocessing import MinMaxScaler


def setup_plot_style():
    """Configures clean, modern typography and styling for all Matplotlib/Seaborn figures."""
    sns.set_theme(style="whitegrid", palette="deep")
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Helvetica", "Arial"]
    plt.rcParams["axes.edgecolor"] = "#cccccc"
    plt.rcParams["axes.linewidth"] = 0.8
    plt.rcParams["grid.color"] = "#eeeeee"
    plt.rcParams["grid.linestyle"] = "--"


def plot_national_landscape(gdf: gpd.GeoDataFrame) -> plt.Figure:
    """Generates a 4-panel multi-distribution plot across all 5 macro-regions."""
    setup_plot_style()
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Median Household Income by Region
    sns.boxplot(
        data=gdf, x="macro_region", y="median_hh_income", hue="macro_region", legend=False,
        palette="Set2", showmeans=True, meanprops={"marker":"o", "markerfacecolor":"white"}
    )
    axes[0, 0].set_title("Median Household Income Distribution by Macro-Region", fontsize=13, fontweight="bold")
    axes[0, 0].set_ylabel("Median Household Income ($)")
    axes[0, 0].set_xlabel("")
    axes[0, 0].yaxis.set_major_formatter("${x:,.0f}")
    axes[0, 0].tick_params(axis="x", rotation=15)

    # 2. 2020 Democratic Margin by Region
    sns.violinplot(
        data=gdf, x="macro_region", y="dem_margin_2020", hue="macro_region", legend=False,
        palette="coolwarm", cut=0, inner="quartile"
    )
    axes[0, 1].axhline(0, color="gray", linestyle="--", alpha=0.7)
    axes[0, 1].set_title("2020 Presidential Margin (Dem % - GOP %)", fontsize=13, fontweight="bold")
    axes[0, 1].set_ylabel("Partisan Margin (+Dem / -GOP)")
    axes[0, 1].set_xlabel("")
    axes[0, 1].tick_params(axis="x", rotation=15)

    # 3. RUCC Urban vs Rural Population Density
    gdf_plot = gdf.copy()
    gdf_plot["log_density"] = np.log10(gdf_plot["pop_density_sq_km"].clip(lower=0.1))
    sns.scatterplot(
        data=gdf_plot, x="rucc_code", y="log_density", hue="macro_region",
        alpha=0.6, s=35, ax=axes[1, 0], palette="Set1"
    )
    axes[1, 0].set_title("USDA RUCC (1=Metro Core to 9=Remote) vs Log Density", fontsize=13, fontweight="bold")
    axes[1, 0].set_xlabel("RUCC Code (1=Large Metro, 9=Completely Rural)")
    axes[1, 0].set_ylabel("Log10 Population Density (per km²)")
    axes[1, 0].legend(title="Macro Region", loc="upper right")

    # 4. 8-Year Political Swing (2012 -> 2020)
    sns.histplot(
        data=gdf, x="swing_2012_2020", hue="macro_region", multiple="stack",
        bins=40, ax=axes[1, 1], palette="tab10"
    )
    axes[1, 1].axvline(0, color="red", linestyle="--", alpha=0.8, label="No Swing")
    axes[1, 1].set_title("8-Year Shift in Democratic Margin (2012 to 2020)", fontsize=13, fontweight="bold")
    axes[1, 1].set_xlabel("Shift in Dem Margin (+ Shift to Dem / - Shift to GOP)")
    axes[1, 1].set_ylabel("Count of Counties")

    plt.tight_layout()
    return fig


def plot_regional_pca_biplot(
    gdf_all: gpd.GeoDataFrame,
    cohort_region: gpd.GeoDataFrame,
    region_name: str
) -> plt.Figure:
    """Generates a 2D PCA Biplot highlighting the 15 selected counties against all regional counties."""
    setup_plot_style()
    fig, ax = plt.subplots(figsize=(14, 9))
    
    # Filter regional all counties
    reg_all = gdf_all[gdf_all["macro_region"] == region_name].copy()
    
    # Plot background points
    ax.scatter(
        reg_all["centroid_lon"], reg_all["centroid_lat"],
        c="#dddddd", alpha=0.4, s=20, label="All Regional Counties"
    )
    
    # Plot selected 15 archetypes with distinct colors
    palette = sns.color_palette("tab20", len(cohort_region))
    for i, (_, row) in enumerate(cohort_region.iterrows()):
        marker = "*" if row["is_regional_centroid"] else "o"
        size = 180 if row["is_regional_centroid"] else 110
        ax.scatter(
            row["centroid_lon"], row["centroid_lat"],
            color=palette[i], marker=marker, s=size, edgecolors="black", linewidths=1.2,
            label=f"{row['county_name']}, {row['state_abbr']}: {row['archetype_label'][:26]}"
        )
        ax.annotate(
            f"{row['county_name']}",
            (row["centroid_lon"] + 0.15, row["centroid_lat"] + 0.1),
            fontsize=8.5, fontweight="bold"
        )
        
    ax.set_title(f"Spatial Distribution of 15 Archetypal Counties in {region_name}", fontsize=14, fontweight="bold")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8.5)
    plt.tight_layout()
    return fig


def plot_county_fingerprint_radar(cohort_region: gpd.GeoDataFrame, region_name: str) -> plt.Figure:
    """Creates a multi-axis Radar / Spider chart comparing 6 diverse archetypes from the 15 selected."""
    # Pick 6 diverse counties from the 15
    sample_counties = cohort_region.head(6).copy()
    
    radar_metrics = [
        ("pop_density_sq_km", "Density"),
        ("median_hh_income", "Income"),
        ("racial_diversity_index", "Diversity"),
        ("age29andunder_pct", "Youth"),
        ("age65andolder_pct", "Seniors"),
        ("turnout_rate_2020", "Turnout"),
        ("dem_margin_2020", "Dem Lean"),
        ("pop_growth_pct", "Growth"),
    ]
    
    scaler = MinMaxScaler()
    scaled_vals = scaler.fit_transform(sample_counties[[m[0] for m in radar_metrics]])
    
    labels = [m[1] for m in radar_metrics]
    num_vars = len(labels)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    palette = sns.color_palette("bright", len(sample_counties))
    
    for i, (_, row) in enumerate(sample_counties.iterrows()):
        values = scaled_vals[i].tolist()
        values += values[:1]
        ax.plot(angles, values, color=palette[i], linewidth=2, label=f"{row['county_name']} ({row['archetype_label'][:22]})")
        ax.fill(angles, values, color=palette[i], alpha=0.15)
        
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_thetagrids(np.degrees(angles[:-1]), labels, fontsize=10, fontweight="bold")
    ax.set_ylim(0, 1.05)
    ax.set_title(f"Multi-Dimensional Fingerprints: Diverse Archetypes in {region_name}", fontsize=13, fontweight="bold", y=1.08)
    ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.1), fontsize=9)
    plt.tight_layout()
    return fig


def plot_political_swing_slopegraph(cohort_region: gpd.GeoDataFrame, region_name: str) -> plt.Figure:
    """Generates a 3-cycle presidential margin slopegraph (2012 -> 2016 -> 2020)."""
    setup_plot_style()
    fig, ax = plt.subplots(figsize=(12, 8))
    
    x_points = [2012, 2016, 2020]
    
    for _, row in cohort_region.iterrows():
        y_points = [row["dem_margin_2012"], row["dem_margin_2016"], row["dem_margin_2020"]]
        
        # Color line by 2020 lean
        line_color = "#2b83ba" if row["dem_margin_2020"] > 0 else "#d7191c"
        alpha = 0.85 if row["is_regional_centroid"] else 0.65
        lw = 2.8 if row["is_regional_centroid"] else 1.8
        
        ax.plot(x_points, y_points, marker="o", color=line_color, linewidth=lw, alpha=alpha)
        
        # Label endpoints
        ax.text(2020.1, y_points[2], f"{row['county_name']} ({y_points[2]:+.1%})", fontsize=8, va="center")
        
    ax.axhline(0, color="gray", linestyle="--", alpha=0.7)
    ax.set_xticks(x_points)
    ax.set_xticklabels(["2012 (Obama vs Romney)", "2016 (Clinton vs Trump)", "2020 (Biden vs Trump)"], fontsize=11, fontweight="bold")
    ax.set_ylabel("Democratic Presidential Margin (+Dem / -GOP)", fontsize=11)
    ax.set_title(f"3-Cycle Partisan Trajectories (2012 -> 2016 -> 2020): 15 Counties in {region_name}", fontsize=13, fontweight="bold")
    ax.yaxis.set_major_formatter("{x:+.0%}")
    plt.tight_layout()
    return fig


def create_interactive_folium_map(
    cohort_gdf: gpd.GeoDataFrame,
    output_html: Optional[str] = "data/processed/cohort_75_interactive_map.html"
) -> folium.Map:
    """Creates a full-featured interactive Folium map rendering true irregular county polygons.
    
    Displays exact boundary geometries, popups with demographic and political cards,
    and H3 polyfill stats for all 75 selected counties.
    """
    # Center map on continental USA
    m = folium.Map(location=[38.5, -96.5], zoom_start=4, tiles="OpenStreetMap")
    
    region_colors = {
        "Northeast": "#377eb8",
        "Midwest": "#4daf4a",
        "South / Southeast": "#e41a1c",
        "Southwest": "#ff7f00",
        "Northwest": "#984ea3",
    }
    
    # Add FeatureGroups per region
    for region_name, color in region_colors.items():
        reg_group = folium.FeatureGroup(name=f"{region_name} (15 Counties)")
        reg_counties = cohort_gdf[cohort_gdf["macro_region"] == region_name]
        
        for _, row in reg_counties.iterrows():
            geom = row.geometry
            fips = row["fips"]
            name = row["county_name"]
            state = row["state_abbr"]
            archetype = row["archetype_label"]
            pop_str = f"{int(row['pop_2023']):,}"
            inc_str = f"${int(row['median_hh_income']):,}"
            dem_margin = f"{row['dem_margin_2020']:+.1%}"
            rucc = f"RUCC {row['rucc_code']}"
            h3_count = row["h3_cell_count"]
            
            popup_html = f"""
            <div style="font-family: Arial; font-size: 12px; width: 260px;">
                <h4 style="margin: 0; color: {color};">{name}, {state}</h4>
                <b>FIPS:</b> {fips} | <b>Region:</b> {region_name}<br>
                <b>Archetype:</b> <span style="background-color: #f0f0f0; padding: 2px 4px;">{archetype}</span><br>
                <hr style="margin: 6px 0;">
                <b>Population (2023):</b> {pop_str}<br>
                <b>Median Income:</b> {inc_str}<br>
                <b>Poverty Rate:</b> {row['poverty_pct']:.1f}%<br>
                <b>2020 Dem Margin:</b> {dem_margin}<br>
                <b>8-Year Swing (2012-20):</b> {row['swing_2012_2020']:+.1%}<br>
                <b>Urban-Rural:</b> {rucc} ({row['rucc_desc'][:25]}...)<br>
                <b>H3 Polyfill Hexagons:</b> {h3_count} cells<br>
                <b>Bounding Box:</b> [{row['min_lon']:.2f}, {row['min_lat']:.2f}, {row['max_lon']:.2f}, {row['max_lat']:.2f}]
            </div>
            """
            
            # Add True Polygon Layer (GeoJSON)
            geo_j = folium.GeoJson(
                geom.__geo_interface__,
                style_function=lambda x, c=color: {
                    "fillColor": c,
                    "color": "#222222",
                    "weight": 1.5,
                    "fillOpacity": 0.45,
                },
                highlight_function=lambda x: {
                    "weight": 3,
                    "fillOpacity": 0.75,
                },
                tooltip=f"{name}, {state} ({archetype})",
                popup=folium.Popup(popup_html, max_width=300)
            )
            geo_j.add_to(reg_group)
            
            # Centroid Marker
            marker_icon = "star" if row["is_regional_centroid"] else "info-sign"
            marker_color = "darkred" if row["is_regional_centroid"] else "blue"
            folium.Marker(
                location=[row["centroid_lat"], row["centroid_lon"]],
                icon=folium.Icon(icon=marker_icon, color=marker_color, prefix="glyphicon"),
                tooltip=f"{name}, {state} (Centroid: {row['centroid_lat']:.2f}, {row['centroid_lon']:.2f})"
            ).add_to(reg_group)
            
        reg_group.add_to(m)
        
    folium.LayerControl().add_to(m)
    
    if output_html:
        from pathlib import Path
        Path(output_html).parent.mkdir(parents=True, exist_ok=True)
        m.save(str(output_html))
        print(f"Interactive map saved to {output_html}")
        
    return m
