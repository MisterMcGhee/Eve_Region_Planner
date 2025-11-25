# Pure Blind Planning Tool - Project Status

**Last Updated:** November 25, 2025  
**Version:** 0.2.0-alpha  
**Lead:** Matthew

---

## ✅ Completed

### Phase 1: Data Acquisition & Foundation
- [x] Downloaded and integrated Fuzzwork's SDE SQLite database
- [x] Created Pure Blind systems spreadsheet with 85 systems
- [x] Identified 12 ice belt systems
- [x] Compiled power and workforce capacities for all systems
- [x] Moon counts added for all systems
- [x] Built NetworkX graph with all stargate connections
- [x] Created `phase1_quick_start.py` - working data acquisition script
- [x] Validated graph connectivity (all systems reachable)
- [x] Generated initial analysis:
  - Chokepoints (articulation points)
  - High-traffic systems (betweenness centrality)
  - Network center calculations
  - Constellation connectivity matrix

**Deliverables:**
- `pure_blind_systems.xlsx` - Complete data spreadsheet
- `phase1_quick_start.py` - Ready-to-run data loader
- `pure_blind_data/` directory with:
  - `systems.csv` - All system attributes
  - `gates_internal.csv` - Internal gate connections
  - `gates_border.csv` - Border gates
  - `pure_blind_graph.graphml` - NetworkX graph
  - `summary.json` - Network statistics

### Documentation
- [x] PROJECT_PLAN.md - Complete 4-phase roadmap
- [x] UI_ARCHITECTURE.md - Split-screen design specification
- [x] EXISTING_RESOURCES.md - Data source guide
- [x] GETTING_STARTED.md - Quick start instructions
- [x] README.md - Project overview
- [x] python_graph_primer.py - NetworkX tutorial (15 examples)
- [x] existing_data_guide.py - SDE query examples

### Design Decisions
- [x] Split-screen UI architecture finalized
- [x] Tool modes defined (5 primary tools)
- [x] Plotly Dash selected as framework
- [x] State management approach defined
- [x] Visualization types specified per tool

---

## 🚧 In Progress

### Phase 2: UI Framework
- [x] Basic Dash application structure (`dash_app_starter.py`)
- [x] Split-screen layout (30% left, 70% right)
- [x] Tool selector dropdown
- [ ] Dynamic control panel switching (partial)
- [ ] Graph visualization with proper layout
- [ ] State persistence between tool switches
- [ ] Callback optimization for performance

**Current Focus:**
- Refining the graph visualization to match Dotlan-like readability
- Implementing proper state management in Dash
- Testing control panel reactivity

**Blockers:**
- None currently

**Next Steps:**
1. Complete graph layout algorithm (2D projection from 3D coordinates)
2. Add constellation color-coding
3. Implement hover tooltips for systems
4. Test tool switching with sample data

---

## 📋 Todo - Phase 3: Tool Implementation

### Phase 3A: Ansiblex Bridge Builder (2 weeks)
- [ ] Bridge selection UI (From/To dropdowns)
- [ ] Distance validation (5 LY constraint)
- [ ] One-per-system constraint checking
- [ ] Bridge visualization on graph (blue lines)
- [ ] Distance recalculation after adding bridges
- [ ] Strategic system designation UI
- [ ] Metrics dashboard:
  - [ ] Average jumps to staging
  - [ ] Average jumps to industrial hubs
  - [ ] Average jumps to market hubs
  - [ ] Before/after comparison
- [ ] "Suggest Next Bridge" button (greedy algorithm)
- [ ] Bridge removal functionality
- [ ] Export bridge list (CSV, Discord format)

**Algorithm Implementation:**
- [ ] Weighted distance calculation
- [ ] Greedy optimization algorithm
- [ ] 3D distance calculation (light-years)

### Phase 3B: System Upgrade Planner (2 weeks)
- [ ] System selection dropdown
- [ ] System info display (constellation, security, moons, ice)
- [ ] Upgrade type dropdown (Mining, Ratting, Belt, etc.)
- [ ] Upgrade tier dropdown (Level 1-3)
- [ ] Add/Remove upgrade buttons
- [ ] Current upgrades list with checkboxes
- [ ] Capacity gauges (power and workforce)
- [ ] Real-time validation
- [ ] Warning messages for over-capacity
- [ ] Preset buttons:
  - [ ] Max Mining
  - [ ] Max Ratting (Subcap)
  - [ ] Balanced Economy
  - [ ] Strategic (PVP)
- [ ] Clear all upgrades button
- [ ] Export system configuration (JSON, text)

**Data Needed:**
- [ ] Complete upgrade database (power/workforce costs)
- [ ] Upgrade effects and descriptions
- [ ] Tier progression details

### Phase 3C: Mining System Optimizer (2 weeks)
- [ ] Industrial hub selection (multi-select)
- [ ] Number of mining systems slider/dropdown
- [ ] Priority checkboxes (ice, moons, clustering, true-sec)
- [ ] "Run Optimization" button
- [ ] Algorithm implementation:
  - [ ] Distance scoring
  - [ ] Ice belt bonus
  - [ ] Moon count bonus
  - [ ] Constellation clustering bonus
- [ ] Results list with scores
- [ ] Graph visualization with:
  - [ ] Industrial hubs highlighted (gold stars)
  - [ ] Recommended systems highlighted (green)
  - [ ] Distance rings
  - [ ] Score color gradient
- [ ] "Configure" button per system (jumps to Upgrade Planner)
- [ ] "Apply Mining to All" batch action
- [ ] Export mining system list

### Phase 3D: Ratting System Optimizer (1 week)
- [ ] Staging system selection
- [ ] Number of ratting systems dropdown
- [ ] Distribution strategy radio buttons:
  - [ ] Spread evenly
  - [ ] Cluster near staging
  - [ ] One per constellation
- [ ] Priority checkboxes (true-sec, distance, border avoidance)
- [ ] Algorithm implementation (spread/clustering logic)
- [ ] Graph visualization with:
  - [ ] Staging highlighted
  - [ ] Recommended systems highlighted
  - [ ] Coverage heatmap
- [ ] Export ratting system list

---

## 📋 Todo - Phase 4: Strategic Analysis (1-2 weeks)

- [ ] Analysis type dropdown
- [ ] Chokepoint detection visualization
- [ ] Betweenness centrality (traffic analysis)
- [ ] Closeness centrality (system importance)
- [ ] Constellation border analysis
- [ ] Distance heatmap from selected system
- [ ] Critical path highlighting
- [ ] Export analysis reports

---

## 📋 Todo - Phase 5: Polish & Advanced Features (2-3 weeks)

### Multi-System Configuration
- [ ] Constellation multi-select
- [ ] System type filters (ice, high moons, border)
- [ ] Batch preset application
- [ ] Capacity summary across selected systems
- [ ] Warning for systems exceeding capacity
- [ ] Export shopping list (ISK costs, materials)

### Export Functions
- [ ] CSV export for all tools
- [ ] JSON export for configurations
- [ ] Discord-friendly text format
- [ ] Markdown reports
- [ ] Image export of graphs

### Advanced Features
- [ ] Save/load configurations
- [ ] What-if scenario comparison (side-by-side)
- [ ] ESI API integration (live sovereignty data)
- [ ] Historical tracking (see changes over time)
- [ ] Alliance member permissions (view vs. edit)

### Visualization Enhancements
- [ ] 3D graph view (optional)
- [ ] Animation of route changes
- [ ] Zoom and pan controls
- [ ] System search/filter
- [ ] Constellation grouping toggle
- [ ] Legend customization

### Documentation
- [ ] User manual
- [ ] Video tutorials
- [ ] Algorithm explanations
- [ ] Troubleshooting guide
- [ ] API documentation (if exposing endpoints)

---

## 🐛 Known Issues

### High Priority
- None currently

### Medium Priority
- Graph layout needs improvement (systems overlapping)
- Dash callbacks need optimization (currently slow on large graphs)

### Low Priority
- Dark theme colors need refinement
- Mobile responsiveness not yet implemented

---

## 🎯 Upcoming Milestones

| Milestone | Target Date | Status |
|-----------|-------------|--------|
| Phase 1 Complete | ✅ Nov 20, 2025 | Done |
| Phase 2 Complete (UI Framework) | Dec 5, 2025 | In Progress |
| Phase 3A Complete (Ansiblex Builder) | Dec 20, 2025 | Not Started |
| Phase 3B Complete (Upgrade Planner) | Jan 5, 2026 | Not Started |
| Phase 3C Complete (Mining Optimizer) | Jan 20, 2026 | Not Started |
| Phase 3D Complete (Ratting Optimizer) | Jan 27, 2026 | Not Started |
| Phase 4 Complete (Strategic Analysis) | Feb 10, 2026 | Not Started |
| Phase 5 Complete (Polish) | Feb 28, 2026 | Not Started |
| **Production Ready** | **March 1, 2026** | **Target** |

---

## 📝 Notes

### Recent Decisions
- **Nov 25, 2025:** Revised UI architecture to split-screen design. Controls on left (30%), visualizations on right (70%). Different visualizations per tool mode.
- **Nov 25, 2025:** Confirmed Plotly Dash as primary framework. Can migrate to full web app later if needed.
- **Nov 24, 2025:** Data acquisition completed. All 85 systems loaded successfully from Fuzzwork SDE.

### Feedback Needed
- Alliance leadership: Priority order for tools (Ansiblex first vs. Upgrades first?)
- Alliance leadership: Strategic system designations (which systems are staging, industrial, market?)
- Finance: Budget constraints for upgrades (total ISK available)
- Members: Preferred export formats

### Questions to Resolve
- Should we include wormhole connections in the graph? (Not in initial version)
- Do we need multi-tenant support? (One instance per alliance or shared?)
- Authentication/authorization needed? (Start simple, add later if needed)

---

## 🤔 Lessons Learned

### What Went Well
- Fuzzwork's SDE integration was straightforward
- NetworkX is perfect for this use case
- Split-screen design clarifies the workflow
- Phase 1 script runs fast (<1 minute for all data)

### What Could Be Better
- Initial UI design was too complex (clicking on graph to configure)
- Should have researched Eve Online upgrade costs earlier
- Graph visualization needs more work than anticipated

### Risks & Mitigation
- **Risk:** Upgrade cost data might not be available
  - **Mitigation:** Crowdsource from alliance members, check Eve wikis
- **Risk:** Performance issues with large graphs in browser
  - **Mitigation:** Add graph simplification options, lazy loading
- **Risk:** Alliance leadership might want features we didn't plan
  - **Mitigation:** Modular design allows adding features incrementally

---

**Status Summary:** Project is ~30% complete. Foundation is solid, UI framework in progress, tool implementation is next.
