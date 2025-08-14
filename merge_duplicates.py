#!/usr/bin/env python3
"""
Script to merge duplicate clothing items in both Summer and Spring collections.
"""

import json
import re

def normalize_item_name(name):
    """Normalize item name for comparison"""
    # Remove leading underscores and extra spaces
    cleaned = name.strip().lstrip('_').strip()
    # Remove extra spaces inside
    cleaned = ' '.join(cleaned.split())
    return cleaned

def merge_duplicates_in_index(index_file, page_items_file):
    """Merge duplicate items in a clothing index"""
    
    # Load the data
    with open(index_file, 'r') as f:
        index = json.load(f)
    
    with open(page_items_file, 'r') as f:
        page_items = json.load(f)
    
    # Find and merge duplicates
    merged_index = {}
    merge_map = {}  # Maps old names to new canonical names
    
    for item, pages in index.items():
        # For Spring items, extract the base name without category
        if '(' in item and ')' in item:
            base_name = item[:item.rfind('(')].strip()
            category = item[item.rfind('(')+1:item.rfind(')')]
            normalized = normalize_item_name(base_name)
            canonical_key = f"{normalized} ({category})"
        else:
            normalized = normalize_item_name(item)
            # Special case for Loro Piana sandal - use capital P
            if normalized.lower() == "loro piana sandal":
                normalized = "Loro Piana sandal"
            canonical_key = normalized
        
        # Check if we've seen a similar item
        found_match = False
        for existing_key in merged_index:
            if '(' in existing_key and ')' in existing_key:
                existing_base = existing_key[:existing_key.rfind('(')].strip()
                existing_category = existing_key[existing_key.rfind('(')+1:existing_key.rfind(')')]
                if normalized == existing_base and category == existing_category:
                    # Merge pages
                    existing_pages = merged_index[existing_key]
                    all_pages = list(set(existing_pages + pages))
                    merged_index[existing_key] = sorted(all_pages, key=lambda x: int(x.split('_')[1]))
                    merge_map[item] = existing_key
                    found_match = True
                    print(f"Merging: '{item}' into '{existing_key}'")
                    break
            else:
                # For Summer items, check case-insensitive match
                if normalized.lower() == existing_key.lower():
                    # Use the properly capitalized version
                    if normalized != existing_key and normalized[0].isupper():
                        # Replace with better capitalized version
                        merged_index[normalized] = list(set(merged_index[existing_key] + pages))
                        del merged_index[existing_key]
                        merge_map[existing_key] = normalized
                        merge_map[item] = normalized
                        print(f"Merging and recapitalizing: '{item}' and '{existing_key}' -> '{normalized}'")
                    else:
                        # Add to existing
                        existing_pages = merged_index[existing_key]
                        all_pages = list(set(existing_pages + pages))
                        merged_index[existing_key] = sorted(all_pages, key=lambda x: int(x.split('_')[1]))
                        merge_map[item] = existing_key
                        print(f"Merging: '{item}' into '{existing_key}'")
                    found_match = True
                    break
        
        if not found_match:
            merged_index[canonical_key] = sorted(pages, key=lambda x: int(x.split('_')[1]))
            merge_map[item] = canonical_key
    
    # Update page_items to use canonical names
    updated_page_items = {}
    for page, items in page_items.items():
        if isinstance(items, list):
            if isinstance(items[0], dict):  # Spring format
                updated_items = []
                for item_obj in items:
                    item_name = item_obj['name']
                    category = item_obj['category']
                    normalized = normalize_item_name(item_name)
                    # Find the canonical name
                    canonical = f"{normalized} ({category})"
                    if canonical in merged_index:
                        updated_items.append({
                            'name': normalized,
                            'category': category
                        })
                    else:
                        # Try without category suffix
                        found = False
                        for key in merged_index:
                            if key.startswith(normalized) and f"({category})" in key:
                                base_name = key[:key.rfind('(')].strip()
                                updated_items.append({
                                    'name': base_name,
                                    'category': category
                                })
                                found = True
                                break
                        if not found:
                            updated_items.append(item_obj)
                updated_page_items[page] = updated_items
            else:  # Summer format (simple strings)
                updated_items = []
                for item in items:
                    normalized = normalize_item_name(item)
                    # Special case for Loro Piana sandal
                    if normalized.lower() == "loro piana sandal":
                        normalized = "Loro Piana sandal"
                    if normalized in merged_index:
                        updated_items.append(normalized)
                    else:
                        # Find canonical version
                        found = False
                        for canonical in merged_index:
                            if canonical.lower() == normalized.lower():
                                updated_items.append(canonical)
                                found = True
                                break
                        if not found:
                            updated_items.append(item)
                updated_page_items[page] = updated_items
        else:
            updated_page_items[page] = items
    
    return merged_index, updated_page_items

def main():
    print("=" * 60)
    print("Merging duplicate items in Summer collection...")
    print("=" * 60)
    
    # Process Summer collection
    summer_index, summer_pages = merge_duplicates_in_index(
        'clothing_index.json', 
        'page_items.json'
    )
    
    # Save updated Summer files
    with open('clothing_index.json', 'w') as f:
        json.dump(summer_index, f, indent=2)
    
    with open('page_items.json', 'w') as f:
        json.dump(summer_pages, f, indent=2)
    
    print(f"\nUpdated Summer collection: {len(summer_index)} unique items")
    
    print("\n" + "=" * 60)
    print("Merging duplicate items in Spring collection...")
    print("=" * 60)
    
    # Process Spring collection
    spring_index, spring_pages = merge_duplicates_in_index(
        'clothing_index_spring.json',
        'page_items_spring.json'
    )
    
    # Save updated Spring files
    with open('clothing_index_spring.json', 'w') as f:
        json.dump(spring_index, f, indent=2)
    
    with open('page_items_spring.json', 'w') as f:
        json.dump(spring_pages, f, indent=2)
    
    print(f"\nUpdated Spring collection: {len(spring_index)} unique items")
    
    print("\n" + "=" * 60)
    print("✅ Duplicate merging complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()