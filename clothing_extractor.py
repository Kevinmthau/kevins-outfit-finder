#!/usr/bin/env python3
"""
Base clothing extractor class that consolidates OCR extraction logic.
Subclass this for collection-specific behavior.
"""

import os
import json
import re
from abc import ABC, abstractmethod
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PIL import Image
import pytesseract

from config import (
    TESSERACT_PATH,
    MAX_ITEM_LENGTH,
    MIN_ITEM_LENGTH,
    OCR_ARTIFACTS,
    ALL_BRANDS,
    SUMMER_BRANDS,
    SPRING_BRANDS,
    FW_BRANDS,
    SUMMER_CATEGORIES,
    SPRING_CATEGORIES,
    FW_CATEGORIES,
    COLLECTION_PATHS,
    DATA_FILES,
)
from models import ClothingItem, CategoryStats


# Set tesseract path
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


class ClothingExtractor(ABC):
    """
    Base class for extracting clothing items from outfit images using OCR.

    Subclass this and implement:
    - collection_name property
    - brands property
    - categories property
    """

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.clothing_index: Dict[str, List[str]] = defaultdict(list)
        self.page_items: Dict[str, List[ClothingItem]] = {}
        self.category_stats = CategoryStats()

    @property
    @abstractmethod
    def collection_name(self) -> str:
        """Return the collection name: 'summer', 'spring', or 'fw'."""
        pass

    @property
    @abstractmethod
    def brands(self) -> List[str]:
        """Return the list of brands to recognize for this collection."""
        pass

    @property
    @abstractmethod
    def categories(self) -> Dict[str, List[str]]:
        """Return the category definitions for this collection."""
        pass

    @property
    def images_dir(self) -> Path:
        """Return the image directory path for this collection."""
        return COLLECTION_PATHS[self.collection_name]

    @property
    def output_files(self) -> Dict[str, Path]:
        """Return the output file paths for this collection."""
        return DATA_FILES[self.collection_name]

    def extract_text_from_image(self, image_path: Path) -> str:
        """Extract text from image using OCR."""
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            if self.verbose:
                print(f"Error processing {image_path}: {e}")
            return ""

    def clean_text(self, text: str) -> str:
        """Clean OCR artifacts from text."""
        # Remove common OCR artifacts
        text = text.replace('_', '').replace('|', '').replace('"', '').replace('"', '').replace("'", "'")

        # Apply artifact patterns
        for pattern in OCR_ARTIFACTS:
            text = re.sub(pattern, '', text)

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)

        return text.strip()

    def is_brand_name(self, text: str) -> bool:
        """Check if text contains a brand name."""
        text_lower = text.lower()
        for brand in self.brands:
            if brand.lower() in text_lower:
                return True
        return False

    def has_clothing_keyword(self, text: str) -> bool:
        """Check if text contains any clothing-related keyword."""
        text_lower = text.lower()
        for keywords in self.categories.values():
            for keyword in keywords:
                if keyword in text_lower:
                    return True
        return False

    def categorize_item(self, item_text: str) -> str:
        """Categorize a clothing item based on keywords."""
        item_lower = item_text.lower()

        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in item_lower:
                    return category

        return 'Other'

    def split_combined_items(self, text: str) -> List[str]:
        """Split text that might contain multiple items."""
        items = []
        words = text.split()
        current_item: List[str] = []

        for i, word in enumerate(words):
            current_item.append(word)

            # Check if this word is a clothing type and the next word might be a brand
            if self.has_clothing_keyword(' '.join(current_item)):
                # Look ahead to see if next word starts a new brand
                if i + 1 < len(words) and self.is_brand_name(words[i + 1]):
                    # We found a complete item
                    items.append(' '.join(current_item).strip())
                    current_item = []

        # Add any remaining words as the last item
        if current_item:
            items.append(' '.join(current_item).strip())

        # If we didn't split anything, return the original text
        if len(items) <= 1:
            return [text]

        return items

    def parse_clothing_items(self, text: str) -> List[ClothingItem]:
        """Parse and categorize clothing items from extracted text."""
        lines = text.strip().split('\n')
        clothing_items: List[ClothingItem] = []
        current_item = ""

        for line in lines:
            line = self.clean_text(line)

            if not line or line.isdigit() or len(line) < MIN_ITEM_LENGTH:
                continue

            # Check if this line starts a new item (contains a brand name)
            if self.is_brand_name(line):
                # Save previous item if it exists
                if current_item and self.has_clothing_keyword(current_item):
                    self._add_parsed_items(current_item.strip(), clothing_items)
                current_item = line
            elif self.has_clothing_keyword(line):
                # This might be a continuation or standalone item
                if current_item and not self.has_clothing_keyword(current_item):
                    # Continuation of previous item (brand + item type)
                    current_item += " " + line
                else:
                    # Save previous and start new
                    if current_item and self.has_clothing_keyword(current_item):
                        self._add_parsed_items(current_item.strip(), clothing_items)
                    current_item = line
            else:
                # Might be a continuation (color, material, etc.)
                if current_item and len(current_item) < MAX_ITEM_LENGTH:
                    current_item += " " + line

        # Don't forget the last item
        if current_item and self.has_clothing_keyword(current_item):
            self._add_parsed_items(current_item.strip(), clothing_items)

        # Deduplicate
        return self._deduplicate_items(clothing_items)

    def _add_parsed_items(self, text: str, items_list: List[ClothingItem]) -> None:
        """Parse text and add items to the list."""
        split_items = self.split_combined_items(text)
        for split_item in split_items:
            if self.has_clothing_keyword(split_item) and len(split_item) > MIN_ITEM_LENGTH:
                item = ClothingItem(
                    name=split_item.strip(),
                    category=self.categorize_item(split_item)
                )
                items_list.append(item)

    def _deduplicate_items(self, items: List[ClothingItem]) -> List[ClothingItem]:
        """Remove duplicate items while preserving order."""
        seen = set()
        result = []
        for item in items:
            # Clean name
            item.name = ' '.join(item.name.split())

            # Create unique key
            item_key = (item.name.lower(), item.category)

            if item_key not in seen and len(item.name) > MIN_ITEM_LENGTH:
                seen.add(item_key)
                result.append(item)

        return result

    def process_all_images(self) -> None:
        """Process all images in the collection directory."""
        if not self.images_dir.exists():
            print(f"Directory {self.images_dir} not found!")
            return

        # Get all PNG files and sort them numerically
        png_files = sorted(
            [f for f in self.images_dir.iterdir() if f.suffix == '.png'],
            key=lambda x: int(re.findall(r'\d+', x.name)[0])
        )

        if self.verbose:
            print(f"Processing {len(png_files)} {self.collection_name} collection images...")
            print("=" * 60)

        for image_file in png_files:
            page_num = image_file.stem  # e.g., "page_1"

            if self.verbose:
                print(f"\nProcessing {image_file.name}...")

            # Extract text from image
            text = self.extract_text_from_image(image_file)

            # Parse and categorize clothing items
            items = self.parse_clothing_items(text)

            if items:
                self.page_items[page_num] = items

                # Add to clothing index and track categories
                for item in items:
                    item_key = f"{item.name} ({item.category})"
                    self.clothing_index[item_key].append(page_num)
                    self.category_stats.increment(item.category)

                if self.verbose:
                    print(f"  Found {len(items)} items")
            else:
                if self.verbose:
                    print(f"  No items found")

    def save_results(self) -> None:
        """Save extraction results to JSON files."""
        output = self.output_files

        # Save clothing index
        with open(output["clothing_index"], 'w') as f:
            json.dump(dict(self.clothing_index), f, indent=2)

        # Save page items (convert ClothingItem to dict)
        page_items_dict = {
            page: [item.model_dump() for item in items]
            for page, items in self.page_items.items()
        }
        with open(output["page_items"], 'w') as f:
            json.dump(page_items_dict, f, indent=2)

        # Save category stats if applicable
        if "category_stats" in output:
            with open(output["category_stats"], 'w') as f:
                json.dump(self.category_stats.stats, f, indent=2)

        if self.verbose:
            self._print_summary()

    def _print_summary(self) -> None:
        """Print extraction summary."""
        print(f"\n{'=' * 60}")
        print(f"Processing complete!")
        print(f"Total unique clothing items: {len(self.clothing_index)}")
        print(f"Pages processed: {len(self.page_items)}")

        # Print category statistics
        print("\nCategory breakdown:")
        for category, count in self.category_stats.get_sorted():
            print(f"  {category}: {count} items")

        # Print most common items
        print("\nMost common items:")
        sorted_items = sorted(
            self.clothing_index.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )
        for item, pages in sorted_items[:15]:
            print(f"  {item}: appears on {len(pages)} pages")

    def run(self) -> None:
        """Run the full extraction pipeline."""
        self.process_all_images()
        self.save_results()


class SummerExtractor(ClothingExtractor):
    """Extractor for Summer collection."""

    @property
    def collection_name(self) -> str:
        return "summer"

    @property
    def brands(self) -> List[str]:
        return SUMMER_BRANDS

    @property
    def categories(self) -> Dict[str, List[str]]:
        return SUMMER_CATEGORIES


class SpringExtractor(ClothingExtractor):
    """Extractor for Spring collection."""

    @property
    def collection_name(self) -> str:
        return "spring"

    @property
    def brands(self) -> List[str]:
        return SPRING_BRANDS

    @property
    def categories(self) -> Dict[str, List[str]]:
        return SPRING_CATEGORIES


class FallWinterExtractor(ClothingExtractor):
    """Extractor for Fall/Winter collection."""

    @property
    def collection_name(self) -> str:
        return "fw"

    @property
    def brands(self) -> List[str]:
        return FW_BRANDS

    @property
    def categories(self) -> Dict[str, List[str]]:
        return FW_CATEGORIES


def main():
    """Run extraction for a specified collection."""
    import argparse

    parser = argparse.ArgumentParser(description="Extract clothing items from outfit images")
    parser.add_argument(
        "collection",
        choices=["summer", "spring", "fw", "all"],
        help="Collection to process"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress verbose output"
    )

    args = parser.parse_args()

    extractors = {
        "summer": SummerExtractor,
        "spring": SpringExtractor,
        "fw": FallWinterExtractor,
    }

    if args.collection == "all":
        for name, extractor_class in extractors.items():
            print(f"\n{'#' * 60}")
            print(f"# Processing {name.upper()} collection")
            print(f"{'#' * 60}")
            extractor = extractor_class(verbose=not args.quiet)
            extractor.run()
    else:
        extractor = extractors[args.collection](verbose=not args.quiet)
        extractor.run()


if __name__ == "__main__":
    main()
