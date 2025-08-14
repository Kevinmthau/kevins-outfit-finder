#!/usr/bin/env python3
"""
Script to clean OCR artifacts and merge items with leading characters.
Specifically targeting variations of "The Row brown tassel loafer"
"""

import json
import re

def clean_spring_data():
    """Clean Spring collection data"""
    
    # Load Spring data
    with open('clothing_index_spring.json', 'r') as f:
        index = json.load(f)
    
    with open('page_items_spring.json', 'r') as f:
        page_items = json.load(f)
    
    # Items to merge - variations of The Row brown tassel loafer
    artifacts_to_clean = [
        "i The Row brown tassel loafer (Footwear)",
        "of The Row brown tassel loafer (Footwear)", 
        "f The Row brown tassel loafer (Footwear)",
        '". The Row brown tassel loafer (Footwear)',
        "eS) Saint Laurent loafer (Footwear)",
        "Ic Saint Laurent loafer (Footwear)"
    ]
    
    canonical_names = {
        "i The Row brown tassel loafer (Footwear)": "The Row brown tassel loafer (Footwear)",
        "of The Row brown tassel loafer (Footwear)": "The Row brown tassel loafer (Footwear)",
        "f The Row brown tassel loafer (Footwear)": "The Row brown tassel loafer (Footwear)",
        '". The Row brown tassel loafer (Footwear)': "The Row brown tassel loafer (Footwear)",
        "eS) Saint Laurent loafer (Footwear)": "Saint Laurent loafer (Footwear)",
        "Ic Saint Laurent loafer (Footwear)": "Saint Laurent loafer (Footwear)"
    }
    
    # Create cleaned index
    cleaned_index = {}
    merge_count = 0
    
    for item, pages in index.items():
        if item in canonical_names:
            # This is an artifact - merge with canonical
            canonical = canonical_names[item]
            if canonical in cleaned_index:
                # Add pages to existing canonical entry
                cleaned_index[canonical].extend(pages)
                print(f"Merging '{item}' -> '{canonical}' ({len(pages)} pages)")
            else:
                # Start new canonical entry
                cleaned_index[canonical] = pages
                print(f"Converting '{item}' -> '{canonical}'")
            merge_count += 1
        else:
            # Keep as is
            if item in cleaned_index:
                # Already exists (shouldn't happen but just in case)
                cleaned_index[item].extend(pages)
            else:
                cleaned_index[item] = pages
    
    # Sort and deduplicate pages for merged items
    for item in cleaned_index:
        pages = list(set(cleaned_index[item]))
        cleaned_index[item] = sorted(pages, key=lambda x: int(x.split('_')[1]))
    
    # Clean page_items
    for page, items in page_items.items():
        cleaned_items = []
        for item in items:
            if isinstance(item, dict):
                item_name = item['name']
                category = item['category']
                
                # Clean the name
                # Remove leading OCR artifacts (single letters, special chars followed by space)
                cleaned_name = re.sub(r'^[a-z]\s+The Row', 'The Row', item_name, flags=re.IGNORECASE)
                cleaned_name = re.sub(r'^[^\w]+\s*The Row', 'The Row', cleaned_name)
                cleaned_name = re.sub(r'^of\s+The Row', 'The Row', cleaned_name)
                cleaned_name = re.sub(r'^[eE][sS]\)\s*Saint Laurent', 'Saint Laurent', cleaned_name)
                cleaned_name = re.sub(r'^[iI]c\s+Saint Laurent', 'Saint Laurent', cleaned_name)
                cleaned_name = re.sub(r'^[""]\.\s*The Row', 'The Row', cleaned_name)
                
                # Also clean any other common OCR artifacts
                cleaned_name = re.sub(r'^\W+\s*', '', cleaned_name)  # Remove leading non-word chars
                cleaned_name = re.sub(r'\s+', ' ', cleaned_name)  # Normalize spaces
                
                if cleaned_name != item_name:
                    print(f"  Page {page}: '{item_name}' -> '{cleaned_name}'")
                
                cleaned_items.append({
                    'name': cleaned_name.strip(),
                    'category': category
                })
            else:
                cleaned_items.append(item)
        
        page_items[page] = cleaned_items
    
    # Save cleaned data
    with open('clothing_index_spring.json', 'w') as f:
        json.dump(cleaned_index, f, indent=2)
    
    with open('page_items_spring.json', 'w') as f:
        json.dump(page_items, f, indent=2)
    
    print(f"\n✅ Cleaning complete!")
    print(f"Merged {merge_count} artifact entries")
    print(f"Total unique items: {len(cleaned_index)}")
    
    # Show the consolidated The Row brown tassel loafer entry
    if "The Row brown tassel loafer (Footwear)" in cleaned_index:
        pages = cleaned_index["The Row brown tassel loafer (Footwear)"]
        print(f"\n'The Row brown tassel loafer' now appears on {len(pages)} pages")

def main():
    print("=" * 60)
    print("Cleaning OCR artifacts in Spring collection...")
    print("=" * 60)
    
    clean_spring_data()

if __name__ == "__main__":
    main()