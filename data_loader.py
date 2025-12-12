#!/usr/bin/env python3
"""
Data loader with validation for Kevin's Outfit Finder.
Loads JSON data and validates using Pydantic models.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from pydantic import ValidationError

from config import DATA_FILES, PAGE_SEASONS_FILE
from models import ClothingItem, CollectionData


def load_json(file_path: Path) -> Dict:
    """Load JSON file with error handling."""
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_collection(collection: str, validate: bool = True) -> CollectionData:
    """
    Load and optionally validate a collection's data.

    Args:
        collection: Collection name ('summer', 'spring', or 'fw')
        validate: Whether to validate data against models

    Returns:
        CollectionData object with all collection data

    Raises:
        FileNotFoundError: If data files don't exist
        ValidationError: If validation fails (when validate=True)
    """
    files = DATA_FILES.get(collection)
    if not files:
        raise ValueError(f"Unknown collection: {collection}")

    # Load raw data
    clothing_index = {}
    page_items = {}
    category_stats = None

    if files.get("clothing_index") and files["clothing_index"].exists():
        clothing_index = load_json(files["clothing_index"])

    if files.get("page_items") and files["page_items"].exists():
        page_items = load_json(files["page_items"])

    if files.get("category_stats") and files["category_stats"].exists():
        category_stats = load_json(files["category_stats"])

    if validate:
        # Validate using Pydantic model
        return CollectionData(
            name=collection,
            clothing_index=clothing_index,
            page_items=page_items,
            category_stats=category_stats,
        )
    else:
        # Return without validation (for legacy code compatibility)
        return CollectionData.model_construct(
            name=collection,
            clothing_index=clothing_index,
            page_items=page_items,
            category_stats=category_stats,
        )


def load_collection_raw(collection: str) -> Tuple[Dict, Dict, Optional[Dict]]:
    """
    Load collection data as raw dictionaries (legacy interface).

    This maintains backward compatibility with existing code.

    Returns:
        Tuple of (clothing_index, page_items, category_stats)
    """
    data = load_collection(collection, validate=False)
    return data.clothing_index, dict(data.page_items), data.category_stats


def load_page_seasons() -> Dict[str, str]:
    """Load the page seasons mapping."""
    if PAGE_SEASONS_FILE.exists():
        return load_json(PAGE_SEASONS_FILE)
    return {}


def validate_collection(collection: str) -> List[str]:
    """
    Validate a collection and return list of issues found.

    Returns:
        List of issue descriptions (empty if valid)
    """
    issues = []

    try:
        data = load_collection(collection, validate=True)
    except FileNotFoundError as e:
        return [str(e)]
    except ValidationError as e:
        return [f"Validation error: {err['msg']}" for err in e.errors()]

    # Additional semantic validation
    index_items = set(data.clothing_index.keys())
    page_item_names = set()

    for page, items in data.page_items.items():
        for item in items:
            if isinstance(item, ClothingItem):
                page_item_names.add(item.name)

    # Check for items in index but not in page_items
    orphan_index = index_items - page_item_names
    if orphan_index and len(orphan_index) < 10:
        issues.append(f"Items in index but not in page_items: {orphan_index}")

    # Check for items in page_items but not in index
    orphan_pages = page_item_names - index_items
    if orphan_pages and len(orphan_pages) < 10:
        issues.append(f"Items in page_items but not in index: {orphan_pages}")

    return issues


def validate_all_collections() -> Dict[str, List[str]]:
    """Validate all collections and return issues by collection."""
    results = {}
    for collection in DATA_FILES.keys():
        issues = validate_collection(collection)
        if issues:
            results[collection] = issues
        else:
            results[collection] = ["OK"]
    return results


if __name__ == "__main__":
    # When run directly, validate all collections
    print("Validating all collections...\n")

    results = validate_all_collections()

    for collection, issues in results.items():
        status = "✅" if issues == ["OK"] else "⚠️"
        print(f"{status} {collection}:")
        for issue in issues:
            print(f"   {issue}")
        print()
