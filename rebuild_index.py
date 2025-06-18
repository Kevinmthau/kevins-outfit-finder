#!/usr/bin/env python3
"""
Rebuild clothing_index.json from the manually updated page_items.json
"""

import json
from collections import defaultdict

def rebuild_clothing_index():
    """Rebuild the clothing index from page items"""
    
    # Load the updated page items
    with open('page_items.json', 'r') as f:
        page_items = json.load(f)
    
    # Build new clothing index
    clothing_index = defaultdict(list)
    
    for page, items in page_items.items():
        for item in items:
            clothing_index[item].append(page)
    
    # Sort pages for each item
    for item in clothing_index:
        clothing_index[item].sort(key=lambda x: int(x.split('_')[1]))
    
    # Convert to regular dict and sort by frequency
    clothing_index = dict(clothing_index)
    
    # Save the rebuilt index
    with open('clothing_index.json', 'w') as f:
        json.dump(clothing_index, f, indent=2)
    
    # Show statistics
    print("🔄 Rebuilt clothing index from page items!")
    print(f"📊 Found {len(clothing_index)} unique items across {len(page_items)} pages")
    
    # Show top items
    sorted_items = sorted(clothing_index.items(), key=lambda x: len(x[1]), reverse=True)
    print("\n🏆 Top 15 items by frequency:")
    for i, (item, pages) in enumerate(sorted_items[:15], 1):
        print(f"   {i:2d}. {item}: {len(pages)} pages")
    
    return clothing_index

if __name__ == "__main__":
    rebuild_clothing_index()