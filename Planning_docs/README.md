# Pure Blind Sovereignty Planning Tool

A comprehensive planning tool for Eve Online alliance sovereignty management in the Pure Blind region. Optimize Ansiblex jump bridge placement, system upgrade configurations, mining operations, and ratting distributions across 85 systems.

## 🎯 Project Goals

This tool helps alliance leadership make strategic decisions about:

1. **Ansiblex Jump Bridge Network** - Optimize bridge placement to minimize jumps to strategic systems (staging, industrial hubs, market hubs)
2. **System Upgrades** - Plan sovereignty upgrades within power and workforce constraints
3. **Mining Operations** - Cluster mining upgrades near industrial hubs, prioritize ice belt systems
4. **Ratting Distribution** - Spread ratting upgrades across the region for balanced PvE opportunities
5. **Strategic Analysis** - Identify chokepoints, high-traffic systems, and network vulnerabilities

## 🏗️ Architecture

**Split-Screen Design:**
- **Left Panel (30%):** Control panel with dropdowns, buttons, and configuration tools
- **Right Panel (70%):** Context-specific visualizations that update in real-time

**Technology Stack:**
- Backend: Python 3.10+, NetworkX, Pandas, NumPy
- Visualization: Plotly Dash (interactive web framework)
- Data: Fuzzwork's SDE (Static Data Export) SQLite database

## 🚀 Quick Start

### Prerequisites

```bash
# Install dependencies
pip install networkx pandas openpyxl plotly dash matplotlib scipy
```

### 1. Download Eve Online Data

```bash
# Download Fuzzwork's SDE database (~130MB compressed)
wget https://www.fuzzwork.co.uk/dump/sqlite-latest.sqlite.bz2
bunzip2 sqlite-latest.sqlite.bz2
```

### 2. Run Phase 1 - Data Acquisition

```bash
python phase1_quick_start.py
```

This will:
- Load all 85 Pure Blind systems from the SDE
- Extract stargate connections
- Merge with our spreadsheet data (power, workforce, ice belts, moons)
- Build a NetworkX graph
- Generate initial analysis (chokepoints, strategic systems)
- Save to `pure_blind_data/` directory

### 3. Run the Dash Application

```bash
python dash_app_starter.py
```

Open your browser to: http://127.0.0.1:8050/

## 📊 Tool Modes

### 1. Ansiblex Bridge Builder
**What it does:** Plan jump bridge network to minimize travel time

**Controls (Left):**
- Select reference system
- Add bridges (From/To dropdowns)
- View impact metrics

**Visualization (Right):**
- Graph showing stargate connections (gray) and bridges (blue)
- Distance heatmap from reference system
- Jump count metrics

**Constraints:**
- 5 light-year maximum range
- One bridge terminus per system
- ISK and fuel costs

### 2. System Upgrade Planner
**What it does:** Configure sovereignty upgrades for individual systems

**Controls (Left):**
- Select system
- Choose upgrade type (Mining, Ratting, Belt, etc.)
- Choose upgrade tier (Level 1-3)
- Apply presets (Max Mining, Max Ratting, Balanced)

**Visualization (Right):**
- Power capacity gauge
- Workforce capacity gauge
- Upgrade summary table
- Validation warnings

### 3. Mining System Optimizer
**What it does:** Recommend which systems to configure for mining

**Controls (Left):**
- Select industrial hub
- Set number of mining systems
- Configure priorities (ice belts, moon count, clustering)

**Visualization (Right):**
- Graph with recommended systems highlighted
- Distance rings from industrial hub
- Score gradient

**Algorithm prioritizes:**
- Proximity to industrial hubs
- Ice belt presence (+50 points)
- Moon count (+2 per moon)
- Constellation clustering (+5 per adjacent mining system)

### 4. Ratting System Optimizer
**What it does:** Recommend which systems to configure for ratting

**Controls (Left):**
- Select staging system
- Set number of ratting systems
- Choose distribution (spread vs. clustered)

**Visualization (Right):**
- Graph with recommended systems highlighted
- Coverage heatmap (distance to nearest ratting system)

**Algorithm prioritizes:**
- Even distribution across region
- Higher true-sec systems
- Balanced constellation coverage
- Proximity to staging (3-6 jumps ideal)

### 5. Strategic Network Analysis
**What it does:** Analyze network properties and vulnerabilities

**Controls (Left):**
- Choose analysis type:
  - Chokepoints (articulation points)
  - Traffic (betweenness centrality)
  - System centrality
  - Distance heatmaps

**Visualization (Right):**
- Context-dependent graph visualizations
- Highlighted critical systems
- Metrics and statistics

## 📁 Project Structure

```
pure-blind-planning-tool/
├── README.md                  # This file
├── PROJECT_PLAN.md           # Detailed 4-phase development plan
├── UI_ARCHITECTURE.md        # Split-screen design specifications
├── EXISTING_RESOURCES.md     # Data sources and APIs
├── GETTING_STARTED.md        # Detailed setup instructions
├── STATUS.md                 # Current project status
├── DATA_STRUCTURE.md         # Data models and schemas
│
├── data/
│   ├── sqlite-latest.sqlite           # SDE database (download separately)
│   ├── pure_blind_systems.xlsx        # System data spreadsheet
│   └── pure_blind_data/               # Generated data (from Phase 1)
│       ├── systems.csv
│       ├── gates_internal.csv
│       ├── pure_blind_graph.graphml
│       └── summary.json
│
├── src/
│   ├── phase1_quick_start.py         # Data acquisition
│   ├── dash_app_starter.py           # Main application
│   ├── python_graph_primer.py        # NetworkX tutorial
│   └── existing_data_guide.py        # SDE query examples
│
└── docs/
    └── (additional documentation)
```

## 📈 Development Phases

### ✅ Phase 1: Data Acquisition & Foundation (Completed)
- SDE database integration
- Pure Blind system data compilation
- Graph construction
- Initial analysis tools

### 🚧 Phase 2: UI Framework (In Progress)
- Dash application structure
- Split-screen layout
- Tool selector and navigation
- Basic graph visualization

### 📋 Phase 3: Tool Implementation (Todo)
- Phase 3A: Ansiblex Bridge Builder (2 weeks)
- Phase 3B: System Upgrade Planner (2 weeks)
- Phase 3C: Mining System Optimizer (2 weeks)
- Phase 3D: Ratting System Optimizer (1 week)

### 📋 Phase 4: Strategic Analysis (Todo)
- Chokepoint detection
- Traffic analysis
- Centrality metrics
- Multi-system batch configuration

### 📋 Phase 5: Polish & Advanced Features (Todo)
- Export capabilities (CSV, JSON, Discord-friendly)
- What-if scenario analysis
- ESI API integration (live data)
- Documentation and tutorials

## 🎓 Learning Resources

If you're new to the technologies used:

- **NetworkX Tutorial:** `python_graph_primer.py` - 15 practical examples for Eve Online
- **Data Sources:** `EXISTING_RESOURCES.md` - All Eve Online data APIs
- **Project Plan:** `PROJECT_PLAN.md` - Complete technical roadmap
- **UI Design:** `UI_ARCHITECTURE.md` - Detailed mockups and workflows

## 📊 Data Sources

### Primary Data: Fuzzwork's SDE
- **URL:** https://www.fuzzwork.co.uk/dump/
- **Database:** SQLite format (~500MB uncompressed)
- **Key Tables:**
  - `mapSolarSystems` - All system info
  - `mapSolarSystemJumps` - All stargate connections
  - `mapConstellations` - Constellation info
  - `mapRegions` - Region info (Pure Blind = regionID 10000023)

### Custom Data: Pure Blind Systems
- Power capacities (varies by system: 1600-3000)
- Workforce capacities (varies by system: 6000-30000)
- Ice belt presence (12 systems identified)
- Moon counts (varies: 12-79 moons per system)
- Strategic classifications (staging, industrial, market, etc.)

## 🛠️ Key Algorithms

### Mining Clustering
```python
score = 0
- Distance to nearest industrial hub (negative weight)
+ Ice belt presence (+50)
+ Moon count (+2 per moon)
+ Adjacent mining systems in same constellation (+5 per neighbor)
```

### Ansiblex Optimization
```python
# Greedy algorithm:
1. Calculate weighted distances to all strategic systems
2. Find bridge that maximizes reduction in weighted average jumps
3. Validate: Range ≤ 5 LY, no existing bridge in either system
4. Add bridge and recalculate distances
5. Repeat until desired number of bridges or no valid options
```

### Ratting Distribution
```python
# Spread algorithm:
1. Divide region into quadrants/areas
2. Select one system per area based on:
   - Higher true-sec (better anomaly spawns)
   - Distance from staging (3-6 jumps ideal)
   - Constellation balance
```

## 🤝 Contributing

This is an internal alliance tool. If you have suggestions:

1. Document your idea in an issue
2. Discuss with alliance leadership
3. Submit a pull request with tests

## 📝 License

Internal tool for [Your Alliance Name]. Not for public distribution.

## 🙏 Acknowledgments

- **Steve Ronuken (Fuzzwork)** - SDE database conversions
- **CCP Games** - Eve Online and SDE
- **NetworkX Team** - Graph analysis library
- **Plotly Team** - Interactive visualization framework

## 📞 Support

Questions? Contact:
- Discord: [Your Discord]
- In-game: [Your Character Name]
- GitHub Issues: [Repository Issues]

---

**Current Status:** Phase 2 (UI Framework) in progress  
**Last Updated:** November 2025  
**Version:** 0.2.0-alpha
