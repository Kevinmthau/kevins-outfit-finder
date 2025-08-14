#!/usr/bin/env python3
"""
Script to clean and merge duplicate items in Fall/Winter collection.
Specifically targeting Loro Piana precious blazer variations.
"""

import json
import re

def clean_fw_data():
    """Clean Fall/Winter collection data"""
    
    # Load Fall/Winter data
    with open('clothing_index_fw.json', 'r') as f:
        index = json.load(f)
    
    with open('page_items_fw.json', 'r') as f:
        page_items = json.load(f)
    
    # Items to merge - variations to consolidate
    merge_mappings = {
        "Loro Piana brown precious blazer (Outerwear)": "Loro Piana precious blazer (Outerwear)",
        # Add any other duplicates we find
    }
    
    # Create cleaned index
    cleaned_index = {}
    merge_count = 0
    
    for item, pages in index.items():
        if item in merge_mappings:
            # This is a duplicate - merge with canonical
            canonical = merge_mappings[item]
            if canonical in cleaned_index:
                # Add pages to existing canonical entry
                cleaned_index[canonical].extend(pages)
                print(f"Merging '{item}' -> '{canonical}' ({len(pages)} pages)")
            else:
                # This shouldn't happen if canonical exists, but handle it
                cleaned_index[canonical] = pages
                print(f"Converting '{item}' -> '{canonical}'")
            merge_count += 1
        else:
            # Keep as is or add to existing
            if item in cleaned_index:
                # Already exists (shouldn't happen but just in case)
                cleaned_index[item].extend(pages)
            else:
                cleaned_index[item] = pages
    
    # Sort and deduplicate pages for merged items
    for item in cleaned_index:
        pages = list(set(cleaned_index[item]))
        cleaned_index[item] = sorted(pages, key=lambda x: int(x.split('_')[1]))
    
    # Clean page_items - update item names
    for page, items in page_items.items():
        cleaned_items = []
        for item in items:
            if isinstance(item, dict):
                item_name = item['name']
                category = item['category']
                
                # Clean the name
                if "brown precious blazer" in item_name.lower():
                    item_name = item_name.replace("brown precious blazer", "precious blazer")
                    item_name = item_name.replace("Brown precious blazer", "precious blazer")
                    print(f"  Page {page}: Updating item name to 'Loro Piana precious blazer'")
                
                cleaned_items.append({
                    'name': item_name.strip(),
                    'category': category
                })
            else:
                cleaned_items.append(item)
        
        page_items[page] = cleaned_items
    
    # Save cleaned data
    with open('clothing_index_fw.json', 'w') as f:
        json.dump(cleaned_index, f, indent=2)
    
    with open('page_items_fw.json', 'w') as f:
        json.dump(page_items, f, indent=2)
    
    print(f"\n✅ Cleaning complete!")
    print(f"Merged {merge_count} duplicate entries")
    print(f"Total unique items: {len(cleaned_index)}")
    
    # Show the consolidated Loro Piana precious blazer entry
    if "Loro Piana precious blazer (Outerwear)" in cleaned_index:
        pages = cleaned_index["Loro Piana precious blazer (Outerwear)"]
        print(f"\n'Loro Piana precious blazer' now appears on {len(pages)} pages total")
        print(f"Pages: {', '.join(pages[:10])}{'...' if len(pages) > 10 else ''}")

def main():
    print("=" * 60)
    print("Cleaning duplicates in Fall/Winter collection...")
    print("=" * 60)
    
    clean_fw_data()

if __name__ == "__main__":
    main()