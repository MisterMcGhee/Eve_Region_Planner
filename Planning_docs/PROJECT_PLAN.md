# Pure Blind Sovereignty Planning Tool - Project Plan

## Project Overview

**Goal:** Build an interactive map and planning tool for optimizing sovereignty infrastructure in Eve Online's Pure Blind region.

**Core Capabilities:**
1. Visualize the Pure Blind jump gate network (Dotlan-style)
2. Plan and optimize Ansiblex jump bridge placement
3. Optimize mining upgrade placement based on clustering and proximity to industrial hubs
4. Plan ratting upgrade deployment for subcapital ships
5. Interactive sovereignty upgrade tinkering with power/workforce constraints
6. Strategic analysis of network connectivity and chokepoints

---

## PHASE 1: Data Acquisition & Foundation
**Timeline: 1-2 weeks**
**Status: Foundation for everything else**

### 1.1 Core System Data
**Source: Fuzzwork SQLite SDE + Your Spreadsheet**

**Required Data:**
- [x] System names (85 systems in Pure Blind)
- [x] Constellation assignments
- [x] Security status
- [x] Power capacity per system
- [x] Workforce capacity per system
- [x] Moon counts
- [x] Ice belt presence (boolean)
- [ ] Current belt counts
- [ ] Planet types and counts (for PI value assessment)

**Data Structure:**
```python
system_data = {
    'system_name': {
        'system_id': int,
        'constellation': str,
        'constellation_id': int,
        'security': float,
        'power_capacity': int,
        'workforce_capacity': int,
        'moons': int,
        'has_ice': bool,
        'belts': int,
        'planets': {...},
        'x': float,  # 3D coordinates for visualization
        'y': float,
        'z': float,
    }
}
```

### 1.2 Network Topology
**Source: Fuzzwork SDE (mapSolarSystemJumps)**

**Required Data:**
- [ ] All stargate connections within Pure Blind
- [ ] Cross-region connections (entry/exit points to neighboring regions)
- [ ] 3D coordinates for planar graph layout

**Data Structure:**
```python
gate_connections = [
    ('System-A', 'System-B'),
    ('System-B', 'System-C'),
    ...
]
```

### 1.3 Sovereignty Upgrade Database
**Source: Manual research or Eve University Wiki**

**Required Data:**
- [ ] All IHUB upgrade types (mining, ratting, cyno beacons, etc.)
- [ ] Power requirements per upgrade
- [ ] Workforce requirements per upgrade
- [ ] Upgrade effects and bonuses
- [ ] Upgrade tier system (where applicable)

**Data Structure:**
```python
upgrades = {
    'Mining Upgrades': {
        'Advanced ORE Development Lv 1': {'power': 1000, 'workforce': 5000, 'effect': '+5% ore'},
        'Advanced ORE Development Lv 2': {'power': 2000, 'workforce': 10000, 'effect': '+10% ore'},
        # ... etc
    },
    'Ratting Upgrades': {
        'Pirate Detection Array Lv 1': {...},
        # ... etc
    },
}
```

### 1.4 Strategic System Classification
**Source: Manual input from alliance/coalition leadership**

**Required Data:**
- [ ] Staging systems (where fleets form)
- [ ] Industrial hubs (manufacturing, research)
- [ ] Market hubs (trade centers)
- [ ] Important moon mining systems
- [ ] Border/defensive systems

**Data Structure:**
```python
strategic_systems = {
    'staging': ['5ZXX-K', ...],
    'industrial': ['X-7OMU', ...],
    'market': ['X-7OMU', ...],
    'moon_mining': [...],
    'border': [...],
}
```

### 1.5 Ansiblex Jump Bridge Constraints
**Source: Game mechanics knowledge**

**Required Data:**
- [x] Maximum range: 5 light-years
- [x] Mass limit: 1.48 million tons (no supers/titans)
- [x] One bridge per system limit
- [ ] Current installed bridges (if any)
- [ ] Fuel costs and consumption rates

**Phase 1 Deliverables:**
- ✅ Pure Blind systems spreadsheet with power/workforce
- [ ] SQLite database loaded with all system data
- [ ] Python data structure with complete system information
- [ ] Documented data sources and update procedures
- [ ] Data validation scripts

---

## PHASE 2: Graph Construction & Visualization
**Timeline: 2-3 weeks**
**Status: Core visualization engine**

### 2.1 NetworkX Graph Construction
**Goal: Build the computational graph for analysis**

**Tasks:**
- [ ] Import system data and create nodes with attributes
- [ ] Add stargate edges from SDE
- [ ] Calculate 3D->2D projection for planar visualization
- [ ] Validate graph completeness (all 85 systems connected)

**Technical Approach:**
```python
import networkx as nx

G = nx.Graph()

# Add nodes with full attributes
for system, data in system_data.items():
    G.add_node(system, **data)

# Add stargate edges
G.add_edges_from(gate_connections)

# Verify connectivity
assert nx.is_connected(G), "Graph should be fully connected"
```

### 2.2 Planar Layout Algorithm
**Goal: Dotlan-style readable 2D map**

**Challenges:**
- Pure Blind's actual 3D coordinates need projection to 2D
- Must preserve relative positions (recognize familiar shapes)
- Minimize edge crossings for readability

**Approaches (try in order):**
1. **Direct 3D projection** (use x,y coordinates, ignore z)
   - Pros: Preserves actual game layout
   - Cons: May have edge crossings
   
2. **Force-directed layout** (nx.spring_layout)
   - Pros: Minimizes crossings automatically
   - Cons: Doesn't match Dotlan/in-game map
   
3. **Manual position optimization** (hybrid approach)
   - Use 3D projection as starting point
   - Apply force-directed refinement with position constraints
   - Fine-tune manually for key systems

**Recommended: Start with #1, iterate to #3 if needed**

### 2.3 Interactive Visualization
**Goal: Dotlan-style interactive map**

**Technology Stack Options:**

**Option A: Matplotlib + Interactive Widgets (Simpler)**
- Pros: Python-native, good for analysis
- Cons: Limited interactivity, desktop-only

**Option B: Plotly (Better for interactive)**
- Pros: Interactive hover, zoom, click events
- Cons: More complex, but still Python-based

**Option C: Web-based (D3.js, Cytoscape.js) (Most powerful)**
- Pros: Full interactivity, shareable, modern UI
- Cons: Requires web dev knowledge (HTML/JS/CSS)

**Recommendation: Start with Plotly, migrate to web if needed**

### 2.4 Visual Elements

**Required Features:**
- [ ] System nodes (colored by constellation or sovereignty)
- [ ] Gate connections (thin gray lines)
- [ ] System labels (readable at default zoom)
- [ ] Hover tooltips (show system info)
- [ ] Click selection (highlight system and neighbors)
- [ ] Constellation boundaries (optional, visual grouping)
- [ ] Legend (color codes, symbols)

**Advanced Features (Phase 2+):**
- [ ] Ansiblex jump bridges (thick colored lines)
- [ ] Upgrade indicators (icons or node size)
- [ ] Strategic system highlighting (stars, special colors)
- [ ] Distance rings (show X-jump radius from selected system)
- [ ] Traffic heatmap (betweenness centrality visualization)

### 2.5 Layout Refinement
**Goal: Match Dotlan's readability**

**Tasks:**
- [ ] Compare with Dotlan's Pure Blind map
- [ ] Adjust node positions for constellation clustering
- [ ] Ensure gate connections don't overlap nodes
- [ ] Test readability at different zoom levels
- [ ] Get feedback from alliance members on recognizability

**Phase 2 Deliverables:**
- [ ] Working NetworkX graph with all Pure Blind data
- [ ] Interactive map visualization (Plotly or matplotlib)
- [ ] System click/hover information display
- [ ] Constellation color coding
- [ ] Export capability (PNG/SVG for sharing)

---

## PHASE 3: Sovereignty Upgrade Planning Tool
**Timeline: 2-3 weeks**
**Status: Core planning functionality**

### 3.1 Upgrade Calculator
**Goal: Calculate what fits in a system's power/workforce**

**Features:**
- [ ] Input: System selection
- [ ] Display: Current power/workforce capacity
- [ ] Interface: Add/remove upgrades interactively
- [ ] Validation: Real-time capacity checking
- [ ] Output: Upgrade list with totals

**UI Mockup:**
```
System: X-7OMU
Power: 2000 / 2500 (80% used)
Workforce: 15000 / 18000 (83% used)

Current Upgrades:
[Remove] Mining Lv 2        Power: 1000   Workforce: 8000
[Remove] Ratting Lv 1       Power: 1000   Workforce: 7000

Available Capacity:
Power: 500    Workforce: 3000

Add Upgrade: [Dropdown] [Add Button]

Warnings:
⚠️ Cannot fit Mining Lv 3 (needs 1500 power)
```

### 3.2 Preset Configurations
**Goal: Quick deployment of standard loadouts**

**Preset Types:**

**A. Maximum Mining**
```python
def max_mining_config(power, workforce):
    """
    Install largest mining upgrades that fit, plus belt upgrades
    """
    config = []
    # Try Mining Lv 5, then Lv 4, Lv 3, etc.
    for level in [5, 4, 3, 2, 1]:
        upgrade = mining_upgrades[level]
        if power >= upgrade['power'] and workforce >= upgrade['workforce']:
            config.append(('Mining', level))
            power -= upgrade['power']
            workforce -= upgrade['workforce']
            break
    
    # Add belt upgrades if capacity remains
    # ...
    
    return config
```

**B. Maximum Ratting (Subcap)**
```python
def max_ratting_config(power, workforce):
    """
    Prioritize Haven/Sanctum spawns for subcaps
    """
    # Similar approach, but prioritize:
    # 1. Pirate Detection Array (spawn rats)
    # 2. Survey Networks (more havens/sanctums)
```

**C. Balanced Economy**
```python
def balanced_config(power, workforce):
    """
    Mix of mining and ratting with surplus capacity
    """
    # 50/50 split of remaining capacity
```

**D. Strategic (PVP Focus)**
```python
def strategic_config(power, workforce):
    """
    Cyno jammer, cyno beacon, etc.
    """
```

### 3.3 Region-Wide Planning
**Goal: Optimize upgrade placement across all systems**

**Features:**
- [ ] System filtering (by constellation, security, attributes)
- [ ] Batch upgrade application
- [ ] Resource totals (alliance-wide capacity usage)
- [ ] Cost estimation (ISK for all upgrades)

**Example Workflow:**
```
1. Select all systems in U-7RBK constellation
2. Apply "Max Ratting" preset to all
3. Review total resource usage
4. Export shopping list for alliance
```

### 3.4 Mining Upgrade Clustering
**Goal: Place mining upgrades near industrial hubs**

**Algorithm:**
```python
def optimal_mining_placement(G, industrial_hubs, num_mining_systems):
    """
    Find best systems for mining upgrades based on:
    - Proximity to industrial hubs (minimize logistics)
    - Ice belt presence (bonus priority)
    - Moon count (bonus priority)
    - Constellation clustering (easier to defend)
    """
    scores = {}
    
    for system in G.nodes():
        score = 0
        
        # Distance to nearest industrial hub (lower is better)
        min_dist = min(nx.shortest_path_length(G, system, hub) 
                       for hub in industrial_hubs)
        score -= min_dist * 10  # Negative weight (closer = better)
        
        # Ice belt bonus
        if G.nodes[system]['has_ice']:
            score += 50
        
        # Moon bonus (more moons = better for moon mining)
        score += G.nodes[system]['moons'] * 2
        
        # Constellation clustering bonus
        constellation = G.nodes[system]['constellation']
        same_const_neighbors = sum(1 for n in G.neighbors(system)
                                   if G.nodes[n]['constellation'] == constellation)
        score += same_const_neighbors * 5
        
        scores[system] = score
    
    # Return top N systems
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:num_mining_systems]
```

### 3.5 Ratting Upgrade Placement
**Goal: Spread ratting systems across region**

**Considerations:**
- Avoid clustering (spread players out)
- Prioritize higher true-sec systems (better loot)
- Balance across constellations
- Consider proximity to staging (easy access)

**Algorithm:**
```python
def optimal_ratting_placement(G, staging_systems, num_ratting_systems):
    """
    Maximize coverage while avoiding over-concentration
    """
    # Use k-center or set cover approach
    # Ensure each constellation has ratting systems
    # Prioritize systems near staging but not too clustered
```

**Phase 3 Deliverables:**
- [ ] Interactive upgrade calculator (per system)
- [ ] Preset configuration buttons (max mining, max ratting, etc.)
- [ ] Real-time capacity validation and warnings
- [ ] Mining system clustering algorithm
- [ ] Ratting system distribution algorithm
- [ ] Export upgrade plans (CSV, text for alliance)

---

## PHASE 4: Ansiblex Jump Bridge Optimization
**Timeline: 3-4 weeks**
**Status: Advanced network optimization**

### 4.1 Jump Bridge Constraints
**Goal: Model all game mechanics accurately**

**Hard Constraints:**
- [ ] 5 light-year maximum range
- [ ] One jump bridge terminus per system
- [ ] Cannot cross certain space (e.g., can't bridge through enemy territory)
- [ ] Mass limit (1.48M tons - no supers)

**Soft Constraints:**
- [ ] ISK cost per bridge
- [ ] Fuel consumption considerations
- [ ] Defensive considerations (don't bridge into death traps)

**Implementation:**
```python
def can_build_bridge(G, system_a, system_b):
    """
    Check if bridge between systems is valid
    """
    # Calculate light-year distance using 3D coordinates
    coord_a = (G.nodes[system_a]['x'], G.nodes[system_a]['y'], G.nodes[system_a]['z'])
    coord_b = (G.nodes[system_b]['x'], G.nodes[system_b]['y'], G.nodes[system_b]['z'])
    
    distance_meters = euclidean_distance(coord_a, coord_b)
    distance_ly = distance_meters / METERS_PER_LIGHTYEAR
    
    if distance_ly > 5.0:
        return False, "Exceeds 5 LY range"
    
    # Check if either system already has a bridge
    if has_bridge(system_a) or has_bridge(system_b):
        return False, "System already has a bridge"
    
    return True, "Valid"
```

### 4.2 Strategic System Weighting
**Goal: Prioritize connectivity to important systems**

**Weight Factors:**
```python
strategic_weights = {
    'staging': 100,      # Highest priority - fleet staging
    'market': 80,        # High priority - trade hub
    'industrial': 80,    # High priority - manufacturing
    'moon_mining': 50,   # Medium priority - income generation
    'border': 40,        # Medium priority - defensive positions
    'ratting': 30,       # Low-medium priority
    'mining': 30,        # Low-medium priority
    'normal': 10,        # Baseline priority
}

def get_system_weight(system, strategic_systems):
    """
    Determine strategic importance of a system
    """
    for category, systems in strategic_systems.items():
        if system in systems:
            return strategic_weights[category]
    return strategic_weights['normal']
```

### 4.3 Bridge Placement Algorithms

**Approach A: Greedy Weighted Reduction**
```python
def greedy_bridge_placement(G, strategic_systems, max_bridges):
    """
    Iteratively add bridges that maximize reduction in 
    weighted average jumps to strategic systems
    """
    bridges = []
    
    for _ in range(max_bridges):
        best_bridge = None
        best_improvement = 0
        
        # Try all valid bridge pairs
        for sys_a in G.nodes():
            for sys_b in G.nodes():
                if sys_a == sys_b:
                    continue
                    
                can_build, reason = can_build_bridge(G, sys_a, sys_b)
                if not can_build:
                    continue
                
                # Calculate improvement
                improvement = calculate_weighted_improvement(
                    G, sys_a, sys_b, strategic_systems
                )
                
                if improvement > best_improvement:
                    best_improvement = improvement
                    best_bridge = (sys_a, sys_b)
        
        if best_bridge:
            bridges.append(best_bridge)
            G.add_edge(best_bridge[0], best_bridge[1], type='ansiblex')
        else:
            break  # No more valid bridges
    
    return bridges
```

**Approach B: Optimization with Constraints**
```python
def optimize_bridges_ilp(G, strategic_systems, max_bridges):
    """
    Use integer linear programming to find optimal bridge network
    
    Minimize: Weighted sum of distances to strategic systems
    Subject to:
    - Max N bridges
    - 5 LY range constraints
    - One bridge per system constraints
    """
    # Use scipy.optimize.linprog or pulp library
    # This is more complex but can find globally optimal solutions
```

**Approach C: Genetic Algorithm**
```python
def evolve_bridge_network(G, strategic_systems, max_bridges, generations=1000):
    """
    Use genetic algorithm to evolve optimal bridge placements
    
    Chromosome: List of (system_a, system_b) bridge pairs
    Fitness: Inverse of weighted average jumps to strategic systems
    Mutation: Add/remove/swap bridge
    Crossover: Combine bridge sets from two parents
    """
    # Advantage: Can explore more of the solution space
    # Disadvantage: No guarantee of global optimum
```

**Recommendation: Start with Approach A (Greedy), compare with B if needed**

### 4.4 Network Analysis Metrics

**Goal: Quantify bridge network effectiveness**

**Metrics to Calculate:**
- [ ] Average jumps to each strategic system (before/after)
- [ ] Maximum jumps to any strategic system (worst-case)
- [ ] Network diameter (longest shortest path)
- [ ] Betweenness centrality changes (new chokepoints)
- [ ] Alternative routes created (redundancy)
- [ ] ISK cost of bridge network

**Visualization:**
```python
def compare_networks(G_before, G_after, strategic_systems):
    """
    Create before/after comparison
    """
    # Calculate improvements
    improvements = {}
    
    for system in G_before.nodes():
        for strat_cat, strat_systems in strategic_systems.items():
            for strat_sys in strat_systems:
                before_dist = nx.shortest_path_length(G_before, system, strat_sys)
                after_dist = nx.shortest_path_length(G_after, system, strat_sys)
                improvement = before_dist - after_dist
                
                improvements[f"{system} to {strat_sys}"] = improvement
    
    return improvements
```

### 4.5 Interactive Bridge Planning

**UI Features:**
- [ ] Click two systems to propose bridge
- [ ] Show validity (range check, conflicts)
- [ ] Show impact on network metrics
- [ ] "Suggest Next Bridge" button (run greedy algorithm)
- [ ] "Optimize All Bridges" button (run full optimization)
- [ ] Undo/redo functionality
- [ ] Save/load bridge configurations

**Phase 4 Deliverables:**
- [ ] Light-year distance calculator
- [ ] Bridge validity checker
- [ ] Strategic system weighting system
- [ ] Greedy bridge placement algorithm
- [ ] Network comparison metrics
- [ ] Interactive bridge planning UI
- [ ] Before/after visualization comparison
- [ ] Export bridge construction orders

---

## PHASE 5: Polish & Advanced Features
**Timeline: 2-3 weeks**
**Status: Quality of life improvements**

### 5.1 Data Export & Sharing
- [ ] Export upgrade plans (markdown, CSV, Discord-friendly)
- [ ] Export bridge plans with coordinates
- [ ] Screenshot/image export of map
- [ ] Share links (if web-based)

### 5.2 What-If Analysis
- [ ] Save multiple scenarios
- [ ] Compare scenarios side-by-side
- [ ] Cost estimation for each scenario
- [ ] Timeline planning (upgrade deployment order)

### 5.3 Integration with External Data
- [ ] Import current sovereignty data (via ESI or manual)
- [ ] Import kill/NPC kill data (for traffic analysis)
- [ ] Market price data (for cost calculations)

### 5.4 Advanced Visualizations
- [ ] Heatmaps (traffic, upgrades, strategic value)
- [ ] 3D view (optional, cool but not necessary)
- [ ] Animation (show route paths, bridge impact)
- [ ] Constellation-level summary views

### 5.5 Documentation & Tutorials
- [ ] User guide (how to use the tool)
- [ ] Theory documentation (algorithms explained)
- [ ] Example scenarios
- [ ] Video walkthrough (optional)

---

## Technical Architecture

### Technology Stack Recommendation

**Backend / Core:**
- Python 3.10+
- NetworkX (graph algorithms)
- Pandas (data manipulation)
- NumPy (numerical calculations)
- SQLite (data storage)

**Visualization (Choose One):**
- **Option A: Plotly** (interactive, Python-based, easiest)
  - Pros: Python-native, interactive graphs, no web dev needed
  - Cons: Desktop-only, can be slow with large graphs
  
- **Option B: Dash** (Plotly + web framework)
  - Pros: Web-based, shareable, still Python
  - Cons: More setup, requires server
  
- **Option C: React + Cytoscape.js** (full web app)
  - Pros: Most powerful, beautiful, shareable
  - Cons: Requires JavaScript knowledge

**Recommended: Start with Plotly, migrate to Dash if sharing is needed**

### Data Storage

```
project/
├── data/
│   ├── sde/
│   │   └── sqlite-latest.sqlite          # From Fuzzwork
│   ├── pure_blind_systems.xlsx           # Your spreadsheet
│   ├── sovereignty_upgrades.json         # Upgrade database
│   └── strategic_systems.json            # Staging, industrial, etc.
├── src/
│   ├── data_loader.py                    # Import from SDE/spreadsheet
│   ├── graph_builder.py                  # Build NetworkX graph
│   ├── visualization.py                  # Plotly/matplotlib viz
│   ├── upgrade_calculator.py             # Phase 3 logic
│   ├── bridge_optimizer.py               # Phase 4 logic
│   └── utils.py                          # Helper functions
├── notebooks/
│   ├── 01_data_exploration.ipynb         # Jupyter for analysis
│   ├── 02_visualization_testing.ipynb
│   └── 03_algorithm_testing.ipynb
└── outputs/
    ├── maps/                             # Generated visualizations
    ├── plans/                            # Exported upgrade/bridge plans
    └── scenarios/                        # Saved configurations
```

### Development Workflow

1. **Jupyter Notebooks** for exploration and prototyping
2. **Python modules** for production code
3. **Version control** (Git) for collaboration
4. **Testing** (pytest) for critical algorithms

---

## Success Metrics

### Phase 1 Complete When:
- [x] All Pure Blind system data imported and validated
- [ ] SQLite database accessible and queryable
- [ ] Data quality verified (no missing systems, all connections valid)

### Phase 2 Complete When:
- [ ] Map generates and displays all 85 systems
- [ ] Layout is recognizable vs Dotlan
- [ ] Interactive features work (hover, click, zoom)
- [ ] Alliance members can identify systems by position

### Phase 3 Complete When:
- [ ] Can calculate upgrade fits for any system
- [ ] Presets work correctly (max mining, max ratting)
- [ ] Mining clustering algorithm produces sensible results
- [ ] Can export complete upgrade plan for alliance

### Phase 4 Complete When:
- [ ] Can suggest valid bridge placements
- [ ] Algorithm respects all constraints (range, one per system)
- [ ] Weighted optimization produces better results than random
- [ ] Can demonstrate improvement in connectivity metrics

### Project Complete When:
- [ ] Tool is being actively used for sovereignty planning
- [ ] Decisions made based on tool recommendations
- [ ] Positive feedback from alliance/coalition leadership
- [ ] Documentation allows others to use without assistance

---

## Risk Mitigation

### Technical Risks
| Risk | Mitigation |
|------|------------|
| Layout doesn't match Dotlan | Start with 3D projection, iterate; worst case: manual position tuning |
| Optimization is too slow | Use greedy algorithm first; optimize hot paths; cache results |
| Bridge algorithm too complex | Start with simple greedy; add sophistication later |
| Data quality issues | Validation scripts; manual review; community feedback |

### Project Risks
| Risk | Mitigation |
|------|------------|
| Feature creep | Stick to phased plan; add features only after phase complete |
| Incomplete domain knowledge | Consult alliance experts; iterate based on feedback |
| Changing game mechanics | Modular design; easy to update parameters |
| Loss of interest | Focus on quick wins; show progress regularly |

---

## Next Steps

### Immediate Actions (Next 7 Days):
1. [ ] Download Fuzzwork's SQLite database
2. [ ] Write data import script (SDE + spreadsheet)
3. [ ] Build basic NetworkX graph
4. [ ] Generate first visualization (any layout)
5. [ ] Research sovereignty upgrade mechanics (Eve University Wiki)

### Short Term (Weeks 2-3):
1. [ ] Refine layout to match Dotlan
2. [ ] Add interactive features (hover, click)
3. [ ] Build upgrade database (JSON file)
4. [ ] Implement basic upgrade calculator

### Medium Term (Weeks 4-8):
1. [ ] Complete Phase 3 (upgrade planning)
2. [ ] Get feedback from alliance members
3. [ ] Iterate on UX based on feedback
4. [ ] Begin Phase 4 (bridge optimization)

### Long Term (Weeks 9-12):
1. [ ] Complete Phase 4
2. [ ] Polish and documentation
3. [ ] Deploy for alliance use
4. [ ] Collect feedback and iterate

---

## Questions to Research

1. **Sovereignty Upgrades:**
   - What are the exact power/workforce costs?
   - What are all available upgrade types?
   - How do they tier (Lv 1, Lv 2, etc.)?

2. **Ansiblex Bridges:**
   - Current ISK cost to build?
   - Fuel consumption rates?
   - Can you bridge TO a system without FROM permissions?

3. **Strategic Systems:**
   - Which systems are current staging/industrial hubs?
   - Are there future plans to move these?
   - What defines a "good" industrial hub?

4. **Alliance Constraints:**
   - Budget for bridges? (limit optimization)
   - Upgrade priorities? (mining vs ratting emphasis)
   - Defensive considerations? (don't bridge into gatecamps)

---

## Conclusion

This is an ambitious but achievable project. The phased approach allows for:
- Quick wins (Phase 1-2 can be done in a month)
- Iterative feedback (test with alliance members early)
- Flexibility (can skip/reorder phases based on priorities)
- Sustainability (modular design allows maintenance)

**Recommended Start:** Focus on Phase 1 data acquisition this week. Once you have clean data, the rest follows naturally.

Good luck, and feel free to ask for help on any specific phase!
