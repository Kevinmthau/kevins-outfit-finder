#!/usr/bin/env python3
"""
Script to update "Loro Piana Coat" to "Loro Piana Navy coat" in Fall/Winter collection.
"""

import json

def update_loro_piana_coat():
    """Update Loro Piana Coat to Loro Piana Navy coat"""
    
    # Load Fall/Winter data
    with open('clothing_index_fw.json', 'r') as f:
        index = json.load(f)
    
    with open('page_items_fw.json', 'r') as f:
        page_items = json.load(f)
    
    # Update the index
    updated_index = {}
    updates_made = 0
    
    for item, pages in index.items():
        if item == "Loro Piana Coat (Outerwear)":
            # Change to Navy coat
            new_key = "Loro Piana Navy coat (Outerwear)"
            updated_index[new_key] = pages
            print(f"Updated index: '{item}' -> '{new_key}'")
            print(f"  Appears on pages: {', '.join(pages)}")
            updates_made += 1
        else:
            updated_index[item] = pages
    
    # Update page_items
    page_updates = 0
    for page, items in page_items.items():
        updated_items = []
        for item in items:
            if isinstance(item, dict):
                if item['name'] == "Loro Piana Coat":
                    item['name'] = "Loro Piana Navy coat"
                    print(f"  Updated page {page}: Loro Piana Coat -> Loro Piana Navy coat")
                    page_updates += 1
                updated_items.append(item)
            else:
                updated_items.append(item)
        page_items[page] = updated_items
    
    # Save updated data
    with open('clothing_index_fw.json', 'w') as f:
        json.dump(updated_index, f, indent=2)
    
    with open('page_items_fw.json', 'w') as f:
        json.dump(page_items, f, indent=2)
    
    print(f"\n✅ Update complete!")
    print(f"Updated {updates_made} index entries")
    print(f"Updated {page_updates} page item entries")
    print(f"Total unique items: {len(updated_index)}")

def main():
    print("=" * 60)
    print("Updating Loro Piana Coat to Loro Piana Navy coat...")
    print("=" * 60)
    
    update_loro_piana_coat()

if __name__ == "__main__":
    main()