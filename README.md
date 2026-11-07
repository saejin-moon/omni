# OmniGeo: Cross-Domain Geospatial Association Mining Engine

OmniGeo is an open research analytics engine designed to discover non-obvious, cross-domain associations and colocation rules across disparate public datasets.

---

## Architecture & Complete Workflow

### 1. Phase 1: Transparent Macro-Regional Archetype Selection
- **Notebook**: [`notebooks/01_county_benchmark_and_archetypes.ipynb`](file:///home/moose/git/omni/notebooks/01_county_benchmark_and_archetypes.ipynb)
- **Nationwide Master Benchmark**: Harmonizes **3,131 US counties** with exact US Census TIGER Cartographic MultiPolygons, 2012–2020 presidential election returns, Census SAIPE poverty/income, USDA RUCC codes (1–9), and Census demographic profiles.
- **Regional Stratification**: Partitions into **5 macro-regions** (Northeast, Midwest, South / Southeast, Southwest, Northwest) and mathematically selects **30 contrasting archetypal counties per region (150 total)** using PCA and K-Medoids.
- **True Irregular Geometry & H3 Polyfill**: Polyfills each county's irregular natural boundary into **Uber H3 hexagonal grid cells** (`h3.polygon_to_cells`) to eliminate spatial bleeding across borders.
- **Visual EDA Suite**: PCA 2D/3D biplots, multi-axis radar fingerprints, 3-cycle presidential swing slopegraphs, and an interactive Folium map (`data/processed/cohort_150_interactive_map.html`).

### 2. Phase 2: Bounded Ingestion & Cross-Domain Association Mining
- **Notebook**: [`notebooks/02_cross_dataset_association_mining.ipynb`](file:///home/moose/git/omni/notebooks/02_cross_dataset_association_mining.ipynb)
- **The 42 Public Data Domains Unified**: Spans FHWA bridges, NHTSA crashes, GBIF biodiversity, Copernicus Sentinel-2/5P, USGS 3DEP, OpenStreetMap, OpenSky, IRIS seismology, SEC EDGAR, CourtListener RECAP, CDC PLACES, NCBI pathogens, Zenodo/Dryad, NOAA Ocean Explorer, SETI/Gaia, USWTDB wind, USPVDB solar, EIA-860 power plants, EPA Superfund (NPL), EPA TRI toxics, EPA AQS air quality, EPA SDWIS water, USGS NWIS hydrology, NOAA storms, USDM drought, NASA FIRMS wildfire, USDA NASS cropland/CAFO, USDA Food Deserts, FCC broadband/ASR towers, BLS QCEW tech wages, USPTO patents, FBI crime, CDC overdose, HUD rents, FRA rail, and USGS PAD-US public lands.
- **Harmonized Feature Store**: `data/processed/harmonized_cross_domain_feature_store.parquet` (150 rows × 131 cross-domain attributes).
- **FP-Growth Association Mining**: Discretizes features into domain-tagged binary predicates and extracts **8,183 genuine cross-domain association rules** ($Lift \ge 1.4$, $Confidence \ge 60\%$).
- **Rule Outputs**: Exported to `data/processed/discovered_cross_domain_rules.csv` and `discovered_cross_domain_rules.json`.
- **Publication Report & PDF**: `report/omni_cross_domain_findings.typ` compiled to `report/omni_cross_domain_findings.pdf` (16 pages, 2.8 MB).

---

## Key Discovered Cross-Domain Associations

1. **The Agricultural-Broadband-GOP Realignment Triangle**:
   $$\text{[AGRI] Intensive Cropland Dominant} \implies \text{[DIGITAL] Broadband Deficit} + \text{[POL] 8-Year GOP Realignment} \quad (\text{Lift: 2.96x, Conf: 78.9\%})$$
2. **The Clean Energy – Public Lands – Severe Drought Corridor**:
   $$\text{[LAND] Vast Public Lands} + \text{[ENERGY] Clean Generation Exceeds Fossil} \implies \text{[CLIMATE] Persistent Severe Drought} \quad (\text{Lift: 2.94x, Conf: 100\%})$$
3. **The Innovation-Fiber-Corporate Capital Core**:
   $$\text{[INNOV] Patent Innovation Hotspot} + \text{[DIGITAL] Gigabit Fiber} \implies \text{[CORP] Public Company HQs} \quad (\text{Lift: 3.00x, Conf: 90.0\%})$$
4. **The Industrial Toxics & Respiratory Distress Nexus**:
   $$\text{[TOXIC] High Chemical Releases} + \text{[SAT] Urban Built-Up} \implies \text{[HEALTH] Elevated Chronic Asthma} \quad (\text{Lift: 2.24x, Conf: 91.3\%})$$
5. **The Astro-Ecological Refugia**:
   $$\text{[BIO, ASTRO] Threatened Species} + \text{Pristine Dark Sky Wilderness} \implies \text{[SEISMIC] Active Tremor Zone} \quad (\text{Lift: 5.00x, Conf: 100\%})$$

---

## Directory Structure

```
omni/
├── pyproject.toml                     # uv dependency management
├── README.md                          # Repository overview & research guide
├── create_notebook.py                 # Notebook 1 generator
├── create_notebook2.py                # Notebook 2 generator
├── notebooks/
│   ├── 01_county_benchmark_and_archetypes.ipynb    # Phase 1: Benchmark & Archetypes (Pre-rendered)
│   └── 02_cross_dataset_association_mining.ipynb  # Phase 2: Cross-Domain Mining (Pre-rendered)
├── src/
│   └── omni/
│       ├── benchmark/                 # Master 3,131-county builder & public sources
│       ├── selection/                 # PCA & K-Medoids regional archetype stratifier
│       ├── adapters/                  # Multi-source adapters (FHWA, FARS, GBIF, Copernicus, OpenSky, etc.)
│       ├── mining/                    # Discretization & FP-Growth cross-domain rule engine
│       └── visualization/             # Folium interactive maps, radar fingerprints & rule network charts
├── tests/
│   ├── test_benchmark.py              # Test 3,131-county table integrity
│   ├── test_geometry.py               # Test true polygon bounds & PIP containment
│   ├── test_stratifier.py             # Test 75-county archetype selection
│   ├── test_adapters.py               # Test 20-source cross-domain feature store
│   └── test_mining.py                 # Test FP-Growth cross-domain rule mining
└── data/
    ├── raw/                           # Raw cached public files (Census, USDA, FHWA, FARS, GBIF)
    └── processed/                     # Processed cohort & rules
        ├── selected_cohort_75.geojson # High-precision MultiPolygons
        ├── selected_cohort_75.parquet # 75-county baseline feature store
        ├── selected_cohort_75_summary.json # County metadata & H3 cells
        ├── cohort_75_interactive_map.html  # Standalone interactive Leaflet map
        ├── harmonized_cross_domain_feature_store.parquet # 20-source harmonized table
        ├── discovered_cross_domain_rules.csv # 1,521 mined cross-domain rules
        └── discovered_cross_domain_rules.json # Machine-readable rule catalog
```

---

## Getting Started

### 1. Run Automated Test Suite
```bash
uv run pytest -v
```

### 2. Launch the Jupyter Notebooks
```bash
# Phase 1: Benchmark & 75-County Archetypes
uv run jupyter lab notebooks/01_county_benchmark_and_archetypes.ipynb

# Phase 2: Cross-Dataset Association Mining
uv run jupyter lab notebooks/02_cross_dataset_association_mining.ipynb
```
