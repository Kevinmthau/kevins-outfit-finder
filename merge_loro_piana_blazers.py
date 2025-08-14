#!/usr/bin/env python3
"""
Script to merge "Loro Piana blazer" into "Loro Piana precious blazer" in Fall/Winter collection.
"""

import json

def merge_loro_piana_blazers():
    """Merge Loro Piana blazer into Loro Piana precious blazer"""
    
    # Load Fall/Winter data
    with open('clothing_index_fw.json', 'r') as f:
        index = json.load(f)
    
    with open('page_items_fw.json', 'r') as f:
        page_items = json.load(f)
    
    # Get the page where Loro Piana blazer appears
    loro_blazer_pages = index.get("Loro Piana blazer (Outerwear)", [])
    print(f"Found 'Loro Piana blazer' on pages: {', '.join(loro_blazer_pages)}")
    
    # Add these pages to Loro Piana precious blazer
    if "Loro Piana precious blazer (Outerwear)" in index:
        existing_pages = index["Loro Piana precious blazer (Outerwear)"]
        print(f"'Loro Piana precious blazer' currently appears on {len(existing_pages)} pages")
        
        # Add the Loro Piana blazer pages to Loro Piana precious blazer
        index["Loro Piana precious blazer (Outerwear)"].extend(loro_blazer_pages)
        
        # Remove duplicates and sort
        index["Loro Piana precious blazer (Outerwear)"] = sorted(
            list(set(index["Loro Piana precious blazer (Outerwear)"])), 
            key=lambda x: int(x.split('_')[1])
        )
        
        print(f"Added page(s) {', '.join(loro_blazer_pages)} to 'Loro Piana precious blazer'")
        new_total = len(index["Loro Piana precious blazer (Outerwear)"])
        print(f"'Loro Piana precious blazer' now appears on {new_total} pages total")
    else:
        print("Creating 'Loro Piana precious blazer (Outerwear)' entry")
        index["Loro Piana precious blazer (Outerwear)"] = loro_blazer_pages
    
    # Remove Loro Piana blazer from index
    if "Loro Piana blazer (Outerwear)" in index:
        del index["Loro Piana blazer (Outerwear)"]
        print("Removed 'Loro Piana blazer' from index")
    
    # Update page_items - change Loro Piana blazer to Loro Piana precious blazer
    updates_made = 0
    for page, items in page_items.items():
        updated_items = []
        for item in items:
            if isinstance(item, dict):
                if item['name'] == "Loro Piana blazer":
                    item['name'] = "Loro Piana precious blazer"
                    print(f"  Updated page {page}: Loro Piana blazer -> Loro Piana precious blazer")
                    updates_made += 1
                updated_items.append(item)
            else:
                updated_items.append(item)
        page_items[page] = updated_items
    
    # Save updated data
    with open('clothing_index_fw.json', 'w') as f:
        json.dump(index, f, indent=2)
    
    with open('page_items_fw.json', 'w') as f:
        json.dump(page_items, f, indent=2)
    
    print(f"\n✅ Merge complete!")
    print(f"Updated {updates_made} page item entries")
    print(f"Total unique items: {len(index)}")
    
    # Show the updated Loro Piana precious blazer entry
    if "Loro Piana precious blazer (Outerwear)" in index:
        pages = index["Loro Piana precious blazer (Outerwear)"]
        print(f"\n'Loro Piana precious blazer' now appears on {len(pages)} pages total:")
        print(f"Pages: {', '.join(pages)}")

def main():
    print("=" * 60)
    print("Merging 'Loro Piana blazer' into 'Loro Piana precious blazer'...")
    print("=" * 60)
    
    merge_loro_piana_blazers()

if __name__ == "__main__":
    main()