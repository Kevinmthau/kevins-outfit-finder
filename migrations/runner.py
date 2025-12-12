#!/usr/bin/env python3
"""
Migration runner - execute data migrations.

Usage:
    python -m migrations.runner <migration_name> [--live]

Examples:
    python -m migrations.runner clean_ocr --dry-run
    python -m migrations.runner merge_loro_piana --live
"""

import sys
import argparse
from pathlib import Path

# Add parent dir to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from migrations.base import (
    Migration,
    MergeItemsMigration,
    RenameItemMigration,
    CleanOCRArtifactsMigration,
)


# =============================================================================
# Available Migrations
# =============================================================================

class MergeLoroPianaBlazersMigration(MergeItemsMigration):
    """Merge Loro Piana blazer variants."""
    name = "merge_loro_piana_blazers"
    description = "Merge 'Loro Piana blazer' and 'Loro Piana precious blazer' variants"
    collection = "fw"
    merge_map = {
        "Loro Piana blazer": "Loro Piana precious blazer",
    }


class MergeWoollyTrousersMigration(MergeItemsMigration):
    """Merge woolly trouser variants."""
    name = "merge_woolly_trousers"
    description = "Merge 'The Row woolly' variants into 'The Row woolly trouser'"
    collection = "fw"
    merge_map = {
        "The Row woolly": "The Row woolly trouser",
        "The Row woolly grey trouser": "The Row grey woolly trouser",
    }


class FixMislabeledBlazerMigration(RenameItemMigration):
    """Fix mislabeled blazer."""
    name = "fix_mislabeled_blazer"
    description = "Fix '1 Brioni brown corduroy' -> 'Brioni brown corduroy'"
    collection = "fw"
    old_name = "1 Brioni brown corduroy"
    new_name = "Brioni brown corduroy"


class UpdateCoatToTrenchMigration(RenameItemMigration):
    """Update coat to trench."""
    name = "update_coat_to_trench"
    description = "Update 'Saint Laurent coat' -> 'Saint Laurent trench coat'"
    collection = "fw"
    old_name = "Saint Laurent coat"
    new_name = "Saint Laurent trench coat"


class CleanFWArtifactsMigration(CleanOCRArtifactsMigration):
    """Clean OCR artifacts from Fall/Winter collection."""
    name = "clean_fw_ocr"
    description = "Clean OCR artifacts from Fall/Winter item names"
    collection = "fw"


class CleanSummerArtifactsMigration(CleanOCRArtifactsMigration):
    """Clean OCR artifacts from Summer collection."""
    name = "clean_summer_ocr"
    description = "Clean OCR artifacts from Summer item names"
    collection = "summer"


class CleanSpringArtifactsMigration(CleanOCRArtifactsMigration):
    """Clean OCR artifacts from Spring collection."""
    name = "clean_spring_ocr"
    description = "Clean OCR artifacts from Spring item names"
    collection = "spring"


# Registry of all migrations
MIGRATIONS = {
    "merge_loro_piana_blazers": MergeLoroPianaBlazersMigration,
    "merge_woolly_trousers": MergeWoollyTrousersMigration,
    "fix_mislabeled_blazer": FixMislabeledBlazerMigration,
    "update_coat_to_trench": UpdateCoatToTrenchMigration,
    "clean_fw_ocr": CleanFWArtifactsMigration,
    "clean_summer_ocr": CleanSummerArtifactsMigration,
    "clean_spring_ocr": CleanSpringArtifactsMigration,
}


def list_migrations():
    """Print available migrations."""
    print("\nAvailable migrations:")
    print("-" * 60)
    for name, cls in MIGRATIONS.items():
        print(f"  {name:30} - {cls.description}")
    print()


def run_migration(name: str, live: bool = False) -> bool:
    """Run a specific migration."""
    if name not in MIGRATIONS:
        print(f"Unknown migration: {name}")
        list_migrations()
        return False

    migration_cls = MIGRATIONS[name]
    migration = migration_cls(dry_run=not live)
    return migration.run()


def main():
    parser = argparse.ArgumentParser(description="Run data migrations")
    parser.add_argument("migration", nargs="?", help="Migration name to run")
    parser.add_argument("--live", action="store_true", help="Apply changes (default is dry-run)")
    parser.add_argument("--list", action="store_true", help="List available migrations")

    args = parser.parse_args()

    if args.list or not args.migration:
        list_migrations()
        return

    success = run_migration(args.migration, live=args.live)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
