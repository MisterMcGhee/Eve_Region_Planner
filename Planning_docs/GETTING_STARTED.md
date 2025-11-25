# Pure Blind Sovereignty Planning Tool - Getting Started

## What You Have Now

### 📊 Existing Data
- ✅ Pure Blind systems spreadsheet (85 systems)
- ✅ Power and workforce capacities
- ✅ Ice belt identification
- ✅ Moon counts
- ✅ Constellation assignments

### 📚 Documentation Created
1. **PROJECT_PLAN.md** - Complete 4-phase development plan
2. **EXISTING_RESOURCES.md** - Data sources and community tools
3. **python_graph_primer.py** - NetworkX tutorial
4. **quick_reference.py** - Common operations cheat sheet
5. **existing_data_guide.py** - How to use Fuzzwork SDE

### 🚀 Ready-to-Run Code
1. **phase1_quick_start.py** - Data acquisition script
2. **phase2_visualization.py** - Map generation script

---

## Your Next Steps (This Week)

### Step 1: Download the SDE Database (5 minutes)
```bash
# Download from Fuzzwork (130MB compressed)
wget https://www.fuzzwork.co.uk/dump/sqlite-latest.sqlite.bz2

# Extract (results in ~500MB file)
bunzip2 sqlite-latest.sqlite.bz2
```

**Windows users:** Download manually and use 7-Zip to extract.

### Step 2: Install Python Dependencies (2 minutes)
```bash
pip install networkx pandas openpyxl plotly matplotlib scipy
```

### Step 3: Run Phase 1 Data Acquisition (1 minute)
```bash
python phase1_quick_start.py
```

This will:
- Load all Pure Blind systems from SDE
- Merge with your spreadsheet
- Build the complete network graph
- Generate initial analysis
- Save everything to `pure_blind_data/`

**Expected output:**
```
Found 85 systems in Pure Blind
Found [X] internal gates
Graph created: 85 nodes, [Y] edges
✓ Graph is fully connected
✓ Data saved successfully
```

### Step 4: Generate Visualizations (1 minute)
```bash
python phase2_visualization.py
```

This will create:
- `map_interactive.html` - Interactive Plotly map (open in browser!)
- `map_static.png` - Static image for sharing

---

## What Your Tool Will Do (End Goal)

### 🗺️ Phase 2: Interactive Map
- Dotlan-style layout
- Hover for system info
- Click to select systems
- Color-coded constellations
- Show current upgrades

### ⚙️ Phase 3: Upgrade Planning
**For Individual Systems:**
- "What fits in this system?" calculator
- Real-time power/workforce validation
- Preset configurations (max mining, max ratting)

**Region-Wide:**
- "Best mining systems" recommendation (clustered near industrials)
- "Best ratting systems" recommendation (spread for coverage)
- Export upgrade plans for alliance

### 🌉 Phase 4: Ansiblex Optimization
- Suggest optimal bridge placements
- Minimize jumps to staging/industrial/market hubs
- Respect 5 LY range and one-per-system constraints
- Before/after comparison
- Export bridge construction orders

---

## Key Algorithms You'll Build

### 1. Mining System Clustering
```python
def find_best_mining_systems(industrial_hubs, num_systems=10):
    """
    Score systems by:
    - Distance to industrial hub (closer = better)
    - Ice belt presence (+50 points)
    - Moon count (+2 per moon)
    - Constellation clustering (+5 per same-const neighbor)
    
    Returns: Top N systems for mining upgrades
    """
```

### 2. Bridge Placement Optimization
```python
def optimize_bridge_network(strategic_systems, max_bridges=10):
    """
    Greedy algorithm:
    1. Calculate weighted distances to strategic systems
    2. For each potential bridge:
       - Check if valid (range, conflicts)
       - Calculate improvement in weighted average jumps
    3. Add bridge with best improvement
    4. Repeat until budget exhausted
    
    Returns: List of (system_a, system_b) bridge pairs
    """
```

### 3. Upgrade Capacity Calculator
```python
def calculate_fits(power_capacity, workforce_capacity, desired_upgrades):
    """
    Knapsack-style problem:
    - Try to fit desired upgrades
    - Fall back to smaller tiers if needed
    - Warn if over capacity
    
    Returns: Feasible upgrade configuration
    """
```

---

## Data You Still Need to Collect

### From Game/Wiki (Phase 3)
- [ ] **Sovereignty upgrade database**
  - Exact power costs (e.g., Mining Lv 1 = 1000 power?)
  - Exact workforce costs
  - All upgrade types and tiers
  - Source: Eve University Wiki or game screenshots

### From Alliance Leadership (Phase 4)
- [ ] **Strategic system designations**
  - Which system is main staging?
  - Where are industrial hubs?
  - Where are market hubs?
  - Any planned relocations?

- [ ] **Constraints and priorities**
  - Budget for Ansiblex bridges?
  - Mining vs ratting priority?
  - Any systems to avoid (gatecamps)?

### From ESI or Manual (Optional)
- [ ] **Current sovereignty upgrades** (what's already installed?)
- [ ] **Current Ansiblex bridges** (if any exist)

---

## Technology Stack Summary

### Core Libraries
- **NetworkX** - Graph algorithms (pathfinding, centrality, optimization)
- **Pandas** - Data manipulation
- **NumPy** - Numerical calculations
- **SQLite3** - Database access

### Visualization
- **Plotly** - Interactive maps (recommended)
- **Matplotlib** - Static maps (backup)
- **Dash** - Web app framework (optional, for Phase 5)

### Optional Advanced
- **SciPy** - Optimization algorithms (if greedy isn't enough)
- **PuLP** - Linear programming (for optimal bridge placement)

---

## Development Workflow Recommendations

### Use Jupyter Notebooks for Exploration

```python
# In a notebook:
import networkx as nx
import pandas as pd

# Load graph
G = nx.read_graphml('../data/pure_blind_data/pure_blind_graph.graphml')

# Experiment with algorithms
nx.shortest_path(G, '5ZXX-K', 'EC-P8R')
nx.betweenness_centrality(G)

# Visualize results inline
import matplotlib.pyplot as plt

nx.draw(G)
plt.show()
```

### Then Move to Python Modules
```
project/
├── data/                      # Raw data
│   ├── sqlite-latest.sqlite
│   └── pure_blind_systems.xlsx
├── src/                       # Production code
│   ├── data_loader.py
│   ├── graph_builder.py
│   ├── visualization.py
│   ├── upgrade_calculator.py
│   └── bridge_optimizer.py
├── notebooks/                 # Experiments
│   ├── exploration.ipynb
│   └── algorithm_testing.ipynb
└── outputs/                   # Generated files
    ├── maps/
    └── plans/
```

---

## Success Metrics

### Phase 1 ✅ (This Week)
- [x] Data loaded from SDE
- [x] Spreadsheet merged successfully
- [x] Graph builds with all 85 systems
- [ ] Validation: Graph is fully connected

### Phase 2 🎯 (Next Week)
- [ ] Map generates and looks recognizable
- [ ] Interactive features work (hover, click)
- [ ] Alliance members can identify systems

### Phase 3 🎯 (Weeks 3-4)
- [ ] Upgrade calculator validates capacity correctly
- [ ] Mining clustering produces sensible results
- [ ] Can export complete upgrade plan

### Phase 4 🎯 (Weeks 5-8)
- [ ] Bridge algorithm respects all constraints
- [ ] Optimization improves connectivity metrics
- [ ] Leadership approves recommended bridges

---

## Getting Help

### Resources
- **NetworkX docs:** https://networkx.org/documentation/stable/
- **Plotly docs:** https://plotly.com/python/
- **Eve University Wiki:** https://wiki.eveuniversity.org/
- **Fuzzwork:** https://www.fuzzwork.co.uk/

### Community
- **Eve Online Discord:** #3rd-party-dev-and-esi channel
- **Reddit:** r/evenullsec, r/Eve (for sovereignty questions)
- **GitHub:** Search for "eve online" to see other projects

### Questions to Ask Your Alliance
1. "Which systems are our main staging/industrial hubs?"
2. "What's our priority: mining income or ratting income?"
3. "What's a realistic budget for Ansiblex bridges?"
4. "Are there any systems we should avoid bridging to?"
5. "Can I get access to current sovereignty upgrade configs?"

---

## Timeline Estimate

| Phase | Duration | Start After |
|-------|----------|-------------|
| Phase 1: Data | 1 week | Now |
| Phase 2: Visualization | 2 weeks | Phase 1 |
| Phase 3: Upgrade Planning | 3 weeks | Phase 2 |
| Phase 4: Bridge Optimization | 3 weeks | Phase 3 |
| Phase 5: Polish | 2 weeks | Phase 4 |
| **Total** | **~11 weeks** | - |

**Can be parallelized:** Visualization and upgrade planning can overlap.

---

## Quick Wins You Can Show Early

### Week 1: "Look at our network"
- Show the interactive map
- Highlight chokepoint systems
- Identify high-traffic systems

### Week 2: "Here's where mining should go"
- Run clustering algorithm
- Show top 10 systems for mining
- Explain why they're optimal

### Week 3: "Here's what fits in each system"
- Demonstrate upgrade calculator
- Show preset configurations
- Export upgrade shopping list

These early wins build momentum and get buy-in from leadership!

---

## Final Thoughts

This is an ambitious but achievable project. The key is:
1. **Start small** - Get Phase 1 working this week
2. **Show progress** - Demo to alliance early and often
3. **Iterate** - Get feedback and adjust algorithms
4. **Document** - Write down assumptions and decisions

The phased approach means you can stop at any phase and still have something useful. Even just Phases 1-2 (the map) would be valuable to your alliance.

Good luck! You've got all the tools and knowledge you need. Now it's time to build! 🚀

---

## Immediate Action Items

**Today:**
- [ ] Download Fuzzwork SQLite database
- [ ] Install Python dependencies
- [ ] Run `phase1_quick_start.py`

**This Week:**
- [ ] Run `phase2_visualization.py`
- [ ] Review generated map
- [ ] Research sovereignty upgrade costs
- [ ] Ask alliance for strategic system list

**Next Week:**
- [ ] Start Phase 3 implementation
- [ ] Build upgrade calculator
- [ ] Get feedback on map from alliance

Start now! The data is waiting for you. 💪
