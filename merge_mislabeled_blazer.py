#!/usr/bin/env python3
"""
Script to merge mislabeled "Loro Piana brown blazer" into "The Row blazer" in Fall/Winter collection.
"""

import json

def merge_mislabeled_blazer():
    """Merge Loro Piana brown blazer into The Row blazer"""
    
    # Load Fall/Winter data
    with open('clothing_index_fw.json', 'r') as f:
        index = json.load(f)
    
    with open('page_items_fw.json', 'r') as f:
        page_items = json.load(f)
    
    # Get the page where Loro Piana brown blazer appears
    loro_pages = index.get("Loro Piana brown blazer (Outerwear)", [])
    print(f"Found 'Loro Piana brown blazer' on pages: {', '.join(loro_pages)}")
    
    # Add these pages to The Row blazer
    if "The Row blazer (Outerwear)" in index:
        existing_pages = index["The Row blazer (Outerwear)"]
        print(f"'The Row blazer' currently appears on {len(existing_pages)} pages")
        
        # Add the Loro Piana brown blazer pages to The Row blazer
        index["The Row blazer (Outerwear)"].extend(loro_pages)
        
        # Remove duplicates and sort
        index["The Row blazer (Outerwear)"] = sorted(
            list(set(index["The Row blazer (Outerwear)"])), 
            key=lambda x: int(x.split('_')[1])
        )
        
        print(f"Added page(s) {', '.join(loro_pages)} to 'The Row blazer'")
        new_total = len(index["The Row blazer (Outerwear)"])
        print(f"'The Row blazer' now appears on {new_total} pages total")
    else:
        print("Warning: 'The Row blazer (Outerwear)' not found in index")
        index["The Row blazer (Outerwear)"] = loro_pages
    
    # Remove Loro Piana brown blazer from index
    if "Loro Piana brown blazer (Outerwear)" in index:
        del index["Loro Piana brown blazer (Outerwear)"]
        print("Removed 'Loro Piana brown blazer' from index")
    
    # Update page_items - change Loro Piana brown blazer to The Row blazer
    updates_made = 0
    for page, items in page_items.items():
        updated_items = []
        for item in items:
            if isinstance(item, dict):
                if item['name'] == "Loro Piana brown blazer":
                    item['name'] = "The Row blazer"
                    print(f"  Updated page {page}: Loro Piana brown blazer -> The Row blazer")
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
    
    # Show the updated The Row blazer entry
    if "The Row blazer (Outerwear)" in index:
        pages = index["The Row blazer (Outerwear)"]
        print(f"\n'The Row blazer' now appears on {len(pages)} pages total:")
        print(f"Pages: {', '.join(pages)}")

def main():
    print("=" * 60)
    print("Merging mislabeled 'Loro Piana brown blazer' into 'The Row blazer'...")
    print("=" * 60)
    
    merge_mislabeled_blazer()

if __name__ == "__main__":
    main()