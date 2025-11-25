# Pure Blind Planning Tool - UI/UX Architecture (REVISED)

## Design Philosophy: Control Panel + Visualization Dashboard

**LEFT SIDE: Configuration & Controls**
- Menus, dropdowns, forms
- Where user makes all changes
- Data entry and selection

**RIGHT SIDE: Contextual Visualization**
- Dynamic display based on active tool
- Real-time feedback of changes
- Read-only visualization

---

## Split-Screen Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  Pure Blind Sovereignty Planning Tool                           │
├──────────────────────┬──────────────────────────────────────────┤
│                      │                                          │
│   CONTROL PANEL      │      VISUALIZATION DASHBOARD            │
│                      │                                          │
│   [Tool Selector]    │                                          │
│   ▼ Ansiblex Builder │                                          │
│     Upgrade Planner  │         [Context-dependent               │
│     Mining Optimizer │          visualization area]             │
│     Strategic View   │                                          │
│                      │                                          │
│   [Active Tool UI]   │                                          │
│   - Dropdowns        │                                          │
│   - Inputs           │                                          │
│   - Buttons          │                                          │
│   - Lists            │                                          │
│                      │                                          │
│   [Status/Feedback]  │                                          │
│                      │                                          │
└──────────────────────┴──────────────────────────────────────────┘
```

---

## Tool Modes & Their Visualizations

### MODE 1: Ansiblex Bridge Builder
**Left Panel - Controls:**
```
┌─────────────────────────┐
│ Ansiblex Bridge Builder │
├─────────────────────────┤
│                         │
│ Reference System:       │
│ [5ZXX-K        ▼]       │
│                         │
│ Add New Bridge:         │
│ From: [5ZXX-K      ▼]   │
│ To:   [X-7OMU      ▼]   │
│                         │
│ ✓ Valid (4.2 LY)        │
│ [ Add Bridge ]          │
│                         │
│ OR                      │
│                         │
│ [ Suggest Next Bridge ] │
│                         │
│ ───────────────────────│
│ Current Bridges: 3      │
│                         │
│ □ 5ZXX-K ↔ KI-TL0       │
│ □ X-7OMU ↔ J-CIJV       │
│ □ EC-P8R ↔ EWOK-K       │
│   [Remove Selected]     │
│                         │
│ ───────────────────────│
│ Strategic Systems:      │
│                         │
│ Staging: [5ZXX-K   ▼]   │
│ + Add                   │
│                         │
│ Industrial: [X-7OMU ▼]  │
│ + Add                   │
│                         │
│ Market: [X-7OMU    ▼]   │
│ + Add                   │
│                         │
│ ───────────────────────│
│ Impact Metrics:         │
│                         │
│ Avg jumps to staging:   │
│   Before: 4.2           │
│   After:  3.1  (-26%)   │
│                         │
│ Avg to industrial:      │
│   Before: 5.1           │
│   After:  3.8  (-25%)   │
│                         │
└─────────────────────────┘
```

**Right Panel - Visualization:**
- **Main:** Interactive graph showing:
  - Stargate connections (thin gray)
  - Ansiblex bridges (thick blue)
  - Selected reference system (highlighted)
  - Distance rings from reference (1-jump, 2-jump, etc.)
- **Overlay:** Jumps from reference system to all others (color gradient)
- **Legend:** Color scale, connection types

### MODE 2: System Upgrade Planner
**Left Panel - Controls:**
```
┌─────────────────────────┐
│ System Upgrade Planner  │
├─────────────────────────┤
│                         │
│ Select System:          │
│ [X-7OMU            ▼]   │
│                         │
│ System Info:            │
│   Constellation: 38G6-L │
│   Security: -0.14       │
│   Moons: 76             │
│   Ice: No               │
│                         │
│ ───────────────────────│
│ Add Upgrades:           │
│                         │
│ Type: [Mining      ▼]   │
│ Tier: [Level 2     ▼]   │
│ Power: 1000             │
│ Workforce: 8000         │
│                         │
│ [ Add Upgrade ]         │
│                         │
│ OR                      │
│                         │
│ [ Max Mining Preset ]   │
│ [ Max Ratting Preset ]  │
│ [ Balanced Preset ]     │
│                         │
│ ───────────────────────│
│ Current Upgrades:       │
│                         │
│ ☑ Mining Lv 2           │
│   P: 1000  WF: 8000     │
│                         │
│ ☑ Belt Upgrade Lv 1     │
│   P: 500   WF: 3000     │
│                         │
│ [Remove Selected]       │
│                         │
│ ───────────────────────│
│ Quick Actions:          │
│                         │
│ [ Clear All ]           │
│ [ Copy to Clipboard ]   │
│ [ Apply to Multiple ]   │
│                         │
└─────────────────────────┘
```

**Right Panel - Visualization:**
- **Top Half:** Capacity gauges
  ```
  Power Capacity:
  [████████████░░░░░░] 1500 / 2500 (60%)
  
  Workforce Capacity:
  [████████████████░░] 11000 / 13000 (85%)
  ```
- **Bottom Half:** Upgrade summary table
  ```
  ┌────────────────┬───────┬───────────┐
  │ Upgrade        │ Power │ Workforce │
  ├────────────────┼───────┼───────────┤
  │ Mining Lv 2    │  1000 │     8000  │
  │ Belt Upgrade 1 │   500 │     3000  │
  ├────────────────┼───────┼───────────┤
  │ TOTAL USED     │  1500 │    11000  │
  │ REMAINING      │  1000 │     2000  │
  └────────────────┴───────┴───────────┘
  
  ✓ Configuration valid
  ⚠ Only 2000 workforce remaining
  ```

### MODE 3: Mining System Optimizer
**Left Panel - Controls:**
```
┌─────────────────────────┐
│ Mining System Optimizer │
├─────────────────────────┤
│                         │
│ Optimization Settings:  │
│                         │
│ Industrial Hub:         │
│ [X-7OMU            ▼]   │
│ + Add Hub               │
│                         │
│ Number of Mining        │
│ Systems: [10       ▼]   │
│                         │
│ Priorities:             │
│ ☑ Ice belts (+50pts)    │
│ ☑ Moon count (+2/moon)  │
│ ☑ Constellation cluster │
│ ☐ High true-sec         │
│                         │
│ [ Run Optimization ]    │
│                         │
│ ───────────────────────│
│ Recommended Systems:    │
│                         │
│ 1. KQK1-2    Score: 87  │
│    - Ice: Yes           │
│    - Moons: 79          │
│    - Dist: 2 jumps      │
│    [ Configure ]        │
│                         │
│ 2. EC-P8R    Score: 85  │
│    - Ice: Yes           │
│    - Moons: 64          │
│    - Dist: 3 jumps      │
│    [ Configure ]        │
│                         │
│ 3. O-N8XZ    Score: 78  │
│    ...                  │
│                         │
│ [ Apply Mining to All ] │
│ [ Export List ]         │
│                         │
└─────────────────────────┘
```

**Right Panel - Visualization:**
- **Graph with Overlays:**
  - Industrial hubs (gold stars)
  - Recommended mining systems (green circles)
  - Non-selected systems (gray)
  - Distance rings from industrial hubs
  - Constellation boundaries highlighted
- **Score Legend:** Color gradient showing system scores

### MODE 4: Ratting System Optimizer
**Left Panel - Controls:**
```
┌─────────────────────────┐
│ Ratting System Optimizer│
├─────────────────────────┤
│                         │
│ Optimization Settings:  │
│                         │
│ Staging System:         │
│ [5ZXX-K            ▼]   │
│                         │
│ Number of Ratting       │
│ Systems: [15       ▼]   │
│                         │
│ Distribution:           │
│ ● Spread evenly         │
│ ○ Cluster near staging │
│ ○ One per constellation │
│                         │
│ Priorities:             │
│ ☑ Higher true-sec       │
│ ☑ Near staging (3-6j)   │
│ ☐ Avoid border systems  │
│                         │
│ [ Run Optimization ]    │
│                         │
│ ───────────────────────│
│ Recommended Systems:    │
│                         │
│ [List similar to mining]│
│                         │
│ [ Apply Ratting to All ]│
│ [ Export List ]         │
│                         │
└─────────────────────────┘
```

**Right Panel - Visualization:**
- **Graph showing:**
  - Staging system (blue star)
  - Recommended ratting systems (red circles)
  - Coverage heatmap (how far to nearest ratting system)
  - Constellation distribution

### MODE 5: Strategic Network Analysis
**Left Panel - Controls:**
```
┌─────────────────────────┐
│ Strategic Network View  │
├─────────────────────────┤
│                         │
│ Analysis Type:          │
│ [Chokepoints       ▼]   │
│                         │
│ Options:                │
│ - Chokepoints           │
│ - Traffic (Betweenness) │
│ - System Centrality     │
│ - Constellation Borders │
│ - Jump Distance Heatmap │
│                         │
│ ───────────────────────│
│ Results:                │
│                         │
│ Critical Chokepoints:   │
│                         │
│ 1. X-7OMU               │
│    Separates 38G6-L     │
│    from rest of region  │
│                         │
│ 2. J-CIJV               │
│    Constellation bridge │
│                         │
│ ...                     │
│                         │
│ [ Export Report ]       │
│                         │
└─────────────────────────┘
```

**Right Panel - Visualization:**
- **Dynamic based on analysis type:**
  - Chokepoints: Highlighted systems with warning icons
  - Traffic: Heatmap with node size = betweenness
  - Centrality: Color gradient from center to edge
  - Borders: Constellation regions with entry/exit gates
  - Distance: Heatmap from selected system

### MODE 6: Multi-System Configuration
**Left Panel - Controls:**
```
┌─────────────────────────┐
│ Batch Configuration     │
├─────────────────────────┤
│                         │
│ Select Systems:         │
│                         │
│ By Constellation:       │
│ ☑ U-7RBK (7 systems)    │
│ ☐ 38G6-L (8 systems)    │
│ ☑ YS-GOP (7 systems)    │
│ ...                     │
│                         │
│ OR                      │
│                         │
│ By Type:                │
│ ☑ Ice belt systems      │
│ ☐ High moon count (50+) │
│ ☐ Border systems        │
│                         │
│ Selected: 14 systems    │
│                         │
│ ───────────────────────│
│ Apply Configuration:    │
│                         │
│ Preset: [Max Mining ▼]  │
│                         │
│ [ Apply to Selected ]   │
│                         │
│ ───────────────────────│
│ Summary:                │
│                         │
│ Total Power Needed:     │
│   21,000               │
│                         │
│ Total Workforce Needed: │
│   112,000              │
│                         │
│ Systems Over Capacity:  │
│   2 (see warnings)      │
│                         │
│ [ Review Details ]      │
│ [ Export Shopping List ]│
│                         │
└─────────────────────────┘
```

**Right Panel - Visualization:**
- **Graph showing:**
  - Selected systems (highlighted)
  - Systems with valid config (green)
  - Systems over capacity (red)
  - Summary statistics table

---

## Technical Implementation Approaches

### Option A: Plotly Dash (Recommended)
**Pros:**
- Python-based (fits your existing code)
- Built-in components (dropdowns, buttons, graphs)
- Reactive callbacks (left changes update right automatically)
- Can deploy as web app

**Example Structure:**
```python
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go

app = dash.Dash(__name__)

app.layout = html.Div([
    # LEFT PANEL
    html.Div([
        html.H3("Control Panel"),
        dcc.Dropdown(id='tool-selector', 
                     options=['Ansiblex', 'Upgrades', 'Mining']),
        html.Div(id='tool-controls'),  # Dynamic controls
        html.Div(id='status-display'),
    ], style={'width': '30%', 'display': 'inline-block'}),
    
    # RIGHT PANEL
    html.Div([
        dcc.Graph(id='visualization'),  # Dynamic visualization
        html.Div(id='metrics-display'),
    ], style={'width': '70%', 'display': 'inline-block'}),
])

@app.callback(
    Output('visualization', 'figure'),
    Input('tool-selector', 'value'),
    Input('system-dropdown', 'value'),
    # ... other inputs
)
def update_visualization(tool, system, ...):
    if tool == 'Ansiblex':
        return create_bridge_graph(...)
    elif tool == 'Upgrades':
        return create_capacity_gauges(...)
    # ...
```

### Option B: Tkinter (Desktop App)
**Pros:**
- Standard Python library
- Native desktop feel
- Good for internal tools

**Cons:**
- More manual layout work
- Harder to share

### Option C: Web App (React + Python Backend)
**Pros:**
- Most flexible and powerful
- Modern UI/UX
- Easy to share

**Cons:**
- Requires JavaScript knowledge
- More complex architecture

**Recommendation: Start with Dash, migrate to web if needed**

---

## Component Library Needs

### Left Panel Components
- **Dropdown/Select** - System selection, upgrade types
- **Multi-select** - Constellation selection, system filters
- **Number input** - Capacity values, jump counts
- **Checkbox** - Toggle options
- **Radio buttons** - Exclusive choices
- **Buttons** - Actions (Add, Remove, Run, Export)
- **List with checkboxes** - Current upgrades, bridges
- **Status indicators** - Validation warnings, success messages

### Right Panel Components
- **Interactive graph** (Plotly)
- **Capacity gauges** (Progress bars or circular gauges)
- **Tables** - Upgrade summaries, metrics
- **Heatmaps** - Distance, traffic, scores
- **Statistics cards** - Numeric metrics
- **Legends** - Color codes, symbols

---

## State Management

The app needs to maintain:

```python
app_state = {
    'active_tool': 'ansiblex',
    'graph': G,  # NetworkX graph
    'bridges': [('5ZXX-K', 'X-7OMU'), ...],
    'system_upgrades': {
        'X-7OMU': [
            {'type': 'Mining', 'level': 2, 'power': 1000, 'workforce': 8000},
        ],
    },
    'strategic_systems': {
        'staging': ['5ZXX-K'],
        'industrial': ['X-7OMU'],
        'market': ['X-7OMU'],
    },
    'selected_system': 'X-7OMU',
    'reference_system': '5ZXX-K',  # For distance calculations
}
```

---

## Data Flow

```
User Action (Left Panel)
    ↓
State Update (Python backend)
    ↓
Visualization Regeneration (Right Panel)
    ↓
Display Update
```

Example:
1. User selects "Add Mining Lv 2" to X-7OMU
2. State updates: `system_upgrades['X-7OMU'].append(...)`
3. Recalculate: power used, workforce used
4. Regenerate: Capacity gauges on right panel
5. Display: Updated gauges + success message

---

## Workflow Examples

### Workflow 1: Adding an Ansiblex Bridge
```
1. Select "Ansiblex Builder" tool
2. Choose reference system: 5ZXX-K
3. Right panel shows: Graph with distance colors
4. Select "From": 5ZXX-K
5. Select "To": X-7OMU
6. System validates: ✓ Valid (4.2 LY)
7. Click "Add Bridge"
8. Right panel updates: 
   - Blue line between systems
   - Distance colors update (systems closer to 5ZXX-K now)
   - Metrics show: Avg jumps 4.2 → 3.1
9. Success message: "Bridge added"
```

### Workflow 2: Configuring System Upgrades
```
1. Select "System Upgrade Planner" tool
2. Choose system: X-7OMU
3. Right panel shows: Empty capacity gauges
4. Select upgrade type: Mining
5. Select tier: Level 2
6. System shows: Will use 1000 power, 8000 workforce
7. Click "Add Upgrade"
8. Right panel updates:
   - Power gauge: 0% → 40%
   - Workforce gauge: 0% → 61%
   - Table shows: Mining Lv 2 listed
9. Add another: Belt Upgrade Lv 1
10. Right panel updates again
11. Gauges show new totals
12. Warning if approaching capacity
```

### Workflow 3: Optimizing Mining Systems
```
1. Select "Mining System Optimizer" tool
2. Set industrial hub: X-7OMU
3. Set number of systems: 10
4. Check preferences: Ice belts, Moon count
5. Click "Run Optimization"
6. Left panel shows: Ranked list of systems
7. Right panel shows: 
   - Graph with hub (gold star)
   - Top 10 systems (green circles)
   - Distance rings
   - Score color gradient
8. Click "Configure" on EC-P8R
9. Tool switches to "Upgrade Planner" mode
10. EC-P8R pre-selected
11. Can now add mining upgrades
```

---

## Export Functions

Each tool needs export capability:

### Ansiblex Builder Exports:
- **Bridge Construction List** (CSV)
  ```
  From,To,Distance_LY,Constellation_From,Constellation_To
  5ZXX-K,X-7OMU,4.2,U-7RBK,38G6-L
  ```
- **Impact Report** (Markdown)
  ```markdown
  # Ansiblex Network Analysis
  
  ## Bridges Added: 3
  - 5ZXX-K ↔ X-7OMU (4.2 LY)
  - ...
  
  ## Impact Metrics
  Average jumps to staging: 4.2 → 3.1 (-26%)
  ...
  ```

### Upgrade Planner Exports:
- **Shopping List** (Text, Discord-friendly)
  ```
  Pure Blind Upgrade Shopping List
  
  X-7OMU:
  - Mining Upgrade II (1000 P, 8000 WF)
  - Belt Upgrade I (500 P, 3000 WF)
  
  EC-P8R:
  ...
  
  TOTALS:
  Power: 15,000
  Workforce: 85,000
  ```
- **System Configuration** (JSON)
  ```json
  {
    "X-7OMU": {
      "upgrades": [...],
      "power_used": 1500,
      "workforce_used": 11000
    }
  }
  ```

---

## Visual Design Principles

### Color Scheme
- **Background:** Dark theme (#1a1a1a) - easier on eyes for long sessions
- **Panel backgrounds:** Slightly lighter (#2a2a2a)
- **Accents:** Blue (#4ECDC4) for highlights
- **Status colors:**
  - Success: Green (#2ecc71)
  - Warning: Yellow (#f39c12)
  - Error: Red (#e74c3c)
  - Info: Blue (#3498db)

### Typography
- **Headers:** Bold, larger (16-18px)
- **Body:** Regular (12-14px)
- **Metrics:** Monospace (for alignment)

### Spacing
- Consistent padding: 10-20px
- Clear visual hierarchy
- Grouped related controls
- Dividers between sections

---

## Revised Project Phases

### Phase 1: Data Acquisition ✓ (Same as before)
- Load SDE
- Merge spreadsheet
- Build graph

### Phase 2: UI Framework (2-3 weeks) ← REVISED
- Set up Dash application
- Create split-screen layout
- Implement tool selector
- Create basic graph visualization
- Build navigation between tools

**Deliverable:** Working shell with tool switching

### Phase 3A: Ansiblex Builder (2 weeks)
- Left: Bridge selection dropdowns
- Left: Strategic system inputs
- Right: Graph with bridges
- Right: Distance metrics
- Export functions

### Phase 3B: Upgrade Planner (2 weeks)
- Left: System selector + upgrade dropdowns
- Right: Capacity gauges
- Right: Upgrade summary table
- Preset buttons
- Validation logic

### Phase 3C: Mining Optimizer (2 weeks)
- Left: Optimization settings
- Algorithm: Clustering logic
- Right: Graph with highlighted systems
- Right: Score visualization

### Phase 3D: Ratting Optimizer (1 week)
- Similar to mining, different algorithm
- Spread vs. cluster logic

### Phase 4: Strategic Analysis (1 week)
- Chokepoint detection
- Traffic analysis
- Centrality metrics
- Multiple visualization modes

### Phase 5: Polish (1-2 weeks)
- Multi-system batch configuration
- Export improvements
- Documentation
- Testing with alliance members

---

## Success Criteria (Revised)

### Phase 2 Complete:
- [ ] Can switch between tool modes
- [ ] Each mode shows appropriate controls and visualization
- [ ] Graph displays correctly
- [ ] Basic state management works

### Phase 3A Complete:
- [ ] Can add/remove bridges via dropdowns
- [ ] Graph shows bridges visually
- [ ] Distance metrics calculate correctly
- [ ] Can export bridge list

### Phase 3B Complete:
- [ ] Can select system and add upgrades
- [ ] Capacity validation works
- [ ] Gauges update in real-time
- [ ] Presets apply correctly

### Phase 3C/D Complete:
- [ ] Optimization produces sensible results
- [ ] Graph highlights recommended systems
- [ ] Can configure selected systems

### Project Complete:
- [ ] Alliance leadership uses tool for planning
- [ ] All tools work together (shared state)
- [ ] Can export plans for alliance consumption
- [ ] Documentation complete

---

## Next Steps with New Architecture

1. **This Week:**
   - [x] Complete Phase 1 (data acquisition)
   - [ ] Set up Dash application structure
   - [ ] Create basic split-screen layout
   - [ ] Implement tool selector dropdown

2. **Next Week:**
   - [ ] Build first tool: Ansiblex Builder
   - [ ] Get feedback on UI/UX
   - [ ] Iterate on layout

3. **Following Weeks:**
   - [ ] Add remaining tools one by one
   - [ ] Test with alliance members
   - [ ] Refine based on feedback

The split-screen design is much cleaner and will be easier to use!
