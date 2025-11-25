# Eve Region Planner - Data Directory

This directory contains all data files for the Eve Region Planner tool.

## Structure

```
data/
├── sqlite-latest.sqlite          # Fuzzwork SDE database (download separately)
├── pure_blind_data/              # Pure Blind region extracted data
│   ├── systems_static.csv        # Auto-generated from SDE
│   ├── systems_capacity.csv      # User-maintained (power/workforce)
│   ├── systems_full.csv          # Merged dataset
│   ├── gates_internal.csv        # Internal stargate connections
│   ├── gates_border.csv          # Border connections
│   ├── pure_blind_graph.graphml  # NetworkX graph (XML)
│   ├── pure_blind_graph.json     # NetworkX graph (JSON)
│   └── summary.json              # Network analysis
└── [other_region_data]/          # Future region data folders
```

## Downloading the SDE Database

The `sqlite-latest.sqlite` file is required for extracting region data. Download it from Fuzzwork:

```bash
# Download the latest SDE database
wget https://www.fuzzwork.co.uk/dump/sqlite-latest.sqlite.bz2

# Extract it
bunzip2 sqlite-latest.sqlite.bz2

# Move it to this directory
mv sqlite-latest.sqlite /home/user/Eve_Region_Planner/data/
```

Or download directly from: https://www.fuzzwork.co.uk/dump/

## Region Data Folders

Each region you extract data for will have its own folder containing:

- **systems_static.csv** - Auto-generated from SDE (coordinates, moons, planets, ice, etc.)
- **systems_capacity.csv** - User-maintained (power and workforce capacity)
- **systems_full.csv** - Merged dataset combining static and capacity data
- **gates_internal.csv** - Stargate connections within the region
- **gates_border.csv** - Stargate connections to adjacent regions
- **graph files** - NetworkX graph representations for analysis

## Usage

1. Download `sqlite-latest.sqlite` (see above)
2. Run the region data extractor to create region-specific folders
3. Edit the `systems_capacity.csv` in each region folder as needed
4. Re-run the extractor to regenerate the `systems_full.csv` file

See the main README for more details.
