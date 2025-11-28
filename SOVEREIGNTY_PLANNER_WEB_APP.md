# Sovereignty Upgrade Planner - Web Application

**Interactive Dash web application for planning sovereignty upgrades across Pure Blind**

## Quick Start

1. **Install dependencies** (if not already installed):
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**:
   ```bash
   python sovereignty_planner_app.py
   ```

3. **Open your browser**:
   - Navigate to: http://127.0.0.1:8050
   - The application will load automatically

4. **Stop the server**:
   - Press `Ctrl+C` in the terminal

## Features

### Split-Screen Interface

#### Left Panel (30%) - Control Panel
- **System Selector**: Choose which system to configure
- **System Info**: View constellation, security, moons, ice, and base capacity
- **Capacity Gauges**: Real-time visualization of power and workforce usage
  - Green zone: 0-70% (safe)
  - Yellow zone: 70-90% (caution)
  - Red zone: 90-100% (near capacity)
- **Preset Buttons**: Quick configuration options
  - **Max Mining**: Installs largest mining upgrade that fits
  - **Max Ratting**: Installs largest ratting upgrades that fit
  - **Balanced**: Mix of mining and ratting
  - **Clear All**: Remove all upgrades
- **Installed Upgrades**: List of current upgrades with remove buttons
- **Add Upgrade**: Dropdown to select and add individual upgrades
- **Save Configuration**: Persist changes to `system_upgrades.json`

#### Right Panel (70%) - Region Map
- Interactive graph visualization of all Pure Blind systems
- **Highlighted systems**:
  - **Selected system**: Currently being configured
  - **Systems with upgrades**: Any system that has upgrades installed
- Hover over systems to see details
- Zoom and pan to explore the region
- Constellation color-coding for easy navigation

### Capacity Management

The application provides **real-time validation**:
- ✅ **Green message**: Upgrade added successfully
- ❌ **Red message**: Insufficient capacity (shows deficit amount)
- Capacity gauges update instantly when upgrades are added/removed

### Preset Configurations

#### Max Mining
Installs the largest mining upgrade that fits:
1. Tries Prospecting Array 3 (1800 power, 18100 workforce)
2. Falls back to Array 2 if capacity insufficient
3. Falls back to Array 1 if still insufficient

#### Max Ratting
Installs the largest ratting upgrades:
1. Tries to fit Major Threat 3, falls back to 2, then 1
2. Also tries to fit Minor Threat 3, falls back to 2, then 1

#### Balanced
Installs a mix:
- Prospecting Array 1 (450 power, 6400 workforce)
- Major Threat 1 (400 power, 2700 workforce)

#### Clear All
Removes all upgrades from the selected system

## Workflow Examples

### Example 1: Configure a Single System

1. Select system from dropdown (e.g., "5ZXX-K")
2. View current capacity and installed upgrades
3. Click "Max Mining" preset button
4. Review the capacity gauges
5. Click "Save Configuration" to persist

### Example 2: Add Individual Upgrades

1. Select system
2. Click "Clear All" to start fresh
3. Select "Prospecting Array 2" from upgrade dropdown
4. Click "Add Upgrade"
5. Select "Minor Threat 1" from upgrade dropdown
6. Click "Add Upgrade"
7. Click "Save Configuration"

### Example 3: Remove Specific Upgrades

1. Select system with upgrades
2. Find the upgrade you want to remove in the "Installed Upgrades" list
3. Click the red "Remove" button next to it
4. Capacity gauges update automatically
5. Click "Save Configuration"

### Example 4: Configure Multiple Systems

1. Select first system (e.g., "5ZXX-K")
2. Apply preset or add upgrades
3. Click "Save Configuration"
4. Select next system from dropdown
5. Apply preset or add upgrades
6. Click "Save Configuration"
7. Repeat for all systems

### Example 5: Visual Planning

1. Look at the region map on the right
2. Notice highlighted systems have upgrades installed
3. Click on different systems to see their configurations
4. Use the map to ensure good distribution of mining/ratting systems across the region

## Understanding Capacity

### Base Capacity
All Pure Blind systems have:
- **Power**: 2,500
- **Workforce**: 18,000

### Capacity-Boosting Upgrades
Some upgrades **add** capacity instead of consuming it:
- **Power Monitoring Division 1**: Adds 200 power (costs 2,500 workforce)
- **Power Monitoring Division 2**: Adds 500 power (costs 10,000 workforce)
- **Power Monitoring Division 3**: Adds 1,000 power (costs 25,000 workforce)
- **Workforce Mecha-tooling 1**: Adds 5,000 workforce (costs 200 power)

### Validation Rules
The application enforces:
1. **Cannot exceed total capacity**: power_used ≤ base_power + added_power
2. **Cannot exceed workforce capacity**: workforce_used ≤ base_workforce + added_workforce
3. **Cannot install duplicate upgrades**: Each upgrade can only be installed once per system
4. **Real-time feedback**: Error messages show exactly how much capacity is needed

## Upgrade Categories

| Category | Description | Examples |
|----------|-------------|----------|
| **Mining** | Ore and ice mining bonuses | Prospecting Array 1-3 |
| **Ratting** | NPC spawn rate increases | Major Threat 1-3, Minor Threat 1-3 |
| **Exploration** | Signature strength bonuses | Exploration Detector 1-3 |
| **Strategic** | PVP and logistics support | Cynosural Navigation, Advanced Logistics |
| **Capacity** | Power/workforce boosts | Power Monitoring Division, Workforce Mecha-tooling |
| **Stability** | Resistance bonuses | Electric/Exotic/Gamma/Plasma Stability Generator |

## Data Persistence

### Automatic Saving
Configuration is **not** automatically saved. You must click "Save Configuration" to persist changes.

### Manual Editing
You can also manually edit `system_upgrades.json`:
```json
{
  "5ZXX-K": [
    "Prospecting Array 2",
    "Minor Threat 1"
  ],
  "X-7OMU": [
    "Major Threat 2"
  ]
}
```

After editing the file:
1. Stop the Dash application (Ctrl+C)
2. Restart it: `python sovereignty_planner_app.py`
3. Your changes will be loaded

## Keyboard Shortcuts

- **Ctrl+C**: Stop the server
- **Ctrl+F5** (in browser): Hard refresh the page
- **F5** (in browser): Refresh the page

## Troubleshooting

### Port Already in Use
If you see "Address already in use":
```bash
# Kill any process using port 8050
lsof -ti:8050 | xargs kill -9

# Or change the port in sovereignty_planner_app.py:
app.run(debug=True, host='127.0.0.1', port=8051)
```

### Changes Not Saving
Make sure you clicked "Save Configuration" button before closing the app.

### Gauges Not Updating
Try refreshing the page (F5) or selecting a different system and then back.

### Can't Add Upgrade
Check the error message:
- **Insufficient power**: Need to remove other upgrades or add Power Monitoring Division
- **Insufficient workforce**: Need to remove other upgrades or add Workforce Mecha-tooling
- **Already installed**: Cannot install the same upgrade twice

## Advanced Usage

### Batch Configuration via Python
For advanced users, you can script configurations:

```python
from upgrade_calculator import UpgradeCalculator

calc = UpgradeCalculator()
calc.load_data()
calc.load_system_upgrades()

# Configure all systems in a constellation
u7rbk_systems = ['2-6TGQ', '5ZXX-K', '8S-0E1', 'JE-D5U', 'OE-9UF', 'PFU-LH']
for system in u7rbk_systems:
    calc.apply_preset(system, 'max_ratting')

calc.save_system_upgrades()
```

Then reload the web app to see the changes.

## Technical Details

### Dependencies
- **dash**: Web framework
- **plotly**: Interactive visualizations
- **pandas**: Data manipulation
- **networkx**: Graph analysis

### File Structure
```
Eve_Region_Planner/
├── sovereignty_planner_app.py      # Main Dash application
├── upgrade_calculator.py           # Backend logic
├── graph_visualizer.py             # Map visualization
├── system_upgrades.json            # Your configurations
├── data/pure_blind_data/
│   └── sovereignty_upgrades.csv    # Upgrade database
└── positions_kamada_kawai.json     # Map layout
```

### Performance
- Initial load: ~2-3 seconds (loads all data)
- System selection: Instant
- Add/remove upgrade: Instant
- Map update: <1 second

## Next Steps

After configuring your sovereignty upgrades:

1. **Export for sharing**: Copy `system_upgrades.json` to share with alliance
2. **Review in-game**: Use the configuration to deploy actual IHUB upgrades
3. **Iterate**: Adjust based on alliance needs and feedback

## Support

- Check `PHASE3_SOVEREIGNTY_UPGRADES.md` for detailed documentation on the data structure
- Review `upgrade_calculator.py` examples for programmatic usage
- File issues or questions with your alliance leadership

---

**Version**: 1.0.0
**Phase**: 3A - Web Interface
**Status**: Production Ready ✅
