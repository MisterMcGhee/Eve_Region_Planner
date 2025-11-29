# Phase 3: Sovereignty Upgrade Planning Tool

**Status:** Foundation Complete ✅
**Date:** November 28, 2025

## Overview

Phase 3 implements the sovereignty upgrade planning system, allowing you to:
- Track which upgrades are installed in each system
- Calculate power and workforce usage
- Validate capacity constraints
- Apply preset configurations
- Handle capacity-boosting upgrades (negative costs)

## Data Structure Design

### 1. Sovereignty Upgrades Database (Static)

**File:** `data/pure_blind_data/sovereignty_upgrades.csv`

This CSV file defines ALL available sovereignty upgrades in Eve Online. It's similar to how `systems_full.csv` defines all systems.

**Structure:**
```csv
upgrade_name,power,workforce,category,description
Prospecting Array 1,450,6400,Mining,Ore mining bonus level 1
Power Monitoring Division 1,-200,2500,Capacity,Adds 200 power capacity
```

**Fields:**
- `upgrade_name`: Unique name of the upgrade
- `power`: Power requirement (negative = adds capacity)
- `workforce`: Workforce requirement (negative = adds capacity)
- `category`: Upgrade category (Mining, Ratting, Strategic, etc.)
- `description`: Human-readable description

**Handling Negative Values:**

Some upgrades ADD capacity instead of consuming it:
- **Power Monitoring Division 1**: -200 power = adds 200 to power capacity
- **Workforce Mecha-tooling 1**: -5000 workforce = adds 5000 to workforce capacity

The calculator handles this automatically:
- Negative power/workforce values increase total capacity
- Positive values consume capacity
- Both must fit within constraints

### 2. System Upgrades Configuration (User Data)

**File:** `system_upgrades.json`

This JSON file tracks which upgrades are installed in which systems - similar to how `positions_kamada_kawai.json` tracks node positions.

**Structure:**
```json
{
  "5ZXX-K": [
    "Prospecting Array 2",
    "Minor Threat 1"
  ],
  "X-7OMU": [
    "Major Threat 2",
    "Exploration Detector 1"
  ],
  "EC-P8R": []
}
```

**Design Rationale:**

✅ **Why separate files?**
- **Upgrades database** = game data (changes when CCP updates the game)
- **System configurations** = user data (changes when you plan your sovereignty)
- Separation allows easy updates without losing your configurations

✅ **Why JSON for configurations?**
- Human-readable and easy to edit manually
- Same pattern as `positions_kamada_kawai.json` (consistency)
- Easy to save/load/share configurations
- Version control friendly (git diff works well)

✅ **Why CSV for upgrades database?**
- Easy to edit in Excel/Google Sheets
- Simple to update when game mechanics change
- Familiar format for game data

## Upgrade Calculator Module

**File:** `upgrade_calculator.py`

### Key Features

1. **Load Data**
   ```python
   from upgrade_calculator import UpgradeCalculator

   calc = UpgradeCalculator()
   calc.load_data()  # Loads upgrades database and system capacity data
   calc.load_system_upgrades("system_upgrades.json")
   ```

2. **Check System Capacity**
   ```python
   usage = calc.calculate_capacity_usage('5ZXX-K')
   print(f"Power: {usage['power_used']} / {usage['total_power_capacity']}")
   print(f"Workforce: {usage['workforce_used']} / {usage['total_workforce_capacity']}")
   ```

3. **Validate Before Adding**
   ```python
   can_add, reason = calc.can_add_upgrade('5ZXX-K', 'Major Threat 3')
   if can_add:
       calc.add_upgrade('5ZXX-K', 'Major Threat 3')
   else:
       print(f"Cannot add: {reason}")
   ```

4. **Apply Presets**
   ```python
   calc.apply_preset('EC-P8R', 'max_mining')  # Fits largest mining upgrade
   calc.apply_preset('X-7OMU', 'max_ratting')  # Fits largest ratting upgrades
   calc.apply_preset('5ZXX-K', 'balanced')  # Mix of mining and ratting
   calc.apply_preset('UI-8ZE', 'empty')  # Clear all upgrades
   ```

5. **Print Summary**
   ```python
   calc.print_system_summary('5ZXX-K')
   ```

   Output:
   ```
   ======================================================================
   System: 5ZXX-K
   ======================================================================

   Base Capacity:
     Power:     2,500
     Workforce: 18,000

   Total Capacity:
     Power:     2,500
     Workforce: 18,000

   Usage:
     Power:     1,420 / 2,500 (56.8% used)
     Workforce: 14,500 / 18,000 (80.6% used)

   Available:
     Power:     1,080
     Workforce: 3,500

   Installed Upgrades (2):
     [Mining      ] Prospecting Array 2            | Power: +1,220   | Workforce: +12,700
     [Ratting     ] Minor Threat 1                 | Power: +200     | Workforce: +1,800
   ======================================================================
   ```

6. **Save Configuration**
   ```python
   calc.save_system_upgrades("system_upgrades.json")
   ```

### Capacity Calculation Logic

The calculator properly handles capacity additions (negative values):

```python
# For a system with base capacity 2500 power, 18000 workforce
# If you install:
#   - Power Monitoring Division 3 (power: -1000, workforce: 25000)
#   - Prospecting Array 2 (power: 1220, workforce: 12700)

# Calculation:
base_power = 2500
base_workforce = 18000

# Power Monitoring Division 3
power_added = 1000  # (negative -1000 becomes +1000 capacity)
workforce_used = 25000  # (positive cost)

# Prospecting Array 2
power_used = 1220
workforce_used += 12700

# Totals
total_power_capacity = 2500 + 1000 = 3500
total_workforce_capacity = 18000 + 0 = 18000
power_available = 3500 - 1220 = 2280
workforce_available = 18000 - 37700 = -19700  # EXCEEDS CAPACITY!
```

The calculator validates this and prevents invalid configurations.

## Available Upgrade Categories

From `sovereignty_upgrades.csv`:

| Category | Description | Example Upgrades |
|----------|-------------|------------------|
| **Mining** | Ore and ice mining bonuses | Prospecting Array 1-3 |
| **Ratting** | NPC spawn rate increases | Major Threat 1-3, Minor Threat 1-3 |
| **Exploration** | Signature strength bonuses | Exploration Detector 1-3 |
| **Strategic** | PVP and logistics support | Cynosural Navigation, Advanced Logistics |
| **Capacity** | Power/workforce capacity boosts | Power Monitoring Division 1-3, Workforce Mecha-tooling 1-3 |
| **Stability** | Resistance bonuses | Electric/Exotic/Gamma/Plasma Stability Generator |
| **None** | Empty slot | Empty |

## Preset Configurations

### Max Mining
Installs the largest mining upgrade that fits:
- Tries Prospecting Array 3 (1800 power, 18100 workforce)
- Falls back to Array 2 if capacity insufficient
- Falls back to Array 1 if Array 2 doesn't fit

### Max Ratting
Installs the largest ratting upgrades that fit:
- Tries Major Threat 3, falls back to 2, then 1
- Also tries to fit Minor Threat 3, falls back to 2, then 1

### Balanced
Mix of mining and ratting:
- Prospecting Array 1 (450 power, 6400 workforce)
- Major Threat 1 (400 power, 2700 workforce)

### Empty
Clears all upgrades from the system

## Usage Examples

### Example 1: Configure a Single System

```python
from upgrade_calculator import UpgradeCalculator

calc = UpgradeCalculator()
calc.load_data()
calc.load_system_upgrades()

# Configure 5ZXX-K as a mining system
calc.clear_system_upgrades('5ZXX-K')
calc.add_upgrade('5ZXX-K', 'Prospecting Array 3')
calc.add_upgrade('5ZXX-K', 'Minor Threat 1')

# Save configuration
calc.save_system_upgrades()
```

### Example 2: Batch Configure a Constellation

```python
# Configure all systems in U-7RBK constellation as ratting systems
u7rbk_systems = ['2-6TGQ', '5ZXX-K', '8S-0E1', 'JE-D5U', 'OE-9UF', 'PFU-LH']

for system in u7rbk_systems:
    calc.apply_preset(system, 'max_ratting')

calc.save_system_upgrades()
```

### Example 3: Find Systems That Can Fit an Upgrade

```python
# Find all systems that can fit Prospecting Array 3
upgrade_name = 'Prospecting Array 3'

compatible_systems = []
for system in calc.systems_df['system_name']:
    can_add, reason = calc.can_add_upgrade(system, upgrade_name)
    if can_add:
        compatible_systems.append(system)

print(f"Systems that can fit {upgrade_name}: {len(compatible_systems)}")
print(compatible_systems)
```

### Example 4: Calculate Region-Wide Upgrade Costs

```python
# Calculate total upgrades across all systems
total_power_used = 0
total_workforce_used = 0
systems_configured = 0

for system in calc.system_upgrades.keys():
    usage = calc.calculate_capacity_usage(system)
    total_power_used += usage['power_used']
    total_workforce_used += usage['workforce_used']
    if usage['upgrades']:
        systems_configured += 1

print(f"Region-wide totals:")
print(f"  Systems configured: {systems_configured}")
print(f"  Total power used: {total_power_used:,}")
print(f"  Total workforce used: {total_workforce_used:,}")
```

## Integration with GraphVisualizer

The upgrade calculator can be integrated with the graph visualizer from Phase 2:

```python
from graph_visualizer import GraphVisualizer
from upgrade_calculator import UpgradeCalculator

# Load both modules
viz = GraphVisualizer()
viz.load_data()
viz.build_graph()
viz.calculate_layout()

calc = UpgradeCalculator()
calc.load_data()
calc.load_system_upgrades()

# Highlight systems with mining upgrades
mining_systems = []
for system, upgrades in calc.system_upgrades.items():
    for upgrade in upgrades:
        if 'Prospecting' in upgrade:
            mining_systems.append(system)
            break

# Create visualization with mining systems highlighted
fig = viz.create_plotly_figure(
    highlight_systems=mining_systems,
    title="Pure Blind - Mining Systems"
)
fig.show()
```

## Next Steps

### Phase 3A: Dash Web Interface
Create an interactive web dashboard using Plotly Dash:
- Left panel (30%): System selector and upgrade controls
- Right panel (70%): Graph visualization with system highlighting
- Real-time capacity gauges
- Preset buttons
- Export configuration

### Phase 3B: Advanced Algorithms
Implement optimization algorithms:
- **Mining System Optimizer**: Find best N systems for mining based on proximity to industrial hubs
- **Ratting System Optimizer**: Spread ratting systems across the region for maximum coverage
- **Capacity Optimizer**: Maximize upgrade value within capacity constraints

### Phase 3C: Multi-System Configuration
Batch operations:
- Configure entire constellations
- Filter systems by attributes (ice belts, moon counts, security)
- Copy configurations between systems
- Export shopping lists (ISK costs, materials needed)

## File Summary

| File | Type | Purpose | Size |
|------|------|---------|------|
| `data/pure_blind_data/sovereignty_upgrades.csv` | Database | All available upgrades | 25 upgrades |
| `system_upgrades.json` | Configuration | Installed upgrades per system | User-editable |
| `upgrade_calculator.py` | Code | Upgrade planning logic | ~15 KB |
| `PHASE3_SOVEREIGNTY_UPGRADES.md` | Documentation | This file | You're reading it |

## Testing

Run the example script to test all features:

```bash
python upgrade_calculator.py
```

This will:
1. Load the upgrades database
2. Load system configurations
3. Show available upgrades by category
4. Calculate capacity usage for example systems
5. Test adding/removing upgrades
6. Test preset configurations
7. Test capacity-boosting upgrades
8. Save the configuration

## Validation

✅ **Data Loading:** Successfully loads 25 upgrade types and 86 systems
✅ **Capacity Calculation:** Correctly handles positive and negative values
✅ **Validation:** Prevents invalid configurations that exceed capacity
✅ **Presets:** Max mining, max ratting, balanced, and empty presets work correctly
✅ **Persistence:** Saves and loads configurations from JSON
✅ **Integration Ready:** Can be imported and used by other modules

## Questions & Answers

**Q: Should upgrades be stored in a list like positions_kamada_kawai.json?**
**A:** Yes! The `system_upgrades.json` file uses the same pattern:
- System names as keys
- List of upgrade names as values
- Easy to edit manually
- Version control friendly

**Q: How are negative values handled?**
**A:** Negative power/workforce values represent capacity ADDITIONS:
- Negative power = adds to power capacity
- Negative workforce = adds to workforce capacity
- The calculator separates "added" from "used" capacity
- Total capacity = base + added
- Available capacity = total - used

**Q: Can I edit the CSV file?**
**A:** Yes! The `sovereignty_upgrades.csv` file is designed to be edited:
- Open in Excel, Google Sheets, or text editor
- Add/remove/modify upgrades
- Update power/workforce costs if game mechanics change
- Changes take effect on next load

**Q: What if I want different presets?**
**A:** You can add custom presets by modifying the `apply_preset()` method in `upgrade_calculator.py`, or create your own preset functions that call `add_upgrade()` multiple times.

---

**Status:** Phase 3 foundation is complete and ready for web interface development!
