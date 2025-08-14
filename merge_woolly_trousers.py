#!/usr/bin/env python3
"""
Script to merge all Row woolly trouser variants into a single entry and recategorize as Bottoms.
"""

import json

def merge_woolly_trousers():
    """Merge all woolly trouser variants and recategorize as Bottoms"""
    
    # Load Fall/Winter data
    with open('clothing_index_fw.json', 'r') as f:
        index = json.load(f)
    
    with open('page_items_fw.json', 'r') as f:
        page_items = json.load(f)
    
    # All variants to merge
    variants_to_merge = [
        "The Row woolly trouser (Knitwear)",
        "The Row grey woolly trouser (Knitwear)",
        "The Row woolly grey trouser (Knitwear)"
    ]
    
    # Collect all pages from all variants
    all_pages = []
    for variant in variants_to_merge:
        if variant in index:
            pages = index[variant]
            all_pages.extend(pages)
            print(f"Found '{variant}' on pages: {', '.join(pages)}")
    
    # Remove duplicates and sort
    all_pages = sorted(list(set(all_pages)), key=lambda x: int(x.split('_')[1]))
    
    # Create new consolidated entry with Bottoms category
    new_key = "The Row woolly trouser (Bottoms)"
    
    # Create updated index
    updated_index = {}
    for item, pages in index.items():
        if item not in variants_to_merge:
            updated_index[item] = pages
    
    # Add the consolidated entry
    updated_index[new_key] = all_pages
    print(f"\nCreated consolidated entry: '{new_key}'")
    print(f"Appears on {len(all_pages)} pages total: {', '.join(all_pages)}")
    
    # Update page_items - normalize names and fix category
    page_updates = 0
    for page, items in page_items.items():
        updated_items = []
        for item in items:
            if isinstance(item, dict):
                item_name = item['name']
                category = item['category']
                
                # Check if this is one of the woolly trouser variants
                if any(x in item_name.lower() for x in ['woolly trouser', 'woolly grey']):
                    if 'row' in item_name.lower():
                        # Normalize the name and fix category
                        item['name'] = "The Row woolly trouser"
                        item['category'] = "Bottoms"
                        print(f"  Updated page {page}: '{item_name}' -> 'The Row woolly trouser' (Bottoms)")
                        page_updates += 1
                
                # Also check for standalone "The Row woolly"
                elif item_name == "The Row woolly":
                    item['name'] = "The Row woolly trouser"
                    item['category'] = "Bottoms"
                    print(f"  Updated page {page}: '{item_name}' -> 'The Row woolly trouser' (Bottoms)")
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
    
    print(f"\n✅ Merge complete!")
    print(f"Merged {len(variants_to_merge)} variants into one")
    print(f"Updated {page_updates} page item entries")
    print(f"Total unique items: {len(updated_index)}")
    
    # Show the consolidated entry
    print(f"\n'{new_key}' now appears on {len(all_pages)} pages total")

def main():
    print("=" * 60)
    print("Merging all Row woolly trouser variants and recategorizing as Bottoms...")
    print("=" * 60)
    
    merge_woolly_trousers()

if __name__ == "__main__":
    main()