#!/usr/bin/env python3
"""
Direct data cleaning script - edit this file to clean your clothing data.
Run this script after making your edits to apply the changes.
"""

import json
from collections import defaultdict

def load_data():
    """Load current data"""
    with open('clothing_index.json', 'r') as f:
        clothing_index = json.load(f)
    with open('page_items.json', 'r') as f:
        page_items = json.load(f)
    return clothing_index, page_items

def save_data(clothing_index, page_items):
    """Save cleaned data"""
    with open('clothing_index.json', 'w') as f:
        json.dump(clothing_index, f, indent=2)
    with open('page_items.json', 'w') as f:
        json.dump(page_items, f, indent=2)

def rename_item(clothing_index, page_items, old_name, new_name):
    """Rename an item throughout the dataset"""
    if old_name in clothing_index:
        # Update clothing index
        clothing_index[new_name] = clothing_index.pop(old_name)
        
        # Update page items
        for page, items in page_items.items():
            for i, item in enumerate(items):
                if item == old_name:
                    items[i] = new_name
        
        print(f"✅ Renamed: '{old_name}' → '{new_name}'")
    else:
        print(f"❌ Item not found: '{old_name}'")

def merge_items(clothing_index, page_items, items_to_merge, new_name):
    """Merge multiple items into one"""
    all_pages = set()
    
    # Collect all pages
    for item in items_to_merge:
        if item in clothing_index:
            all_pages.update(clothing_index[item])
            del clothing_index[item]
        else:
            print(f"⚠️  Item not found: '{item}'")
    
    # Create merged item
    clothing_index[new_name] = sorted(list(all_pages))
    
    # Update page items
    for page, items in page_items.items():
        updated_items = []
        merged_added = False
        for item in items:
            if item in items_to_merge:
                if not merged_added:
                    updated_items.append(new_name)
                    merged_added = True
            else:
                updated_items.append(item)
        page_items[page] = updated_items
    
    print(f"✅ Merged {len(items_to_merge)} items into: '{new_name}'")

def delete_item(clothing_index, page_items, item_name):
    """Delete an item completely"""
    if item_name in clothing_index:
        del clothing_index[item_name]
        
        # Remove from page items
        for page, items in page_items.items():
            if item_name in items:
                items.remove(item_name)
        
        print(f"✅ Deleted: '{item_name}'")
    else:
        print(f"❌ Item not found: '{item_name}'")

def main():
    """
    EDIT THIS FUNCTION TO CLEAN YOUR DATA
    
    Common cleaning tasks you might want to do:
    1. Merge similar items (e.g., variations with extra details)
    2. Rename items for consistency
    3. Delete incomplete/invalid items
    4. Standardize naming conventions
    """
    
    clothing_index, page_items = load_data()
    
    print("🧹 Starting data cleaning...")
    print(f"📊 Current stats: {len(clothing_index)} items, {len(page_items)} pages")
    
    # ================================================================
    # ADD YOUR CLEANING OPERATIONS HERE
    # ================================================================
    
    # Example 1: Merge items with extra details into base items
    merge_items(clothing_index, page_items, [
        "Dries striped polo Beams khaki",
        "Boglioli green polo Beams khaki", 
        "Zegna blue polo Beams khaki",
        "Boglioli tan polo Beams khaki",
        "Dries pink polo Beams khaki",
        "Altea olive polo Beams khaki"
    ], "Beams khaki trouser") # Note: this appears to be trousers, not polos
    
    # Example 2: Clean up items that got OCR'd incorrectly
    rename_item(clothing_index, page_items, 
                "trouser", 
                "Valentino ivory canvas trouser")
    
    # Example 3: Merge items that are clearly the same thing
    merge_items(clothing_index, page_items, [
        "Saint Laurent loafer Loewe espadrille",
        "Saint Laurent loafer Loro Piana sandal Loewe espadrille",
        "Saint Laurent loafer Castaner cream espadrille"
    ], "Saint Laurent loafer")
    
    # Example 4: Clean up combined items
    merge_items(clothing_index, page_items, [
        "Prada navy trouser Loro Piana sandal",
        "APC navy trouser Loro Piana sandal",
        "APC navy trouser Castaner cream espadrille"
    ], "APC navy trouser")
    
    # Example 5: Standardize polo naming
    rename_item(clothing_index, page_items,
                "polo Valentino ivory canvas",
                "Valentino ivory canvas trouser")  # This seems to be a trouser based on context
    
    # Example 6: Clean up items that got combined during OCR
    rename_item(clothing_index, page_items,
                "trouser Valentino camel cardigan",
                "Valentino camel trouser")
    
    # Add more cleaning operations here...
    # rename_item(clothing_index, page_items, "old_name", "new_name")
    # merge_items(clothing_index, page_items, ["item1", "item2"], "merged_name")
    # delete_item(clothing_index, page_items, "item_to_delete")
    
    # ================================================================
    # END OF CLEANING OPERATIONS
    # ================================================================
    
    print(f"📊 Final stats: {len(clothing_index)} items, {len(page_items)} pages")
    
    # Save the cleaned data
    save_data(clothing_index, page_items)
    print("💾 Data saved!")
    
    # Show top items after cleaning
    print("\n🏆 Top 10 items after cleaning:")
    sorted_items = sorted(clothing_index.items(), key=lambda x: len(x[1]), reverse=True)
    for item, pages in sorted_items[:10]:
        print(f"   {item}: {len(pages)} pages")

if __name__ == "__main__":
    main()