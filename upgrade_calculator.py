"""
Pure Blind Region Planner - Sovereignty Upgrade Calculator
==========================================================

This module provides:
1. Sovereignty upgrade database management
2. System upgrade configuration (which upgrades are installed where)
3. Capacity calculation (power/workforce usage)
4. Validation (capacity constraints)
5. Preset configurations (max mining, max ratting, etc.)

Usage:
    python upgrade_calculator.py                    # Run examples
    from upgrade_calculator import UpgradeCalculator # Use in other modules
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class UpgradeCalculator:
    """
    Handles sovereignty upgrade planning and capacity calculations
    """

    def __init__(self, data_dir: str = "data/pure_blind_data"):
        """
        Initialize the calculator with data directory

        Args:
            data_dir: Path to directory containing CSV files
        """
        self.data_dir = Path(data_dir)
        self.upgrades_df = None
        self.systems_df = None
        self.system_upgrades = {}  # {system_name: [upgrade_names]}

    def load_data(self) -> None:
        """Load sovereignty upgrades database and system data"""
        print("Loading sovereignty upgrades database...")
        self.upgrades_df = pd.read_csv(self.data_dir / "sovereignty_upgrades.csv")
        print(f"Loaded {len(self.upgrades_df)} upgrade types")

        print("Loading system capacity data...")
        self.systems_df = pd.read_csv(self.data_dir / "systems_capacity.csv")
        print(f"Loaded {len(self.systems_df)} systems")

    def load_system_upgrades(self, filename: str = "system_upgrades.json") -> None:
        """
        Load system upgrade configuration from JSON file

        Args:
            filename: Path to system upgrades JSON file
        """
        filepath = Path(filename)
        if filepath.exists():
            print(f"Loading system upgrade configuration from {filename}...")
            with open(filepath, 'r') as f:
                self.system_upgrades = json.load(f)
            print(f"✓ Loaded upgrades for {len(self.system_upgrades)} systems")
        else:
            print(f"No existing configuration found at {filename}, starting fresh")
            self.system_upgrades = {}

    def save_system_upgrades(self, filename: str = "system_upgrades.json") -> None:
        """
        Save system upgrade configuration to JSON file

        Args:
            filename: Output filename
        """
        with open(filename, 'w') as f:
            json.dump(self.system_upgrades, f, indent=2)
        print(f"✓ Saved system upgrades to {filename}")

    def get_upgrade_info(self, upgrade_name: str) -> Dict:
        """
        Get detailed information about an upgrade

        Args:
            upgrade_name: Name of the upgrade

        Returns:
            Dictionary with upgrade details (power, workforce, category, description)
        """
        upgrade = self.upgrades_df[self.upgrades_df['upgrade_name'] == upgrade_name]
        if upgrade.empty:
            raise ValueError(f"Upgrade '{upgrade_name}' not found in database")
        return upgrade.iloc[0].to_dict()

    def get_system_capacity(self, system_name: str) -> Tuple[int, int]:
        """
        Get base power and workforce capacity for a system

        Args:
            system_name: Name of the system

        Returns:
            Tuple of (power_capacity, workforce_capacity)
        """
        system = self.systems_df[self.systems_df['system_name'] == system_name]
        if system.empty:
            raise ValueError(f"System '{system_name}' not found in database")

        return (
            int(system.iloc[0]['power_capacity']),
            int(system.iloc[0]['workforce_capacity'])
        )

    def calculate_capacity_usage(self, system_name: str) -> Dict:
        """
        Calculate current capacity usage for a system

        This handles negative values correctly:
        - Negative power = adds to power capacity
        - Negative workforce = adds to workforce capacity

        Args:
            system_name: Name of the system

        Returns:
            Dictionary with:
            - base_power: Base power capacity
            - base_workforce: Base workforce capacity
            - power_added: Power added by capacity upgrades
            - workforce_added: Workforce added by capacity upgrades
            - power_used: Power consumed by other upgrades
            - workforce_used: Workforce consumed by other upgrades
            - power_available: Remaining power (base + added - used)
            - workforce_available: Remaining workforce (base + added - used)
            - upgrades: List of installed upgrades with details
        """
        # Get base capacity
        base_power, base_workforce = self.get_system_capacity(system_name)

        # Get installed upgrades
        installed = self.system_upgrades.get(system_name, [])

        power_added = 0
        workforce_added = 0
        power_used = 0
        workforce_used = 0
        upgrades_details = []

        for upgrade_name in installed:
            upgrade = self.get_upgrade_info(upgrade_name)

            # Handle power
            if upgrade['power'] < 0:
                power_added += abs(upgrade['power'])
            else:
                power_used += upgrade['power']

            # Handle workforce
            if upgrade['workforce'] < 0:
                workforce_added += abs(upgrade['workforce'])
            else:
                workforce_used += upgrade['workforce']

            upgrades_details.append({
                'name': upgrade_name,
                'power': upgrade['power'],
                'workforce': upgrade['workforce'],
                'category': upgrade['category']
            })

        return {
            'base_power': base_power,
            'base_workforce': base_workforce,
            'power_added': power_added,
            'workforce_added': workforce_added,
            'power_used': power_used,
            'workforce_used': workforce_used,
            'power_available': base_power + power_added - power_used,
            'workforce_available': base_workforce + workforce_added - workforce_used,
            'total_power_capacity': base_power + power_added,
            'total_workforce_capacity': base_workforce + workforce_added,
            'upgrades': upgrades_details
        }

    def can_add_upgrade(self, system_name: str, upgrade_name: str) -> Tuple[bool, str]:
        """
        Check if an upgrade can be added to a system

        Args:
            system_name: Name of the system
            upgrade_name: Name of the upgrade to add

        Returns:
            Tuple of (can_add: bool, reason: str)
        """
        upgrade = self.get_upgrade_info(upgrade_name)
        usage = self.calculate_capacity_usage(system_name)

        # Calculate what would happen if we add this upgrade
        power_cost = upgrade['power'] if upgrade['power'] > 0 else 0
        workforce_cost = upgrade['workforce'] if upgrade['workforce'] > 0 else 0

        power_remaining = usage['power_available'] - power_cost
        workforce_remaining = usage['workforce_available'] - workforce_cost

        # Check constraints
        if power_remaining < 0:
            return False, f"Insufficient power: need {power_cost}, only {usage['power_available']} available (deficit: {abs(power_remaining)})"

        if workforce_remaining < 0:
            return False, f"Insufficient workforce: need {workforce_cost}, only {usage['workforce_available']} available (deficit: {abs(workforce_remaining)})"

        # Check if already installed
        installed = self.system_upgrades.get(system_name, [])
        if upgrade_name in installed:
            return False, f"Upgrade '{upgrade_name}' is already installed"

        return True, f"Can add: {power_remaining} power and {workforce_remaining} workforce will remain"

    def add_upgrade(self, system_name: str, upgrade_name: str, force: bool = False) -> bool:
        """
        Add an upgrade to a system

        Args:
            system_name: Name of the system
            upgrade_name: Name of the upgrade to add
            force: If True, skip capacity validation (not recommended)

        Returns:
            True if added successfully, False otherwise
        """
        if not force:
            can_add, reason = self.can_add_upgrade(system_name, upgrade_name)
            if not can_add:
                print(f"❌ Cannot add '{upgrade_name}' to {system_name}: {reason}")
                return False

        # Initialize system if not exists
        if system_name not in self.system_upgrades:
            self.system_upgrades[system_name] = []

        self.system_upgrades[system_name].append(upgrade_name)
        print(f"✓ Added '{upgrade_name}' to {system_name}")
        return True

    def remove_upgrade(self, system_name: str, upgrade_name: str) -> bool:
        """
        Remove an upgrade from a system

        Args:
            system_name: Name of the system
            upgrade_name: Name of the upgrade to remove

        Returns:
            True if removed successfully, False otherwise
        """
        if system_name not in self.system_upgrades:
            print(f"❌ System {system_name} has no upgrades")
            return False

        if upgrade_name not in self.system_upgrades[system_name]:
            print(f"❌ Upgrade '{upgrade_name}' not found in {system_name}")
            return False

        self.system_upgrades[system_name].remove(upgrade_name)
        print(f"✓ Removed '{upgrade_name}' from {system_name}")
        return True

    def clear_system_upgrades(self, system_name: str) -> None:
        """
        Remove all upgrades from a system

        Args:
            system_name: Name of the system
        """
        self.system_upgrades[system_name] = []
        print(f"✓ Cleared all upgrades from {system_name}")

    def get_upgrades_by_category(self, category: str) -> pd.DataFrame:
        """
        Get all upgrades in a specific category

        Args:
            category: Category name (Mining, Ratting, Strategic, etc.)

        Returns:
            DataFrame with upgrades in that category
        """
        return self.upgrades_df[self.upgrades_df['category'] == category]

    def print_system_summary(self, system_name: str) -> None:
        """
        Print a detailed summary of a system's upgrades and capacity

        Args:
            system_name: Name of the system
        """
        usage = self.calculate_capacity_usage(system_name)

        print(f"\n{'='*70}")
        print(f"System: {system_name}")
        print(f"{'='*70}")

        # Base capacity
        print(f"\nBase Capacity:")
        print(f"  Power:     {usage['base_power']:,}")
        print(f"  Workforce: {usage['base_workforce']:,}")

        # Capacity modifications
        if usage['power_added'] > 0 or usage['workforce_added'] > 0:
            print(f"\nCapacity Additions:")
            if usage['power_added'] > 0:
                print(f"  Power:     +{usage['power_added']:,}")
            if usage['workforce_added'] > 0:
                print(f"  Workforce: +{usage['workforce_added']:,}")

        # Total capacity
        print(f"\nTotal Capacity:")
        print(f"  Power:     {usage['total_power_capacity']:,}")
        print(f"  Workforce: {usage['total_workforce_capacity']:,}")

        # Usage
        print(f"\nUsage:")
        print(f"  Power:     {usage['power_used']:,} / {usage['total_power_capacity']:,} ({usage['power_used']/usage['total_power_capacity']*100:.1f}% used)")
        print(f"  Workforce: {usage['workforce_used']:,} / {usage['total_workforce_capacity']:,} ({usage['workforce_used']/usage['total_workforce_capacity']*100:.1f}% used)")

        # Available
        print(f"\nAvailable:")
        print(f"  Power:     {usage['power_available']:,}")
        print(f"  Workforce: {usage['workforce_available']:,}")

        # Installed upgrades
        if usage['upgrades']:
            print(f"\nInstalled Upgrades ({len(usage['upgrades'])}):")
            for upgrade in usage['upgrades']:
                power_str = f"{upgrade['power']:+,}" if upgrade['power'] != 0 else "0"
                workforce_str = f"{upgrade['workforce']:+,}" if upgrade['workforce'] != 0 else "0"
                print(f"  [{upgrade['category']:12}] {upgrade['name']:30} | Power: {power_str:8} | Workforce: {workforce_str:8}")
        else:
            print(f"\nInstalled Upgrades: None")

        print(f"{'='*70}\n")

    def apply_preset(self, system_name: str, preset: str) -> List[str]:
        """
        Apply a preset configuration to a system

        Args:
            system_name: Name of the system
            preset: Preset name ('max_mining', 'max_ratting', 'balanced', 'empty')

        Returns:
            List of upgrades that were added
        """
        # Clear existing upgrades
        self.clear_system_upgrades(system_name)

        added = []

        if preset == 'max_mining':
            # Try to fit the largest mining upgrade possible
            for level in [3, 2, 1]:
                upgrade_name = f"Prospecting Array {level}"
                if self.add_upgrade(system_name, upgrade_name):
                    added.append(upgrade_name)
                    break

        elif preset == 'max_ratting':
            # Try to fit the largest ratting upgrades
            for level in [3, 2, 1]:
                major_upgrade = f"Major Threat {level}"
                if self.add_upgrade(system_name, major_upgrade):
                    added.append(major_upgrade)
                    break

            # Try to fit minor threat too
            for level in [3, 2, 1]:
                minor_upgrade = f"Minor Threat {level}"
                if self.add_upgrade(system_name, minor_upgrade):
                    added.append(minor_upgrade)
                    break

        elif preset == 'balanced':
            # Mix of mining and ratting
            if self.add_upgrade(system_name, "Prospecting Array 1"):
                added.append("Prospecting Array 1")
            if self.add_upgrade(system_name, "Major Threat 1"):
                added.append("Major Threat 1")

        elif preset == 'empty':
            # Already cleared above
            pass

        else:
            raise ValueError(f"Unknown preset: {preset}. Use 'max_mining', 'max_ratting', 'balanced', or 'empty'")

        print(f"✓ Applied preset '{preset}' to {system_name}: {len(added)} upgrades added")
        return added


def main():
    """
    Example usage of the UpgradeCalculator
    """
    print("="*70)
    print("Pure Blind Region Planner - Upgrade Calculator Examples")
    print("="*70)
    print()

    # Create calculator
    calc = UpgradeCalculator()

    # Load data
    calc.load_data()
    calc.load_system_upgrades("system_upgrades.json")

    print("\n" + "="*70)
    print("Example 1: View available upgrades by category")
    print("="*70)

    mining_upgrades = calc.get_upgrades_by_category('Mining')
    print("\nMining Upgrades:")
    print(mining_upgrades[['upgrade_name', 'power', 'workforce', 'description']].to_string(index=False))

    print("\n" + "="*70)
    print("Example 2: Check system capacity and installed upgrades")
    print("="*70)

    calc.print_system_summary('5ZXX-K')

    print("\n" + "="*70)
    print("Example 3: Try adding an upgrade")
    print("="*70)

    system = '5ZXX-K'
    upgrade = 'Major Threat 2'

    can_add, reason = calc.can_add_upgrade(system, upgrade)
    print(f"\nCan add '{upgrade}' to {system}?")
    print(f"  Result: {can_add}")
    print(f"  Reason: {reason}")

    if can_add:
        calc.add_upgrade(system, upgrade)
        calc.print_system_summary(system)

    print("\n" + "="*70)
    print("Example 4: Apply presets to a system")
    print("="*70)

    system = 'EC-P8R'
    calc.apply_preset(system, 'max_mining')
    calc.print_system_summary(system)

    # Save the configuration
    calc.save_system_upgrades("system_upgrades.json")

    print("\n" + "="*70)
    print("Example 5: Capacity-boosting upgrades (negative values)")
    print("="*70)

    system = 'X-7OMU'
    print(f"\nBefore adding Power Monitoring Division:")
    calc.print_system_summary(system)

    print(f"\nAdding Power Monitoring Division 3 (adds 1000 power)...")
    calc.add_upgrade(system, 'Power Monitoring Division 3')

    print(f"\nAfter adding capacity upgrade:")
    calc.print_system_summary(system)

    # Save the final configuration
    calc.save_system_upgrades("system_upgrades.json")

    print("\n" + "="*70)
    print("✓ Examples Complete!")
    print("="*70)


if __name__ == "__main__":
    main()
