# Pure Blind Data - Pure Blind

## Data Files

### Auto-Generated (from Fuzzwork SDE)
- **systems_static.csv** - System data from SDE (name, coords, ice, moons, etc.)
- **gates_internal.csv** - Internal stargate connections
- **gates_border.csv** - Border connections to adjacent regions
- **pure_blind_graph.graphml** - NetworkX graph (XML format)
- **pure_blind_graph.json** - NetworkX graph (JSON format)
- **summary.json** - Network analysis and statistics

### User-Maintained
- **systems_capacity.csv** - Power and workforce capacity per system
  - This file can be edited to update capacity values
  - These values are based on Activity Defense Multiplier (ADM)
  - ADM changes based on in-system activity (mining, ratting)

### Merged Data
- **systems_full.csv** - Complete dataset (static + capacity)
  - This is regenerated when you run region_data_extractor.py
  - Use this file for the planning tool

## Data Sources

### Fuzzwork SDE
- **Source:** https://www.fuzzwork.co.uk/dump/
- **What it provides:**
  - System names, IDs, coordinates
  - Security status
  - Constellation/region membership
  - Stargate connections
  - Moon/planet/belt counts
  - Ice belt detection
- **What it DOESN'T provide:**
  - Power/workforce capacity (activity-dependent)
  - Current sovereignty holders
  - Existing upgrades

### ESI API (Optional)
- **Source:** https://esi.evetech.net/
- **Useful for:**
  - Current sovereignty status
  - Live structure data
  - Real-time activity metrics
- **Not currently used** (static planning tool)

## How to Update Data

### Update Static Data (from SDE)
```bash
# Download latest SDE
wget https://www.fuzzwork.co.uk/dump/sqlite-latest.sqlite.bz2
bunzip2 sqlite-latest.sqlite.bz2
mv sqlite-latest.sqlite ../

# Regenerate (from Planning_docs directory)
cd ../../Planning_docs
python region_data_extractor.py
```

### Update Capacity Data
```bash
# Edit systems_capacity.csv manually
# Or import from your alliance's data

# Regenerate full dataset (from Planning_docs directory)
cd ../../Planning_docs
python region_data_extractor.py
```

## Statistics

- **Total Systems:** 85
- **Internal Gates:** 222
- **Border Gates:** 8
- **Ice Systems:** 85
- **Constellations:** 13

## Network Analysis

- **Chokepoints:** 31
- **Network Center:** X-7OMU
- **Diameter:** 25

Generated: 2025-11-25 14:15:01
