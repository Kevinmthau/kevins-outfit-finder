#!/usr/bin/env python3
"""
Pydantic models for data validation in Kevin's Outfit Finder.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class ClothingItem(BaseModel):
    """A single clothing item with name and category."""
    name: str = Field(..., min_length=1, description="The item name, e.g., 'Saint Laurent ivory trouser'")
    category: str = Field(default="Other", description="The category, e.g., 'Bottoms', 'Tops'")

    @field_validator("name")
    @classmethod
    def clean_name(cls, v: str) -> str:
        """Clean and normalize item names."""
        # Remove extra whitespace
        return " ".join(v.split())

    def __hash__(self) -> int:
        return hash((self.name.lower(), self.category))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ClothingItem):
            return False
        return self.name.lower() == other.name.lower() and self.category == other.category


class PageItems(BaseModel):
    """Items on a single page."""
    page_id: str = Field(..., description="Page identifier, e.g., 'page_1'")
    items: List[ClothingItem] = Field(default_factory=list)


class ClothingIndex(BaseModel):
    """Index mapping item names to pages where they appear."""
    # Pages can be strings ("page_1") or integers (1)
    items: Dict[str, List] = Field(default_factory=dict)

    def add_item(self, item_key: str, page_id: str) -> None:
        """Add a page reference for an item."""
        if item_key not in self.items:
            self.items[item_key] = []
        if page_id not in self.items[item_key]:
            self.items[item_key].append(page_id)

    def get_pages(self, item_key: str) -> List[str]:
        """Get all pages where an item appears."""
        return self.items.get(item_key, [])


class CollectionData(BaseModel):
    """Complete data for a clothing collection."""
    name: str = Field(..., description="Collection name: summer, spring, or fw")
    # clothing_index pages can be strings or integers
    clothing_index: Dict[str, List] = Field(default_factory=dict)
    page_items: Dict[str, List[ClothingItem]] = Field(default_factory=dict)
    category_stats: Optional[Dict[str, int]] = None

    @field_validator("page_items", mode="before")
    @classmethod
    def convert_page_items(cls, v: Dict) -> Dict[str, List[ClothingItem]]:
        """Convert raw page items to ClothingItem objects."""
        result = {}
        for page_id, items in v.items():
            converted_items = []
            for item in items:
                if isinstance(item, dict):
                    converted_items.append(ClothingItem(**item))
                elif isinstance(item, str):
                    # Legacy format: just a string name
                    converted_items.append(ClothingItem(name=item, category="Other"))
                elif isinstance(item, ClothingItem):
                    converted_items.append(item)
            result[page_id] = converted_items
        return result


class CategoryStats(BaseModel):
    """Statistics for clothing categories."""
    stats: Dict[str, int] = Field(default_factory=dict)

    def increment(self, category: str) -> None:
        """Increment count for a category."""
        self.stats[category] = self.stats.get(category, 0) + 1

    def get_sorted(self) -> List[tuple]:
        """Get categories sorted by count descending."""
        return sorted(self.stats.items(), key=lambda x: x[1], reverse=True)
