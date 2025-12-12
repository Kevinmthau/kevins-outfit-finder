#!/usr/bin/env python3
"""
Base migration class and utilities for data transformations.
"""

import json
import shutil
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set

from config import DATA_FILES, BASE_DIR


class Migration(ABC):
    """Base class for data migrations."""

    # Subclasses should set these
    name: str = "unnamed_migration"
    description: str = "No description"

    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.changes: List[str] = []
        self.backup_dir: Optional[Path] = None

    @abstractmethod
    def migrate(self) -> bool:
        """Execute the migration. Return True if successful."""
        pass

    def log(self, message: str) -> None:
        """Log a change."""
        self.changes.append(message)
        prefix = "[DRY RUN] " if self.dry_run else ""
        print(f"{prefix}{message}")

    def backup_file(self, file_path: Path) -> Path:
        """Create a backup of a file before modifying."""
        if self.backup_dir is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.backup_dir = BASE_DIR / "backups" / f"{self.name}_{timestamp}"
            self.backup_dir.mkdir(parents=True, exist_ok=True)

        backup_path = self.backup_dir / file_path.name
        if not self.dry_run:
            shutil.copy2(file_path, backup_path)
        return backup_path

    def load_json(self, file_path: Path) -> Dict:
        """Load a JSON file."""
        with open(file_path, 'r') as f:
            return json.load(f)

    def save_json(self, file_path: Path, data: Dict) -> None:
        """Save data to a JSON file (respects dry_run)."""
        if self.dry_run:
            self.log(f"Would save to {file_path}")
        else:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            self.log(f"Saved {file_path}")

    def run(self) -> bool:
        """Run the migration with proper setup/teardown."""
        mode = "DRY RUN" if self.dry_run else "LIVE"
        print(f"\n{'='*60}")
        print(f"Migration: {self.name} [{mode}]")
        print(f"Description: {self.description}")
        print(f"{'='*60}\n")

        success = self.migrate()

        print(f"\n{'='*60}")
        if success:
            if self.dry_run:
                print(f"DRY RUN complete. Run with --live to apply changes.")
            else:
                print(f"Migration completed successfully!")
                if self.backup_dir:
                    print(f"Backups saved to: {self.backup_dir}")
        else:
            print(f"Migration failed!")
        print(f"{'='*60}\n")

        return success


class MergeItemsMigration(Migration):
    """Migration that merges duplicate or variant item names."""

    # Subclasses set this: {"old_name": "new_name", ...}
    merge_map: Dict[str, str] = {}
    collection: str = "summer"  # "summer", "spring", or "fw"

    def migrate(self) -> bool:
        files = DATA_FILES.get(self.collection, {})
        if not files:
            self.log(f"Unknown collection: {self.collection}")
            return False

        index_path = files.get("clothing_index")
        page_items_path = files.get("page_items")

        if not index_path or not page_items_path:
            self.log(f"Missing data files for collection: {self.collection}")
            return False

        # Backup files
        self.backup_file(index_path)
        self.backup_file(page_items_path)

        # Load data
        index = self.load_json(index_path)
        page_items = self.load_json(page_items_path)

        # Merge items in index
        index = self._merge_index(index)

        # Update page_items
        page_items = self._update_page_items(page_items)

        # Save
        self.save_json(index_path, index)
        self.save_json(page_items_path, page_items)

        return True

    def _merge_index(self, index: Dict) -> Dict:
        """Merge items in the clothing index."""
        new_index = {}

        for item, pages in index.items():
            # Check if this item should be merged
            new_name = self.merge_map.get(item, item)

            if new_name != item:
                self.log(f"Merging '{item}' -> '{new_name}'")

            if new_name in new_index:
                # Merge pages
                existing = set(new_index[new_name])
                new_index[new_name] = sorted(existing | set(pages), key=self._page_sort_key)
            else:
                new_index[new_name] = pages

        return new_index

    def _update_page_items(self, page_items: Dict) -> Dict:
        """Update item names in page_items."""
        for page, items in page_items.items():
            for i, item_data in enumerate(items):
                if isinstance(item_data, dict) and 'name' in item_data:
                    old_name = item_data['name']
                    new_name = self.merge_map.get(old_name, old_name)
                    if new_name != old_name:
                        items[i]['name'] = new_name
                elif isinstance(item_data, str):
                    new_name = self.merge_map.get(item_data, item_data)
                    if new_name != item_data:
                        items[i] = new_name
        return page_items

    def _page_sort_key(self, page) -> int:
        """Sort key for pages - handles both string and int formats."""
        if isinstance(page, int):
            return page
        if isinstance(page, str) and page.startswith("page_"):
            return int(page.split("_")[1])
        return 0


class RenameItemMigration(MergeItemsMigration):
    """Convenience class for simple renames (same as merge with one mapping)."""

    old_name: str = ""
    new_name: str = ""

    def __init__(self, dry_run: bool = True):
        super().__init__(dry_run)
        if self.old_name and self.new_name:
            self.merge_map = {self.old_name: self.new_name}


class CleanOCRArtifactsMigration(Migration):
    """Migration to clean OCR artifacts from item names."""

    name = "clean_ocr_artifacts"
    description = "Remove common OCR artifacts from item names"
    collection: str = "summer"

    # Patterns to clean (prefix -> replacement)
    artifacts = [
        ("i ", ""),
        ("of ", ""),
        ("1 ", ""),
        ("| ", ""),
    ]

    def migrate(self) -> bool:
        files = DATA_FILES.get(self.collection, {})
        if not files:
            return False

        index_path = files.get("clothing_index")
        page_items_path = files.get("page_items")

        self.backup_file(index_path)
        self.backup_file(page_items_path)

        index = self.load_json(index_path)
        page_items = self.load_json(page_items_path)

        # Build merge map from artifacts
        merge_map = {}
        for item in list(index.keys()):
            cleaned = self._clean_item(item)
            if cleaned != item:
                merge_map[item] = cleaned
                self.log(f"Clean: '{item}' -> '{cleaned}'")

        # Apply merges
        self.merge_map = merge_map
        merger = MergeItemsMigration(self.dry_run)
        merger.merge_map = merge_map
        merger.collection = self.collection

        new_index = merger._merge_index(index)
        new_page_items = merger._update_page_items(page_items)

        self.save_json(index_path, new_index)
        self.save_json(page_items_path, new_page_items)

        return True

    def _clean_item(self, item: str) -> str:
        """Clean an item name of OCR artifacts."""
        cleaned = item
        for prefix, replacement in self.artifacts:
            if cleaned.lower().startswith(prefix):
                cleaned = replacement + cleaned[len(prefix):]
        return cleaned.strip()
