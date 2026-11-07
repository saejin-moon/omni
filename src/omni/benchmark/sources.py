"""Data downloaders and cache management for benchmark public datasets."""

import os
import urllib.request
from pathlib import Path
from typing import Dict

DATA_SOURCES: Dict[str, str] = {
    "census_pop_2023": "https://www2.census.gov/programs-surveys/popest/datasets/2020-2023/counties/totals/co-est2023-alldata.csv",
    "usda_rucc_2023": "https://www.ers.usda.gov/media/5768/2023-rural-urban-continuum-codes.csv?v=47268",
    "census_saipe_2022": "https://www2.census.gov/programs-surveys/saipe/datasets/2022/2022-state-and-county/est22all.txt",
    "election_results_2020": "https://raw.githubusercontent.com/tonmcg/US_County_Level_Election_Results_08-20/master/2020_US_County_Level_Presidential_Results.csv",
    "election_context_medsl": "https://raw.githubusercontent.com/MEDSL/2018-elections-unoffical/master/election-context-2018.csv",
    "county_polygons_geojson": "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json",
}

LOCAL_FILENAMES: Dict[str, str] = {
    "census_pop_2023": "co-est2023-alldata.csv",
    "usda_rucc_2023": "2023-rural-urban-continuum-codes.csv",
    "census_saipe_2022": "est22all.txt",
    "election_results_2020": "2020_US_County_Level_Presidential_Results.csv",
    "election_context_medsl": "election-context-2018.csv",
    "county_polygons_geojson": "geojson-counties-fips.json",
}


def download_benchmark_sources(cache_dir: str = "data/raw/benchmark") -> Dict[str, Path]:
    """Downloads all benchmark sources into cache_dir if not already cached.

    Returns:
        Dict mapping source key to Path of cached local file.
    """
    cache_path = Path(cache_dir)
    cache_path.mkdir(parents=True, exist_ok=True)

    result_paths: Dict[str, Path] = {}
    headers = {"User-Agent": "Mozilla/5.0 (OmniGeo Research Agent 1.0)"}

    for key, url in DATA_SOURCES.items():
        fname = LOCAL_FILENAMES[key]
        dest_file = cache_path / fname
        result_paths[key] = dest_file

        if dest_file.exists() and dest_file.stat().st_size > 100:
            continue

        print(f"Downloading {key} from {url}...")
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=60) as resp, open(dest_file, "wb") as f_out:
            while True:
                chunk = resp.read(1024 * 1024)
                if not chunk:
                    break
                f_out.write(chunk)
        print(f"Saved {dest_file} ({dest_file.stat().st_size / (1024*1024):.2f} MB)")

    return result_paths
