#!/usr/bin/env python3
"""
Image optimization script for Kevin's Outfit Finder.
Converts images to WebP format for smaller file sizes.
"""

import argparse
import shutil
from pathlib import Path
from typing import Optional

from PIL import Image

from config import COLLECTION_PATHS, DIST_DIR, DIST_IMAGE_FOLDERS


def convert_to_webp(
    input_path: Path,
    output_path: Path,
    quality: int = 85,
    keep_original: bool = True
) -> Optional[int]:
    """
    Convert an image to WebP format.

    Args:
        input_path: Path to source image
        output_path: Path for WebP output
        quality: WebP quality (0-100)
        keep_original: Whether to also copy the original PNG

    Returns:
        Bytes saved, or None if conversion failed
    """
    try:
        with Image.open(input_path) as img:
            # Convert to RGB if necessary (WebP doesn't support all modes)
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGBA')
            elif img.mode != 'RGB':
                img = img.convert('RGB')

            # Save as WebP
            webp_path = output_path.with_suffix('.webp')
            img.save(webp_path, 'WEBP', quality=quality, method=6)

            # Calculate savings
            original_size = input_path.stat().st_size
            webp_size = webp_path.stat().st_size
            savings = original_size - webp_size

            # Optionally copy original for fallback
            if keep_original:
                shutil.copy2(input_path, output_path)

            return savings

    except Exception as e:
        print(f"Error converting {input_path}: {e}")
        return None


def optimize_collection(
    collection: str,
    quality: int = 85,
    keep_original: bool = True,
    verbose: bool = True
) -> dict:
    """
    Optimize all images in a collection.

    Args:
        collection: Collection name ('summer', 'spring', 'fw')
        quality: WebP quality (0-100)
        keep_original: Keep PNG files as fallback
        verbose: Print progress

    Returns:
        Statistics dict with counts and sizes
    """
    source_dir = COLLECTION_PATHS[collection]
    output_folder = DIST_IMAGE_FOLDERS[collection]
    output_dir = DIST_DIR / output_folder

    if not source_dir.exists():
        print(f"Source directory not found: {source_dir}")
        return {}

    output_dir.mkdir(parents=True, exist_ok=True)

    stats = {
        "total_files": 0,
        "converted": 0,
        "failed": 0,
        "original_size": 0,
        "webp_size": 0,
        "savings": 0,
    }

    png_files = list(source_dir.glob("*.png"))
    stats["total_files"] = len(png_files)

    if verbose:
        print(f"Processing {len(png_files)} images from {collection} collection...")

    for i, png_file in enumerate(png_files, 1):
        output_path = output_dir / png_file.name
        original_size = png_file.stat().st_size
        stats["original_size"] += original_size

        savings = convert_to_webp(png_file, output_path, quality, keep_original)

        if savings is not None:
            stats["converted"] += 1
            stats["savings"] += savings
            webp_path = output_path.with_suffix('.webp')
            stats["webp_size"] += webp_path.stat().st_size

            if verbose and i % 10 == 0:
                print(f"  Processed {i}/{len(png_files)} images...")
        else:
            stats["failed"] += 1
            # Copy original as fallback
            shutil.copy2(png_file, output_path)

    return stats


def format_size(size_bytes: int) -> str:
    """Format bytes as human-readable size."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def main():
    """Run image optimization."""
    parser = argparse.ArgumentParser(
        description="Optimize images for Kevin's Outfit Finder"
    )
    parser.add_argument(
        "collection",
        choices=["summer", "spring", "fw", "all"],
        help="Collection to optimize"
    )
    parser.add_argument(
        "--quality", "-q",
        type=int,
        default=85,
        help="WebP quality (0-100, default: 85)"
    )
    parser.add_argument(
        "--no-fallback",
        action="store_true",
        help="Don't keep original PNG files"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress output"
    )

    args = parser.parse_args()

    # Ensure dist directory exists
    DIST_DIR.mkdir(exist_ok=True)

    collections = ["summer", "spring", "fw"] if args.collection == "all" else [args.collection]
    total_stats = {
        "original_size": 0,
        "webp_size": 0,
        "savings": 0,
        "converted": 0,
    }

    for collection in collections:
        print(f"\n{'=' * 60}")
        print(f"Optimizing {collection.upper()} collection")
        print("=" * 60)

        stats = optimize_collection(
            collection,
            quality=args.quality,
            keep_original=not args.no_fallback,
            verbose=not args.quiet
        )

        if stats:
            total_stats["original_size"] += stats["original_size"]
            total_stats["webp_size"] += stats["webp_size"]
            total_stats["savings"] += stats["savings"]
            total_stats["converted"] += stats["converted"]

            print(f"\n{collection.upper()} Results:")
            print(f"  Files processed: {stats['converted']}/{stats['total_files']}")
            print(f"  Original size: {format_size(stats['original_size'])}")
            print(f"  WebP size: {format_size(stats['webp_size'])}")
            print(f"  Savings: {format_size(stats['savings'])} ({stats['savings'] * 100 / stats['original_size']:.1f}%)")

    if len(collections) > 1:
        print(f"\n{'=' * 60}")
        print("TOTAL RESULTS")
        print("=" * 60)
        print(f"  Total files: {total_stats['converted']}")
        print(f"  Original size: {format_size(total_stats['original_size'])}")
        print(f"  WebP size: {format_size(total_stats['webp_size'])}")
        if total_stats["original_size"] > 0:
            percent = total_stats['savings'] * 100 / total_stats['original_size']
            print(f"  Total savings: {format_size(total_stats['savings'])} ({percent:.1f}%)")


if __name__ == "__main__":
    main()
