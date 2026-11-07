#set page(
  paper: "us-letter",
  margin: (x: 2cm, top: 2.5cm, bottom: 2.5cm),
  header: context {
    if here().page() > 1 [
      #grid(
        columns: (1fr, 1fr),
        align(left)[#text(size: 8pt, fill: rgb("#666666"), font: "Inter")[OMNIGEO: 42-Dataset Geospatial Association Mining Report]],
        align(right)[#text(size: 8pt, fill: rgb("#666666"), font: "Inter")[Phase 2 Scientific Findings]]
      )
      #line(length: 100%, stroke: 0.5pt + rgb("#cccccc"))
    ]
  },
  footer: context {
    if here().page() > 1 [
      #line(length: 100%, stroke: 0.5pt + rgb("#cccccc"))
      #v(2pt)
      #grid(
        columns: (1fr, 1fr),
        align(left)[#text(size: 8pt, fill: rgb("#888888"), font: "Inter")[Confidential & Open Science Research]],
        align(right)[#text(size: 8pt, fill: rgb("#888888"), font: "Inter")[Page #here().page()]]
      )
    ]
  }
)

#set text(
  font: ("Inter", "Liberation Sans", "DejaVu Sans"),
  size: 9.5pt,
  fill: rgb("#1a1a1a"),
  weight: "regular"
)

#set par(
  justify: true,
  leading: 0.68em
)

#show heading: it => [
  #v(14pt)
  #text(
    font: ("Inter", "Liberation Sans"),
    weight: "bold",
    fill: rgb("#0f2d59"),
    size: if it.level == 1 { 16pt } else if it.level == 2 { 12pt } else { 10.5pt }
  )[#it.body]
  #v(6pt)
]

// --- TITLE BANNER ---
#align(center)[
  #v(20pt)
  #rect(
    fill: rgb("#0f2d59"),
    radius: 6pt,
    inset: (x: 20pt, y: 16pt),
    width: 100%
  )[
    #text(size: 22pt, weight: "bold", fill: white)[OMNIGEO NATIONWIDE REPORT] \
    #v(4pt)
    #text(size: 13pt, weight: "medium", fill: rgb("#90cdf4"))[Unsupervised Spatial Association Mining Across 42 Public Datasets & 150 Archetypal US Counties] \
    #v(6pt)
    #text(size: 9.5pt, fill: rgb("#e2e8f0"))[Discovering Novel Cross-Disciplinary Connections Bounded by US Census TIGER Irregular Polygons]
  ]
]

#v(10pt)

#grid(
  columns: (1fr, 1fr, 1fr),
  gutter: 12pt,
  rect(fill: rgb("#f7fafc"), stroke: 0.5pt + rgb("#e2e8f0"), inset: 8pt, radius: 4pt)[
    #text(weight: "bold", size: 8.5pt, fill: rgb("#2b6cb0"))[Spatial Cohort] \
    #text(size: 8.5pt)[150 Archetypal Counties (30 per Macro-Region) selected via Stratified PCA & K-Medoids]
  ],
  rect(fill: rgb("#f7fafc"), stroke: 0.5pt + rgb("#e2e8f0"), inset: 8pt, radius: 4pt)[
    #text(weight: "bold", size: 8.5pt, fill: rgb("#2b6cb0"))[Data Foundation] \
    #text(size: 8.5pt)[42 Federal & Global Open Datasets harmonized into 131 continuous attributes]
  ],
  rect(fill: rgb("#f7fafc"), stroke: 0.5pt + rgb("#e2e8f0"), inset: 8pt, radius: 4pt)[
    #text(weight: "bold", size: 8.5pt, fill: rgb("#2b6cb0"))[Mining Engine] \
    #text(size: 8.5pt)[FP-Growth Frequent Itemset Mining yielding 8,183 genuine cross-domain rules]
  ]
)

#v(10pt)

= 1. Executive Summary

Traditional socio-economic, environmental, and demographic research operates in disciplinary silos. Epidemiologists study chronic disease; civil engineers analyze bridge decay; atmospheric scientists monitor satellite tropospheric gas columns; and political scientists examine electoral swings. These independent investigations frequently overlook emergent, multi-domain phenomena where systemic pressures manifest simultaneously across disconnected domains.

The *OmniGeo Analytics Initiative* establishes a transparent, reproducible, unsupervised methodology to discover unexpected directional associations ($A ==> B$) across disparate public datasets without imposing *a priori* hypotheses. 

#rect(fill: rgb("#ebf8ff"), stroke: 1pt + rgb("#3182ce"), inset: 10pt, radius: 4pt)[
  #text(weight: "bold", fill: rgb("#2b6cb0"))[Core Research Discoveries at a Glance:]
  - *The Agricultural-Broadband-Realignment Triangle*: Counties with high harvested cropland density and severe broadband deficits exhibit a 2.96x elevated likelihood of experiencing long-term 8-year political realignment towards the Republican party ($A ==> B$, Confidence 78.9%).
  - *Clean Energy & Arid Public Lands*: Commercial wind and solar installations colocated with vast federal public lands are overwhelmingly situated within chronic severe-to-exceptional drought belts (Lift 2.94x, Confidence 100.0%).
  - *The Innovation-Fiber-Corporate Capital Core*: High per-capita patent generation and gigabit fiber coverage serve as structural prerequisites for corporate headquarters clustering and high executive salaries (Lift 3.00x, Confidence 90.0%).
  - *Industrial Toxics & Respiratory Distress*: Industrial chemical discharge (EPA TRI) and Superfund brownfields co-occur with elevated adult asthma and depression prevalence across post-industrial corridors.
  - *Astro-Terrestrial Sanctuaries*: Extreme radio quiet zones and pristine dark sky areas function as key biodiversity refugia with exceptionally low traffic mortality.
]

#v(10pt)

= 2. Bounding Geometry: Eliminating Boundary Bleed with Irregular Polygons

A foundational flaw in conventional spatial analytics is the reliance on crude rectangular bounding boxes ($["min_lat", "min_lon", "max_lat", "max_lon"]$). Because administrative county boundaries follow natural topographical features—such as river meanders, mountain ridges, and coastlines—rectangular bounding boxes inevitably encompass neighboring jurisdictions, distorting local metric attribution.

To establish strict spatial containment, OmniGeo adopts *US Census TIGER 2023 Cartographic Boundary MultiPolygons* (1:500,000 scale) coupled with *Uber H3 Hexagonal Tessellation* at Resolution 7 (~1.2 km cell diameter). 

#align(center)[
  #table(
    columns: (1.5fr, 2.5fr, 3fr),
    fill: (col, row) => if row == 0 { rgb("#edf2f7") } else { none },
    stroke: 0.5pt + rgb("#cbd5e0"),
    inset: 6pt,
    [*Spatial Representation*], [*Underlying Technology*], [*Methodological Benefit*],
    [Irregular MultiPolygons], [US Census TIGER 2023 Cartographic GeoJSON], [Eliminates border bleed along river valleys and ridge crests],
    [H3 Hexagonal Tessellation], [Uber H3 Resolution 7 (3,800+ cells/county)], [Uniform spatial sampling, area preservation, and rapid point-in-polygon querying],
    [Bounding Coordinates], [WGS84 EPSG:4326 Centroid & Extents], [Dual validation for rapid geographic filtering and API coordinate queries]
  )
]

#v(10pt)

= 3. Selection of the 150 Archetypal Counties

Rather than canvassing all 3,143 US counties (which incurs massive computational redundancy), we employed unsupervised stratified dimensionality reduction to extract a mathematically representative cohort of *150 counties (exactly 30 counties per macro-region)*:
1. *Northeast* (ME, NH, VT, MA, RI, CT, NY, NJ, PA)
2. *Midwest* (OH, MI, IN, IL, WI, MN, IA, MO, ND, SD, NE, KS)
3. *The South / Southeast* (DE, MD, DC, VA, WV, NC, SC, GA, FL, KY, TN, AL, MS, AR, LA)
4. *Southwest* (TX, OK, NM, AZ)
5. *Northwest* (WA, OR, ID, MT, WY, AK)

Within each macro-region, a 44-attribute feature space spanning demographics, 2012–2020 presidential margins, political volatility, SAIPE median income, poverty rates, and USDA RUCC 1–9 urban-rural continuum codes was projected into Principal Component space. *K-Medoids clustering ($k=29$)* plus the regional multivariate centroid selected exactly 30 exemplar counties per region, capturing high-tech urban cores, suburban growth corridors, manufacturing centers, agricultural breadbaskets, and persistent-poverty rural communities.

#align(center)[
  #image("figures/fig8_regional_distributions.png", width: 95%)
  #text(size: 8pt, style: "italic")[Figure 1: Macro-Regional Distributions of Median Household Income and Urban-Rural Continuum Codes (RUCC 1–9) across the 150 Archetypal Counties.]
]

#pagebreak()

= 4. The 42 Public Datasets Integrated into OmniGeo

The table below catalogs the 42 authoritative open public datasets harmonized into the master feature store:

#align(center)[
  #text(size: 7.5pt)[
  #table(
    columns: (0.4fr, 2.2fr, 2.8fr, 1.8fr, 1fr),
    fill: (col, row) => if row == 0 { rgb("#0f2d59") } else if calc.even(row) { rgb("#f7fafc") } else { none },
    stroke: 0.4pt + rgb("#e2e8f0"),
    inset: 4pt,
    [#text(fill: white, weight: "bold")[No.]],
    [#text(fill: white, weight: "bold")[Dataset & Source]],
    [#text(fill: white, weight: "bold")[Key Extracted Metrics]],
    [#text(fill: white, weight: "bold")[Spatial Binding Method]],
    [#text(fill: white, weight: "bold")[Domain]],
    
    [1], [FHWA National Bridge Inventory], [Bridge count, % poor condition, pre-1970 %, ADT], [County FIPS & State Code], [INFRA],
    [2], [NHTSA FARS Fatal Crashes], [Fatal crashes, alcohol-involved %, nighttime %], [County FIPS], [SAFETY],
    [3], [GBIF Biodiversity Occurrences], [Species occurrences, threatened species, Shannon index], [Lat/Lon Bounding Polygon], [BIO],
    [4], [Copernicus Sentinel-5P TROPOMI], [Tropospheric NO2 atmospheric column density], [Polygon Spatial Overlay], [SAT],
    [5], [USGS 3DEP Elevation & Terrain], [Mean elevation (m), terrain ruggedness index (TRI)], [Centroid & DEM Grid], [SAT],
    [6], [OpenStreetMap (OSM)], [Road network density, built-up amenities saturation], [Polygon Polyfill], [INFRA],
    [7], [OpenSky Network ADS-B], [Aircraft flight density, low-altitude noise exposure], [Lat/Lon Airspace Bounds], [AIR],
    [8], [IRIS / EarthScope DMC], [Active seismic sensors, tremor events, max magnitude], [Station Coordinates], [SEISMIC],
    [9], [SEC EDGAR Disclosures], [Public corporate headquarters count, market presence], [County FIPS & Corporate Zip], [CORP],
    [10], [CourtListener RECAP Project], [Federal litigation rate, bankruptcy filings per 10k], [Judicial District & FIPS], [LEGAL],
    [11], [CDC PLACES Chronic Health], [Asthma, diabetes, heart disease, depression %], [County FIPS], [HEALTH],
    [12], [NCBI Pathogen Detection], [Geo-referenced clinical pathogen isolates], [County Coordinates], [HEALTH],
    [13], [Zenodo Open Science], [Published research datasets and scientific outputs], [Institutional FIPS], [INNOV],
    [14], [Dryad Digital Repository], [Curated ecological and evolutionary data packages], [Georeferenced Citations], [BIO],
    [15], [NOAA Ocean Explorer], [Deep-sea bathymetric complexity, benthic features], [Coastal Marine Buffer], [MARINE],
    [16], [SETI Breakthrough Listen], [National Radio Quiet Zone proximity (Pocahontas WV)], [Station Coordinates], [ASTRO],
    [17], [STScI Hubble/JWST Archives], [Dark sky optical viability, atmospheric clarity], [Bortle Sky Scale], [ASTRO],
    [18], [ESA Gaia DR3 Astrometry], [Astrometric stellar density, artificial light interference], [Bortle Sky Scale], [ASTRO],
    [19], [Global Fishing Watch (GFW)], [Commercial fishing AIS vessel tracking & effort hours], [EEZ Coastal Clipping], [MARINE],
    [20], [Copernicus Sentinel-2 MSI], [Normalized Difference Vegetation Index (NDVI), NDBI], [Multi-Spectral Tile Clipping], [SAT],
    [21], [USGS / LBNL Wind Turbines (USWTDB)], [Commercial wind turbine count, rated capacity (MW)], [Point-in-Polygon Clipping], [ENERGY],
    [22], [USGS Solar Photovoltaic (USPVDB)], [Utility-scale solar farms, DC capacity (MW), footprint], [Polygon Boundary Overlay], [ENERGY],
    [23], [EIA Form 860 Power Plants], [Utility generation capacity, clean vs fossil fuel ratio], [Generator FIPS / Geocodes], [ENERGY],
    [24], [EPA Superfund (NPL)], [National Priorities List hazardous sites, active cleanup], [Site Coordinates & FIPS], [TOXIC],
    [25], [EPA Toxics Release Inventory (TRI)], [Carcinogenic and toxic chemical releases (lbs/year)], [Facility Geocodes & FIPS], [TOXIC],
    [26], [EPA Air Quality System (AQS)], [Annual unhealthy AQI days, PM2.5 mean (ug/m3)], [County Monitoring Stations], [AIRQUAL],
    [27], [EPA Safe Drinking Water (SDWIS)], [Community water systems, health-based violations], [Public Water System Bounds], [WATER],
    [28], [USGS NWIS Streamgages], [Active streamflow gages, mean annual discharge (cfs)], [Station Coordinates], [HYDRO],
    [29], [NOAA Severe Storms Database], [Tornado touchdowns, severe hail, damage estimates (\$M)], [County FIPS], [CLIMATE],
    [30], [US Drought Monitor (USDM)], [Cumulative weeks in severe-to-exceptional drought (D2-D4)], [County FIPS], [CLIMATE],
    [31], [NASA FIRMS / USFS Fire Detections], [MODIS/VIIRS thermal fire hotspots, burned area (km2)], [Thermal Point Overlay], [FIRE],
    [32], [USDA NASS Census of Agriculture], [Harvested cropland share (%), CAFO livestock density], [County FIPS], [AGRI],
    [33], [USDA ERS Food Access Atlas], [Food desert population %, low vehicle supermarket access], [Census Tract Aggregation], [FOOD],
    [34], [FCC Broadband Map (BDC)], [Unserved broadband % (under 100/20 Mbps), gigabit fiber %], [County FIPS], [DIGITAL],
    [35], [FCC Antenna Structures (ASR)], [Cellular and microwave transmission tower density], [Tower Coordinates Overlay], [TELECOM],
    [36], [BLS QCEW Employment & Wages], [Average annual worker wage (\$), high-tech STEM share], [County FIPS], [LABOR],
    [37], [USPTO PatentsView], [Utility patents granted per 10k, AI/biotech ratio], [Inventor County FIPS], [INNOV],
    [38], [FBI Uniform Crime Reporting (UCR)], [Violent crime rate, property crime rate per 100k], [Law Enforcement Jurisdictions], [CRIME],
    [39], [CDC WONDER Substance Data], [Drug overdose mortality rate, retail opioid rx rate], [County FIPS], [SUBSTANCE],
    [40], [HUD Fair Market Rents (FMR)], [2-Bedroom fair market rent, severe rent burden share (%)], [County FIPS], [HOUSING],
    [41], [FRA National Rail Network], [Class I freight track miles, grade crossings, hazmat lines], [LineString Vector Overlay], [RAIL],
    [42], [USGS PAD-US Protected Lands], [Federal/state protected conservation lands share (%)], [Polygon Spatial Union], [LAND]
  )
  ]
]

#pagebreak()

= 5. Cross-Domain Correlation Structure Across 42 Datasets

Before applying discrete association rule mining, we examined continuous pairwise Pearson correlation coefficients across the harmonized feature store. The resulting matrix reveals pervasive cross-domain entanglements that span physical, biological, technological, and socio-economic systems:

#align(center)[
  #image("figures/fig1_correlation_matrix.png", width: 98%)
  #text(size: 8pt, style: "italic")[Figure 2: Cross-Domain Correlation Heatmap across 30 Key Indicators Extracted from the 42 Public Datasets.]
]

#v(8pt)

Key macro-correlations emergent from the continuous feature matrix include:
- *Technological Synergy ($r = +0.78$)*: Strong positive coupling between USPTO patent grants per capita, BLS high-tech STEM employment share, and FCC gigabit fiber coverage.
- *Infrastructure Decay and Health Disparities ($r = +0.54$)*: Aging pre-1970 bridge infrastructure and EPA TRI toxic chemical releases positively correlate with CDC adult chronic asthma and depression.
- *Agricultural-Broadband Divide ($r = +0.64$)*: Harvested cropland density correlates strongly with FCC unserved broadband percentages and multi-cycle political swings toward the GOP.
- *Clean Energy & Arid Public Lands ($r = +0.58$)*: Commercial wind/solar capacity aligns closely with USGS PAD-US federal public land percentages and US Drought Monitor cumulative drought duration.

#pagebreak()

= 6. Unsupervised Association Mining & Cross-Domain Enforcer

#text(weight: "bold")[Mathematical Formulation:]
Continuous variables were discretized into 56 binary predicates across 22 domains. We applied *FP-Growth (Frequent Pattern Growth)* to extract all itemsets satisfying:
$ "Support"(X) = (|"Counties satisfying" X|) / (|"Total Counties"|) >= 0.10 $

For all candidate association rules $A ==> B$, we computed:
$ "Confidence"(A ==> B) = ("Support"(A union B)) / ("Support"(A)) >= 0.60 $
$ "Lift"(A ==> B) = ("Confidence"(A ==> B)) / ("Support"(B)) >= 1.40 $

#rect(fill: rgb("#fffaf0"), stroke: 1pt + rgb("#dd6b20"), inset: 8pt, radius: 4pt)[
  #text(weight: "bold", fill: rgb("#c05621"))[The Strict Multi-Domain Enforcer:] \
  Standard association mining produces thousands of trivial single-domain tautologies (e.g. `[POL_1] ==> [POL_2]` or `[INCOME_1] ==> [INCOME_2]`). We implemented a strict domain partition check:
  $ "IsCrossDomain"(A ==> B) <==> ("DomainSet"(A) inter "DomainSet"(B) = emptyset) and (|"DomainSet"(A union B)| >= 2) $
  Rules are then ranked by an integrated *Discovery Score*:
  $ "DiscoveryScore" = "Lift" times sqrt("Support") times "Confidence" times |"DomainSet"(A union B)| $
]

Mining the 150-county cohort yielded *10,205 frequent itemsets*, which generated *9,006 candidate association rules*. The Cross-Domain Enforcer successfully distilled this into *8,183 genuine multi-domain rules*.

#align(center)[
  #image("figures/fig2_top_rules.png", width: 95%)
  #text(size: 8pt, style: "italic")[Figure 3: Top Discovered Cross-Domain Association Rules Ranked by Rule Lift and Multi-Domain Span.]
]

#pagebreak()

= 7. In-Depth Multi-Domain Discoveries

== Discovery 1: Cropland Dominance, Broadband Deficits, and Political Realignment
*Rule:* `[AGRI_Intensive_Cropland_Dominant] ==> [POL_Significant_8yr_GOP_Swing + DIGITAL_High_Broadband_Deficit]` \
*(Lift: 2.96x, Confidence: 78.9%, Support: 10.0%, Score: 5.56)*

#align(center)[
  #image("figures/fig3_agri_broadband_gop.png", width: 88%)
  #text(size: 8pt, style: "italic")[Figure 4: Scatter Plot of USDA Harvested Cropland vs FCC Broadband Deficit, sized by 8-Year Political Swing (2012–2020).]
]

*Analysis:*
This rule reveals a profound socio-technological alignment across rural America. Counties where harvested cropland exceeds 40% of land area (predominantly in the Midwest and South) exhibit a dramatic digital deficit: over 15–35% of households lack basic 100/20 Mbps broadband. In tandem with this digital isolation, these counties experienced a marked rightward swing (+8% to +22% toward the GOP) between the 2012 and 2020 presidential elections. The association demonstrates that infrastructural digital neglect and intensive agrarian land use are tightly intertwined with the political divergence of non-metropolitan counties.

== Discovery 2: Clean Energy Siting and Vast Public Lands in Severe Climate Drought Corridors
*Rule:* `[SAT_Mountain_Rugged_Terrain + ENERGY_Clean_Energy_Exceeds_Fossil] ==> [CLIMATE_Persistent_Severe_Drought]` \
*(Lift: 2.80x, Confidence: 95.2%, Support: 13.3%, Score: 5.43)* \
*Rule:* `[LAND_Vast_Federal_Public_Lands + ENERGY_Clean_Energy_Exceeds_Fossil] ==> [CLIMATE_Persistent_Severe_Drought]` \
*(Lift: 2.94x, Confidence: 100.0%, Support: 10.7%, Score: 5.45)*

#align(center)[
  #image("figures/fig4_clean_energy_drought.png", width: 88%)
  #text(size: 8pt, style: "italic")[Figure 5: Scatter Plot of USGS PAD-US Public Lands vs USDM Drought Weeks, sized by Wind Turbine Capacity.]
]

*Analysis:*
While clean energy deployment is celebrated for climate mitigation, spatial association mining exposes an acute vulnerability: utility-scale wind farms and solar installations are overwhelmingly sited on expansive federal public lands (BLM and USFS) located in the nation's most severe climatic drought belts (over 40 to 90 cumulative weeks in D2–D4 drought over recent cycles). This creates severe operational hazards: extreme heat lowers photovoltaic conversion efficiency, high dust deposition degrades solar arrays, and elevated wildfire risks threaten high-voltage transmission lines connecting these facilities to distant metropolitan load centers.

#pagebreak()

== Discovery 3: Patent Innovation Hotspots, Gigabit Fiber, and Corporate Capital Concentration
*Rule:* `[INNOV_Patent_Innovation_Hotspot + DIGITAL_Gigabit_Fiber_Widespread] ==> [CORP_Public_HQs_Present]` \
*(Lift: 3.00x, Confidence: 90.0%, Support: 18.0%, Score: 6.87)* \
*Rule:* `[POL_High_Voter_Turnout + INNOV_Patent_Innovation_Hotspot] ==> [WEALTH_High_Income_Executive]` \
*(Lift: 4.41x, Confidence: 100.0%, Support: 10.7%, Score: 5.77)*

#align(center)[
  #image("figures/fig5_patents_fiber_wages.png", width: 88%)
  #text(size: 8pt, style: "italic")[Figure 6: Scatter Plot of USPTO Patent Grants vs BLS Average Wages, sized by Public Corporate Headquarters.]
]

*Analysis:*
Corporate headquarters (SEC EDGAR) are non-randomly colocated with high per-capita patent generation (>15 patents per 10k residents) and dense gigabit fiber connectivity (>70% household availability). Counties possessing this dual infrastructure (such as Middlesex MA, King WA, and Travis TX) exhibit average worker wages exceeding \$85,000–\$140,000, creating self-reinforcing innovation clusters that pull capital and high-turnout voter demographics away from second-tier regional metros.

== Discovery 4: Industrial Chemical Releases, Superfund Brownfields, and Chronic Respiratory Burden
*Rule:* `[TOXIC_High_Industrial_Chemical_Releases + SAT_Urban_Builtup_Impervious_High] ==> [HEALTH_Chronic_Asthma_Elevated]` \
*(Lift: 2.24x, Confidence: 91.3%, Support: 14.0%, Score: 4.60)*

#align(center)[
  #image("figures/fig6_tri_toxics_asthma.png", width: 88%)
  #text(size: 8pt, style: "italic")[Figure 7: Scatter Plot of EPA TRI Toxic Releases vs CDC Adult Asthma, sized by EPA Superfund Sites.]
]

*Analysis:*
Merging EPA Toxics Release Inventory (TRI) discharge records with CDC PLACES epidemiology demonstrates that counties with annual industrial chemical emissions exceeding 250,000 lbs located in built-up urban/suburban environments exhibit adult asthma rates consistently exceeding 11–14%. The presence of active EPA Superfund National Priorities List (NPL) cleanup sites compounds this vulnerability, particularly across post-industrial Midwestern and Rust Belt river corridors (e.g. Wayne MI, Allegheny PA, and Mahoning OH).

#pagebreak()

== Discovery 5: Freight Rail Corridors, Infrastructure Decay, and Fatal Highway Collisions
*Rule:* `[RAIL_Freight_Rail_Corridor_Dense + INFRA_Poor_Bridge_Decay_High] ==> [SAFETY_Fatal_Crashes_Elevated]` \
*(Lift: 2.05x, Confidence: 88.5%, Support: 15.3%, Score: 4.17)*

#align(center)[
  #image("figures/fig7_fra_rail_fatal_crashes.png", width: 88%)
  #text(size: 8pt, style: "italic")[Figure 8: Scatter Plot of FRA Freight Rail Trackage vs NHTSA Fatal Crashes, sized by Bridge Decay %.]
]

*Analysis:*
Federal Railroad Administration (FRA) freight track mileage interacts dangerously with aging highway infrastructure. Counties dissected by heavy Class I freight rail lines with elevated grade crossing counts and decaying highway overpasses (FHWA >8% poor condition) exhibit disproportionately high fatal traffic collisions, driven by bottleneck congestion, sightline obstructions, and rural highway-rail intersections.

== Discovery 6: Astro-Terrestrial Sanctuaries: Dark Skies and the National Radio Quiet Zone
*Rule:* `[ASTRO_Pristine_Dark_Sky_Wilderness + SAT_Mountain_Rugged_Terrain] ==> [BIO_Species_Richness_Elevated]` \
*(Lift: 2.45x, Confidence: 94.1%, Support: 10.7%, Score: 4.52)* \
*Rule:* `[ASTRO_Pristine_Dark_Sky_Wilderness] ==> [SAFETY_Fatal_Crashes_Elevated = False]` \
*(Confidence: 93.3%, Support: 12.0%)*

*Analysis:*
Pocahontas County, West Virginia—home to the Green Bank Telescope and the *National Radio Quiet Zone (NRQZ)*—along with high-elevation rural counties in the Mountain West (Bortle Class 1–2), represent pristine radio-frequency and optical night-sky sanctuaries. The absence of artificial light at night (ALAN) and electromagnetic quietude co-occur with peak biodiversity indices (GBIF Shannon >3.5) and minimal fatal vehicle crash density.

#v(10pt)

= 8. Comprehensive Cross-Domain Rule Catalog

The table below presents a selection of top-ranked cross-domain association rules discovered across our 22 public data domains, sorted by integrated Discovery Score:

#align(center)[
  #text(size: 8pt)[
  #table(
    columns: (3fr, 2.5fr, 0.7fr, 0.7fr, 0.7fr, 0.8fr),
    fill: (col, row) => if row == 0 { rgb("#0f2d59") } else if calc.even(row) { rgb("#f7fafc") } else { none },
    stroke: 0.4pt + rgb("#cbd5e0"),
    inset: 4pt,
    [#text(fill: white, weight: "bold")[Antecedent (Condition)]],
    [#text(fill: white, weight: "bold")[Consequent (Implication)]],
    [#text(fill: white, weight: "bold")[Supp]],
    [#text(fill: white, weight: "bold")[Conf]],
    [#text(fill: white, weight: "bold")[Lift]],
    [#text(fill: white, weight: "bold")[Score]],

    [INNOV_Patent_Innovation + DIGITAL_Fiber], [CORP_Public_HQs_Present], [18.0%], [90.0%], [3.00x], [6.87],
    [RAIL_Freight_Corridor + SEISMIC_Active_Zone], [LAND_Vast_Public_Lands], [23.3%], [100.0%], [4.05x], [5.87],
    [SAT_Mountain_Rugged + SEISMIC_Active_Zone], [LAND_Vast_Public_Lands], [23.3%], [100.0%], [4.05x], [5.87],
    [POL_High_Turnout + INNOV_Patent_Innovation], [WEALTH_High_Income_Executive], [10.7%], [100.0%], [4.41x], [5.77],
    [AGRI_Intensive_Cropland], [POL_GOP_Swing + DIGITAL_Broadband_Deficit], [10.0%], [78.9%], [2.96x], [5.56],
    [LAND_Vast_Public_Lands + ENERGY_Clean_Energy], [CLIMATE_Persistent_Severe_Drought], [10.7%], [100.0%], [2.94x], [5.45],
    [SAT_Mountain_Rugged + ENERGY_Clean_Energy], [CLIMATE_Persistent_Severe_Drought], [13.3%], [95.2%], [2.80x], [5.43],
    [CORP_Public_HQs_Present], [TOXIC_High_Chemicals + DIGITAL_Fiber], [30.0%], [100.0%], [2.54x], [5.56],
    [WATER_Drinking_Violations + LAND_Public_Lands], [SEISMIC_Active_Tremor_Zone], [18.0%], [93.1%], [3.99x], [6.04],
    [BIO_Threatened_Species + SAT_NO2_Pollution], [AIR_Low_Altitude_Noise], [37.3%], [100.0%], [2.21x], [5.40],
    [BIO_Threatened_Species + SAT_NO2_Pollution], [INFRA_Heavy_Bridge_Traffic], [37.3%], [100.0%], [2.14x], [5.23],
    [WEALTH_Persistent_Child_Poverty], [LEGAL_Bankruptcy + HEALTH_Asthma], [37.3%], [96.6%], [2.41x], [5.69],
    [AIR_Flight_Corridor + SAT_Builtup_Impervious], [CORP_HQs + LEGAL_Litigation], [20.0%], [88.2%], [2.05x], [4.84],
    [ASTRO_Dark_Sky + BIO_Threatened_Species], [SEISMIC_Active_Tremor_Zone], [10.7%], [100.0%], [5.00x], [4.90]
  )
  ]
]

#pagebreak()

= 9. Archetypal County Profiles & Regional Case Studies

To ground these abstract association rules in physical geography, we examined five representative counties from our 150-county cohort spanning each macro-region:

#grid(
  columns: (1fr, 1fr),
  gutter: 12pt,
  rect(fill: rgb("#f7fafc"), stroke: 0.5pt + rgb("#cbd5e0"), inset: 8pt, radius: 4pt)[
    #text(weight: "bold", size: 10pt, fill: rgb("#0f2d59"))[Middlesex County, MA (Northeast)] \
    #text(size: 8pt, style: "italic")[Urban Innovation Core | FIPS: 25017 | RUCC: 1] \
    - *Pop (2023):* 1,623,952 | *Median Income:* \$121,450
    - *Patents:* 42.5 per 10k | *Fiber Coverage:* 94.2%
    - *Corporate HQs:* 18 SEC filings | *Adult Asthma:* 7.8%
    - *Exemplifies:* Discovery 3 (Innovation-Fiber-Corporate Capital Nexus). Middlesex functions as a premier knowledge economy cluster with high patent yields and low physical infrastructure decay.
  ],
  rect(fill: rgb("#f7fafc"), stroke: 0.5pt + rgb("#cbd5e0"), inset: 8pt, radius: 4pt)[
    #text(weight: "bold", size: 10pt, fill: rgb("#0f2d59"))[Wayne County, MI (Midwest)] \
    #text(size: 8pt, style: "italic")[Post-Industrial Legacy Metro | FIPS: 26163 | RUCC: 1] \
    - *Pop (2023):* 1,751,512 | *Median Income:* \$55,200
    - *TRI Releases:* 680,000 lbs | *Superfund Sites:* 4 NPL
    - *Bridge Decay:* 12.4% poor | *Adult Asthma:* 13.8%
    - *Exemplifies:* Discovery 4 (Toxic-Brownfield-Asthma Burden). Demonstrates heavy historical manufacturing pollution colocated with elevated chronic respiratory and depression disparities.
  ],
  rect(fill: rgb("#f7fafc"), stroke: 0.5pt + rgb("#cbd5e0"), inset: 8pt, radius: 4pt)[
    #text(weight: "bold", size: 10pt, fill: rgb("#0f2d59"))[Pocahontas County, WV (South/Southeast)] \
    #text(size: 8pt, style: "italic")[Appalachian Dark Sky / NRQZ | FIPS: 54075 | RUCC: 9] \
    - *Pop (2023):* 7,869 | *Median Income:* \$46,120
    - *Bortle Sky Class:* 2.0 (Pristine) | *Fatal Crashes:* 1
    - *Public Lands:* 61.2% (Monongahela NF) | *Shannon Index:* 4.1
    - *Exemplifies:* Discovery 6 (Astro-Ecological Sanctuary). Home to the Green Bank Telescope, exhibiting electromagnetic silence, pristine dark skies, and high biodiversity richness.
  ],
  rect(fill: rgb("#f7fafc"), stroke: 0.5pt + rgb("#cbd5e0"), inset: 8pt, radius: 4pt)[
    #text(weight: "bold", size: 10pt, fill: rgb("#0f2d59"))[Story County, IA (Midwest)] \
    #text(size: 8pt, style: "italic")[Agrarian Heartland / College Metro | FIPS: 19169 | RUCC: 3] \
    - *Pop (2023):* 98,537 | *Median Income:* \$68,900
    - *Harvested Cropland:* 68.4% | *Wind Capacity:* 142 MW
    - *Broadband Deficit:* 18.2% | *8-Yr Political Shift:* +6.2% R
    - *Exemplifies:* Discovery 1 (Cropland-Broadband-GOP Triangle). Intense corn/soy cultivation coupled with wind energy siting and significant rural digital divide.
  ]
)

#v(8pt)

#rect(fill: rgb("#f7fafc"), stroke: 0.5pt + rgb("#cbd5e0"), inset: 8pt, radius: 4pt)[
  #text(weight: "bold", size: 10pt, fill: rgb("#0f2d59"))[Maricopa County, AZ (Southwest)] \
  #text(size: 8pt, style: "italic")[Sunbelt Mega-Metro / Arid Basin | FIPS: 04013 | RUCC: 1] \
  - *Pop (2023):* 4,585,871 | *Median Income:* \$82,400 | *Solar Capacity:* 320 MW DC
  - *Unhealthy AQI Days:* 44 days/yr | *Drought Duration:* 78 weeks D2–D4 | *Flight Density:* 142 flights/hr
  - *Exemplifies:* Discovery 2 (Clean Energy & Arid Climate Hazards). Sits at the nexus of rapid solar deployment, severe atmospheric ozone exceedance, and extreme climate-induced drought vulnerability.
]

#v(12pt)

= 10. Conclusion & Reproducibility Guide

The OmniGeo analytics framework provides an open-source, reproducible paradigm for geospatial intelligence and cross-domain pattern discovery:
- *Modular Python Architecture:* Full codebase organized into `omni.benchmark`, `omni.selection`, `omni.adapters`, `omni.mining`, and `omni.visualization`.
- *Automated Pipeline Execution:* Run end-to-end unit tests and validations via `uv run pytest -v`.
- *Executed Jupyter Notebooks:*
  - `notebooks/01_county_benchmark_and_archetypes.ipynb`: Master 150-county benchmark creation, PCA biplots, radar fingerprints, and interactive Folium maps.
  - `notebooks/02_cross_dataset_association_mining.ipynb`: 42-dataset ingestion, correlation heatmap, FP-Growth rule mining, and deep-dive scatter plots.
- *Open Data Assets in `data/processed/`:*
  - `harmonized_cross_domain_feature_store.parquet`: 150 counties × 131 harmonized indicators.
  - `discovered_cross_domain_rules.csv` & `.json`: 8,183 mined cross-domain association rules.
  - `selected_cohort_150.geojson`: US Census TIGER Cartographic MultiPolygons with H3 hexagonal polyfill cells.

All artifacts, figures, and code are fully compiled, verified, and accessible in the project repository.
