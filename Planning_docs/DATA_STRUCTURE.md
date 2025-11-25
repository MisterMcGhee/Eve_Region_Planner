# Pure Blind Planning Tool - Data Structures

This document defines all data models, schemas, and structures used in the project.

---

## Table of Contents
1. [System Data](#system-data)
2. [Network Graph](#network-graph)
3. [Sovereignty Upgrades](#sovereignty-upgrades)
4. [Ansiblex Bridges](#ansiblex-bridges)
5. [Strategic Classifications](#strategic-classifications)
6. [Application State](#application-state)
7. [Export Formats](#export-formats)

---

## System Data

### Source: Pure Blind Systems Spreadsheet
**File:** `pure_blind_systems.xlsx`

### Schema

| Field | Type | Description | Example | Source |
|-------|------|-------------|---------|--------|
| `system_name` | string | System name | "X-7OMU" | SDE |
| `system_id` | integer | Unique system ID | 30003730 | SDE |
| `constellation` | string | Constellation name | "38G6-L" | SDE |
| `constellation_id` | integer | Constellation ID | 20000482 | SDE |
| `region` | string | Always "Pure Blind" | "Pure Blind" | SDE |
| `region_id` | integer | Always 10000023 | 10000023 | SDE |
| `security` | float | True security status | -0.142 | SDE |
| `x` | float | X coordinate (meters) | -1.23e17 | SDE |
| `y` | float | Y coordinate (meters) | 4.56e16 | SDE |
| `z` | float | Z coordinate (meters) | 7.89e16 | SDE |
| `power_capacity` | integer | Max power | 2500 | Manual/Dotlan |
| `workforce_capacity` | integer | Max workforce | 18000 | Manual/Dotlan |
| `has_ice` | boolean | Ice belt present | True | Manual |
| `moons` | integer | Number of moons | 76 | SDE |
| `planets` | integer | Number of planets | 8 | SDE |
| `belts` | integer | Number of asteroid belts | 12 | SDE |

### Example JSON
```json
{
  "system_name": "X-7OMU",
  "system_id": 30003730,
  "constellation": "38G6-L",
  "constellation_id": 20000482,
  "region": "Pure Blind",
  "region_id": 10000023,
  "security": -0.142,
  "x": -123456789012345600.0,
  "y": 45678901234560000.0,
  "z": 78901234567890000.0,
  "power_capacity": 2500,
  "workforce_capacity": 18000,
  "has_ice": false,
  "moons": 76,
  "planets": 8,
  "belts": 12
}
```

### CSV Format
```csv
system_name,system_id,constellation,security,power_capacity,workforce_capacity,has_ice,moons
X-7OMU,30003730,38G6-L,-0.142,2500,18000,False,76
```

---

## Network Graph

### Structure: NetworkX Graph
**File:** `pure_blind_graph.graphml`

### Node Attributes
Each system is a node with attributes:

```python
G.nodes['X-7OMU'] = {
    'system_id': 30003730,
    'constellation': '38G6-L',
    'constellation_id': 20000482,
    'security': -0.142,
    'x': -123456789012345600.0,
    'y': 45678901234560000.0,
    'z': 78901234567890000.0,
    'power_capacity': 2500,
    'workforce_capacity': 18000,
    'has_ice': False,
    'moons': 76,
    'planets': 8,
    'belts': 12,
}
```

### Edge Attributes
Each stargate connection is an edge:

```python
G.edges[('X-7OMU', '5ZXX-K')] = {
    'type': 'stargate',  # or 'ansiblex' for jump bridges
    'distance_ly': 4.2,  # light-years (calculated from 3D coordinates)
}
```

### GraphML Format
```xml
<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
  <key id="system_id" for="node" attr.name="system_id" attr.type="int"/>
  <key id="power_capacity" for="node" attr.name="power_capacity" attr.type="int"/>
  <!-- ... more keys ... -->
  <graph id="Pure_Blind" edgedefault="undirected">
    <node id="X-7OMU">
      <data key="system_id">30003730</data>
      <data key="power_capacity">2500</data>
      <!-- ... more attributes ... -->
    </node>
    <edge source="X-7OMU" target="5ZXX-K">
      <data key="type">stargate</data>
    </edge>
  </graph>
</graphml>
```

### JSON Format (Alternative)
```json
{
  "nodes": [
    {
      "id": "X-7OMU",
      "system_id": 30003730,
      "constellation": "38G6-L",
      "power_capacity": 2500,
      "workforce_capacity": 18000,
      "has_ice": false,
      "moons": 76
    }
  ],
  "edges": [
    {
      "source": "X-7OMU",
      "target": "5ZXX-K",
      "type": "stargate"
    }
  ]
}
```

---

## Sovereignty Upgrades

### Upgrade Definition Schema

```python
upgrade_definition = {
    'type': str,        # 'mining', 'ratting', 'belt', 'cyno_jammer', etc.
    'name': str,        # 'Minmatar Mining Upgrade'
    'level': int,       # 1, 2, or 3
    'power': int,       # Power requirement
    'workforce': int,   # Workforce requirement
    'effects': list,    # List of effect descriptions
    'isk_cost': int,    # ISK to install (optional)
    'fuel_per_hour': int,  # Fuel consumption (optional)
}
```

### Example Upgrade Definitions

```json
{
  "upgrades": [
    {
      "type": "mining",
      "name": "Minmatar Mining Upgrade I",
      "level": 1,
      "power": 500,
      "workforce": 5000,
      "effects": [
        "Increases ore yield by 20%",
        "Adds additional asteroid belts"
      ],
      "isk_cost": 150000000,
      "fuel_per_hour": 100
    },
    {
      "type": "mining",
      "name": "Minmatar Mining Upgrade II",
      "level": 2,
      "power": 1000,
      "workforce": 8000,
      "effects": [
        "Increases ore yield by 40%",
        "Adds additional asteroid belts",
        "Improved asteroid respawn rate"
      ],
      "isk_cost": 300000000,
      "fuel_per_hour": 200
    },
    {
      "type": "ratting",
      "name": "Pirate Detection Array I",
      "level": 1,
      "power": 800,
      "workforce": 6000,
      "effects": [
        "Enables combat anomaly spawns",
        "Increases anomaly spawn rate by 25%"
      ],
      "isk_cost": 200000000,
      "fuel_per_hour": 150
    },
    {
      "type": "belt",
      "name": "Ore Prospecting Array I",
      "level": 1,
      "power": 300,
      "workforce": 2000,
      "effects": [
        "Increases asteroid belt density",
        "Rare ore spawn chance +10%"
      ],
      "isk_cost": 100000000,
      "fuel_per_hour": 50
    },
    {
      "type": "cyno_jammer",
      "name": "Cynosural System Jammer",
      "level": 1,
      "power": 1200,
      "workforce": 10000,
      "effects": [
        "Prevents hostile cyno from opening",
        "Does not affect covert cynos"
      ],
      "isk_cost": 500000000,
      "fuel_per_hour": 300
    }
  ]
}
```

### System Upgrade Configuration

```python
system_upgrades = {
    'X-7OMU': [
        {
            'type': 'mining',
            'name': 'Minmatar Mining Upgrade II',
            'level': 2,
            'power': 1000,
            'workforce': 8000,
        },
        {
            'type': 'belt',
            'name': 'Ore Prospecting Array I',
            'level': 1,
            'power': 300,
            'workforce': 2000,
        },
    ],
    '5ZXX-K': [
        {
            'type': 'cyno_jammer',
            'name': 'Cynosural System Jammer',
            'level': 1,
            'power': 1200,
            'workforce': 10000,
        },
    ],
}
```

### Usage Calculation

```python
def calculate_usage(system_name, upgrades):
    """Calculate power and workforce usage for a system"""
    total_power = sum(u['power'] for u in upgrades)
    total_workforce = sum(u['workforce'] for u in upgrades)
    
    capacity = get_system_capacity(system_name)
    
    return {
        'power_used': total_power,
        'power_capacity': capacity['power'],
        'power_remaining': capacity['power'] - total_power,
        'power_percent': (total_power / capacity['power']) * 100,
        'workforce_used': total_workforce,
        'workforce_capacity': capacity['workforce'],
        'workforce_remaining': capacity['workforce'] - total_workforce,
        'workforce_percent': (total_workforce / capacity['workforce']) * 100,
        'valid': (total_power <= capacity['power'] and 
                 total_workforce <= capacity['workforce']),
    }
```

---

## Ansiblex Bridges

### Bridge Schema

```python
bridge = {
    'from': str,        # System name
    'to': str,          # System name
    'distance_ly': float,  # Distance in light-years
    'valid': bool,      # Within 5 LY constraint
    'isk_cost': int,    # Construction cost (optional)
    'fuel_per_jump': int,  # Fuel consumption (optional)
}
```

### Example Bridge List

```json
{
  "bridges": [
    {
      "from": "5ZXX-K",
      "to": "X-7OMU",
      "distance_ly": 4.2,
      "valid": true,
      "isk_cost": 1000000000,
      "fuel_per_jump": 50
    },
    {
      "from": "X-7OMU",
      "to": "EC-P8R",
      "distance_ly": 3.8,
      "valid": true,
      "isk_cost": 1000000000,
      "fuel_per_jump": 50
    }
  ]
}
```

### CSV Format
```csv
from,to,distance_ly,valid,constellation_from,constellation_to
5ZXX-K,X-7OMU,4.2,True,U-7RBK,38G6-L
X-7OMU,EC-P8R,3.8,True,38G6-L,YS-GOP
```

### Distance Calculation

```python
def calculate_distance_ly(system1, system2):
    """Calculate distance in light-years between two systems"""
    import math
    
    # Get 3D coordinates
    x1, y1, z1 = G.nodes[system1]['x'], G.nodes[system1]['y'], G.nodes[system1]['z']
    x2, y2, z2 = G.nodes[system2]['x'], G.nodes[system2]['y'], G.nodes[system2]['z']
    
    # Calculate Euclidean distance in meters
    distance_m = math.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)
    
    # Convert to light-years (1 LY ≈ 9.461e15 meters)
    distance_ly = distance_m / 9.461e15
    
    return distance_ly
```

### Validation

```python
def validate_bridge(from_system, to_system, existing_bridges):
    """Validate if a bridge can be added"""
    
    # Check distance constraint (5 LY max)
    distance = calculate_distance_ly(from_system, to_system)
    if distance > 5.0:
        return False, f"Distance too far: {distance:.2f} LY (max 5.0 LY)"
    
    # Check one-per-system constraint
    for bridge in existing_bridges:
        if from_system in (bridge['from'], bridge['to']):
            return False, f"{from_system} already has a bridge"
        if to_system in (bridge['from'], bridge['to']):
            return False, f"{to_system} already has a bridge"
    
    return True, f"Valid bridge: {distance:.2f} LY"
```

---

## Strategic Classifications

### Strategic System Schema

```python
strategic_systems = {
    'staging': list,        # Staging systems
    'industrial': list,     # Industrial hubs
    'market': list,         # Market hubs
    'moon_mining': list,    # Moon mining systems
    'border': list,         # Border/entry systems
    'ratting': list,        # Ratting systems
    'mining': list,         # Mining systems
}
```

### Example

```json
{
  "strategic_systems": {
    "staging": ["5ZXX-K"],
    "industrial": ["X-7OMU", "EC-P8R"],
    "market": ["X-7OMU"],
    "moon_mining": ["KQK1-2", "O-N8XZ", "BDV3-T"],
    "border": ["J-CIJV", "Y-C3EQ", "O-BY0Y"],
    "ratting": ["EC-P8R", "KLY-C0", "MI6O-6"],
    "mining": ["KQK1-2", "O-N8XZ", "EC-P8R", "DK-FXK"]
  }
}
```

### Weights for Optimization

```python
strategic_weights = {
    'staging': 100,      # Highest priority
    'market': 80,        # High priority
    'industrial': 80,    # High priority
    'moon_mining': 50,   # Medium priority
    'border': 40,        # Medium priority
    'ratting': 30,       # Low-medium priority
    'mining': 30,        # Low-medium priority
    'normal': 10,        # Baseline
}
```

---

## Application State

### Dash App State Schema

```python
app_state = {
    'active_tool': str,              # Current tool mode
    'graph': nx.Graph,               # NetworkX graph
    'bridges': list,                 # List of Ansiblex bridges
    'system_upgrades': dict,         # System -> upgrades mapping
    'strategic_systems': dict,       # Strategic classifications
    'selected_system': str,          # Currently selected system
    'reference_system': str,         # Reference for distance calculations
    'optimization_results': dict,    # Results from optimization algorithms
    'history': list,                 # Undo/redo history
}
```

### Example State

```json
{
  "active_tool": "upgrades",
  "bridges": [
    {"from": "5ZXX-K", "to": "X-7OMU", "distance_ly": 4.2}
  ],
  "system_upgrades": {
    "X-7OMU": [
      {"type": "mining", "level": 2, "power": 1000, "workforce": 8000}
    ]
  },
  "strategic_systems": {
    "staging": ["5ZXX-K"],
    "industrial": ["X-7OMU"]
  },
  "selected_system": "X-7OMU",
  "reference_system": "5ZXX-K",
  "optimization_results": {},
  "history": []
}
```

### State Persistence

**Browser Storage (dcc.Store):**
```python
dcc.Store(id='app-state', data=app_state, storage_type='session')
```

**File Export (JSON):**
```python
import json

def save_state(app_state, filename):
    """Save state to file"""
    # Convert NetworkX graph to dict
    state_copy = app_state.copy()
    state_copy['graph'] = nx.node_link_data(state_copy['graph'])
    
    with open(filename, 'w') as f:
        json.dump(state_copy, f, indent=2)

def load_state(filename):
    """Load state from file"""
    with open(filename, 'r') as f:
        state = json.load(f)
    
    # Convert dict back to NetworkX graph
    state['graph'] = nx.node_link_graph(state['graph'])
    
    return state
```

---

## Export Formats

### CSV Export - Bridge List
```csv
from,to,distance_ly,constellation_from,constellation_to
5ZXX-K,X-7OMU,4.2,U-7RBK,38G6-L
X-7OMU,EC-P8R,3.8,38G6-L,YS-GOP
```

### CSV Export - Upgrade Configuration
```csv
system,upgrade_type,upgrade_level,power,workforce
X-7OMU,mining,2,1000,8000
X-7OMU,belt,1,300,2000
5ZXX-K,cyno_jammer,1,1200,10000
```

### Discord-Friendly Text Format
```
Pure Blind Upgrade Shopping List
================================

X-7OMU (38G6-L):
  • Mining Upgrade II (1000 P, 8000 WF)
  • Belt Upgrade I (300 P, 2000 WF)
  Total: 1300 P, 10000 WF (52% power, 56% workforce)

EC-P8R (YS-GOP):
  • Ratting Upgrade II (1200 P, 9000 WF)
  Total: 1200 P, 9000 WF (75% power, 30% workforce)

REGION TOTALS:
  Power: 12,500 / 200,000 (6%)
  Workforce: 85,000 / 1,200,000 (7%)
  Estimated ISK: 4.5B
```

### Markdown Report
```markdown
# Pure Blind Sovereignty Plan

## Ansiblex Bridge Network

### Bridges (3 total)
- 5ZXX-K ↔ X-7OMU (4.2 LY)
- X-7OMU ↔ EC-P8R (3.8 LY)
- EC-P8R ↔ KQK1-2 (4.9 LY)

### Impact Metrics
- Average jumps to staging: 4.2 → 3.1 (-26%)
- Average jumps to industrial: 5.1 → 3.8 (-25%)
- Average jumps to market: 5.1 → 3.8 (-25%)

## System Upgrades

### Mining Systems (10)
1. **X-7OMU** (38G6-L)
   - Mining Upgrade II (1000 P, 8000 WF)
   - Belt Upgrade I (300 P, 2000 WF)

...
```

---

## Data Validation

### System Validation
```python
def validate_system(system_data):
    """Validate system data completeness and correctness"""
    required_fields = [
        'system_name', 'system_id', 'constellation', 'security',
        'power_capacity', 'workforce_capacity', 'has_ice', 'moons'
    ]
    
    for field in required_fields:
        if field not in system_data:
            return False, f"Missing field: {field}"
    
    if system_data['power_capacity'] < 0:
        return False, "Power capacity cannot be negative"
    
    if system_data['workforce_capacity'] < 0:
        return False, "Workforce capacity cannot be negative"
    
    return True, "Valid"
```

### Graph Validation
```python
def validate_graph(G):
    """Validate graph structure"""
    # Check connectivity
    if not nx.is_connected(G):
        return False, "Graph is not fully connected"
    
    # Check all systems have required attributes
    for node in G.nodes():
        if 'power_capacity' not in G.nodes[node]:
            return False, f"System {node} missing power_capacity"
    
    # Check all edges are valid
    for edge in G.edges():
        if 'type' not in G.edges[edge]:
            return False, f"Edge {edge} missing type"
    
    return True, "Valid graph"
```

---

## Database Schema (Future: SQLite)

If we migrate to a database, here's the proposed schema:

```sql
-- Systems table
CREATE TABLE systems (
    system_id INTEGER PRIMARY KEY,
    system_name TEXT NOT NULL,
    constellation_id INTEGER,
    constellation TEXT,
    region_id INTEGER,
    security REAL,
    x REAL,
    y REAL,
    z REAL,
    power_capacity INTEGER,
    workforce_capacity INTEGER,
    has_ice BOOLEAN,
    moons INTEGER,
    planets INTEGER,
    belts INTEGER
);

-- Gates table
CREATE TABLE gates (
    from_system_id INTEGER,
    to_system_id INTEGER,
    PRIMARY KEY (from_system_id, to_system_id),
    FOREIGN KEY (from_system_id) REFERENCES systems(system_id),
    FOREIGN KEY (to_system_id) REFERENCES systems(system_id)
);

-- Bridges table
CREATE TABLE bridges (
    bridge_id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_system_id INTEGER,
    to_system_id INTEGER,
    distance_ly REAL,
    created_at TIMESTAMP,
    FOREIGN KEY (from_system_id) REFERENCES systems(system_id),
    FOREIGN KEY (to_system_id) REFERENCES systems(system_id)
);

-- Upgrades table
CREATE TABLE upgrades (
    upgrade_id INTEGER PRIMARY KEY AUTOINCREMENT,
    system_id INTEGER,
    upgrade_type TEXT,
    upgrade_level INTEGER,
    power INTEGER,
    workforce INTEGER,
    created_at TIMESTAMP,
    FOREIGN KEY (system_id) REFERENCES systems(system_id)
);

-- Strategic classifications table
CREATE TABLE strategic_systems (
    system_id INTEGER,
    classification TEXT,
    PRIMARY KEY (system_id, classification),
    FOREIGN KEY (system_id) REFERENCES systems(system_id)
);
```

---

**Version:** 1.0  
**Last Updated:** November 25, 2025
