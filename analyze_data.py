#!/usr/bin/env python3
"""
Analyze clothing data to identify items that need cleaning.
"""

import json
from collections import defaultdict, Counter

def load_data():
    with open('clothing_index.json', 'r') as f:
        clothing_index = json.load(f)
    return clothing_index

def main():
    clothing_index = load_data()
    
    print("🔍 DATA ANALYSIS REPORT")
    print("=" * 50)
    
    # Basic stats
    print(f"📊 Total items: {len(clothing_index)}")
    print(f"📄 Total pages referenced: {len(set(page for pages in clothing_index.values() for page in pages))}")
    
    # Items that appear on only 1 page (might be OCR errors)
    single_page_items = [item for item, pages in clothing_index.items() if len(pages) == 1]
    print(f"\n⚠️  Items appearing on only 1 page: {len(single_page_items)}")
    for item in single_page_items[:10]:
        print(f"   - {item}")
    if len(single_page_items) > 10:
        print(f"   ... and {len(single_page_items) - 10} more")
    
    # Items with suspicious patterns (likely OCR errors)
    print(f"\n🚨 Items with suspicious patterns:")
    
    # Items that seem to combine multiple things
    combined_items = [item for item in clothing_index.keys() if 
                     any(word in item.lower() for word in [' trouser ', ' polo ', ' shirt ', ' blazer ']) and
                     len(item.split()) > 6]
    print(f"   Combined items ({len(combined_items)}):")
    for item in combined_items[:10]:
        print(f"     - {item}")
    
    # Items with "Beams khaki" (seems to be a trouser)
    beams_items = [item for item in clothing_index.keys() if 'beams khaki' in item.lower()]
    print(f"\n   Items with 'Beams khaki' ({len(beams_items)}) - likely should be trouser:")
    for item in beams_items:
        print(f"     - {item}")
    
    # Items with brand names repeated
    print(f"\n   Items with repeated brand names:")
    for item in clothing_index.keys():
        words = item.lower().split()
        if len(words) != len(set(words)):  # Has duplicates
            print(f"     - {item}")
    
    # Find potential duplicates
    print(f"\n🔄 POTENTIAL DUPLICATES:")
    
    # Group by base description
    base_groups = defaultdict(list)
    for item in clothing_index.keys():
        # Extract base item (first few words)
        words = item.split()
        if len(words) >= 3:
            base = ' '.join(words[:3])
            base_groups[base].append(item)
    
    for base, items in base_groups.items():
        if len(items) > 1:
            print(f"\n   {base}:")
            for item in items:
                pages_count = len(clothing_index[item])
                print(f"     - {item} ({pages_count} pages)")
    
    # Most common items
    print(f"\n🏆 TOP 15 MOST COMMON ITEMS:")
    sorted_items = sorted(clothing_index.items(), key=lambda x: len(x[1]), reverse=True)
    for i, (item, pages) in enumerate(sorted_items[:15], 1):
        print(f"   {i:2d}. {item}: {len(pages)} pages")
    
    # Brand analysis
    print(f"\n👔 BRAND ANALYSIS:")
    brand_counts = Counter()
    for item in clothing_index.keys():
        words = item.split()
        if words:
            # Common luxury brands
            brands = ['Saint Laurent', 'Boglioli', 'Lardini', 'The Row', 'Dries', 'Prada', 
                     'Zegna', 'Brioni', 'Valentino', 'Loro Piana', 'Iris Von Arnim']
            for brand in brands:
                if brand.lower() in item.lower():
                    brand_counts[brand] += 1
                    break
    
    for brand, count in brand_counts.most_common():
        print(f"   {brand}: {count} items")

if __name__ == "__main__":
    main()