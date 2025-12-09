#!/usr/bin/env python3
"""
Migrate Summer collection data from simple string format to categorized format.

Before: ["Saint Laurent ivory trouser", "The Row brown tassel loafer"]
After:  [{"name": "Saint Laurent ivory trouser", "category": "Bottoms"}, ...]
"""

import json
from pathlib import Path
from typing import Dict, List

from config import SUMMER_CATEGORIES, DATA_FILES


def categorize_summer_item(item_name: str) -> str:
    """Categorize a summer item based on keywords."""
    item_lower = item_name.lower()

    for category, keywords in SUMMER_CATEGORIES.items():
        for keyword in keywords:
            if keyword in item_lower:
                return category

    return "Other"


def migrate_page_items() -> None:
    """Migrate page_items.json to new format."""
    input_path = DATA_FILES["summer"]["page_items"]

    # Read existing data
    with open(input_path, 'r') as f:
        old_data: Dict[str, List[str]] = json.load(f)

    # Convert to new format
    new_data: Dict[str, List[Dict[str, str]]] = {}
    category_stats: Dict[str, int] = {}

    for page_id, items in old_data.items():
        new_items = []
        for item in items:
            if isinstance(item, str):
                category = categorize_summer_item(item)
                new_items.append({
                    "name": item,
                    "category": category
                })
                category_stats[category] = category_stats.get(category, 0) + 1
            elif isinstance(item, dict):
                # Already in new format
                new_items.append(item)
                category_stats[item.get("category", "Other")] = \
                    category_stats.get(item.get("category", "Other"), 0) + 1
        new_data[page_id] = new_items

    # Backup old file
    backup_path = input_path.with_suffix('.json.bak')
    with open(backup_path, 'w') as f:
        json.dump(old_data, f, indent=2)
    print(f"✅ Backed up old format to {backup_path}")

    # Write new format
    with open(input_path, 'w') as f:
        json.dump(new_data, f, indent=2)
    print(f"✅ Migrated page_items.json to categorized format")

    # Write category stats
    stats_path = DATA_FILES["summer"].get("category_stats")
    if not stats_path:
        stats_path = Path("category_stats_summer.json")
    with open(stats_path, 'w') as f:
        json.dump(category_stats, f, indent=2)
    print(f"✅ Created category stats at {stats_path}")

    # Print summary
    print("\nCategory breakdown:")
    for category, count in sorted(category_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  {category}: {count} items")


def migrate_clothing_index() -> None:
    """Migrate clothing_index.json to include category in keys."""
    input_path = DATA_FILES["summer"]["clothing_index"]

    # Read existing data
    with open(input_path, 'r') as f:
        old_data: Dict[str, List[str]] = json.load(f)

    # Convert to new format with category in key
    new_data: Dict[str, List[str]] = {}

    for item_name, pages in old_data.items():
        # Check if already has category suffix
        if '(' in item_name and ')' in item_name:
            new_data[item_name] = pages
        else:
            category = categorize_summer_item(item_name)
            new_key = f"{item_name} ({category})"
            new_data[new_key] = pages

    # Backup old file
    backup_path = input_path.with_suffix('.json.bak')
    with open(backup_path, 'w') as f:
        json.dump(old_data, f, indent=2)
    print(f"✅ Backed up old index to {backup_path}")

    # Write new format
    with open(input_path, 'w') as f:
        json.dump(new_data, f, indent=2)
    print(f"✅ Migrated clothing_index.json to categorized format")


def main():
    """Run migration."""
    print("🔄 Migrating Summer collection to categorized format...")
    print("=" * 60)

    migrate_page_items()
    print()
    migrate_clothing_index()

    print("\n" + "=" * 60)
    print("✅ Migration complete!")
    print("\nBackup files created with .bak extension.")
    print("Run the static site generator to see the changes.")


if __name__ == "__main__":
    main()
