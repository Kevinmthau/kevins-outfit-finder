#!/usr/bin/env python3
"""
Data cleaning interface for clothing items.
Allows manual editing, merging, and cleaning of extracted clothing data.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
from collections import defaultdict

app = Flask(__name__)

def load_data():
    """Load clothing index and page items from JSON files"""
    try:
        with open('clothing_index.json', 'r') as f:
            clothing_index = json.load(f)
        with open('page_items.json', 'r') as f:
            page_items = json.load(f)
        return clothing_index, page_items
    except FileNotFoundError:
        return {}, {}

def save_data(clothing_index, page_items):
    """Save cleaned data back to JSON files"""
    with open('clothing_index.json', 'w') as f:
        json.dump(clothing_index, f, indent=2)
    with open('page_items.json', 'w') as f:
        json.dump(page_items, f, indent=2)

@app.route('/clean')
def data_cleaner():
    """Main data cleaning interface"""
    clothing_index, page_items = load_data()
    
    # Sort items by frequency for easier cleaning
    sorted_items = sorted(clothing_index.items(), key=lambda x: len(x[1]), reverse=True)
    
    # Identify potential duplicates/similar items
    potential_duplicates = find_potential_duplicates(clothing_index)
    
    return render_template('data_cleaner.html', 
                         clothing_items=sorted_items,
                         potential_duplicates=potential_duplicates,
                         total_items=len(clothing_index))

@app.route('/clean/rename', methods=['POST'])
def rename_item():
    """Rename a clothing item"""
    data = request.get_json()
    old_name = data['old_name']
    new_name = data['new_name']
    
    clothing_index, page_items = load_data()
    
    if old_name in clothing_index and old_name != new_name:
        # Update clothing index
        pages = clothing_index[old_name]
        del clothing_index[old_name]
        clothing_index[new_name] = pages
        
        # Update page items
        for page, items in page_items.items():
            if old_name in items:
                items[items.index(old_name)] = new_name
        
        save_data(clothing_index, page_items)
        return jsonify({'success': True, 'message': f'Renamed "{old_name}" to "{new_name}"'})
    
    return jsonify({'success': False, 'message': 'Item not found or names are the same'})

@app.route('/clean/merge', methods=['POST'])
def merge_items():
    """Merge multiple clothing items into one"""
    data = request.get_json()
    items_to_merge = data['items']
    target_name = data['target_name']
    
    clothing_index, page_items = load_data()
    
    # Collect all pages from items to merge
    all_pages = set()
    for item in items_to_merge:
        if item in clothing_index:
            all_pages.update(clothing_index[item])
            del clothing_index[item]
    
    # Create merged item
    clothing_index[target_name] = sorted(list(all_pages))
    
    # Update page items
    for page, items in page_items.items():
        updated_items = []
        merged_added = False
        for item in items:
            if item in items_to_merge:
                if not merged_added:
                    updated_items.append(target_name)
                    merged_added = True
            else:
                updated_items.append(item)
        page_items[page] = updated_items
    
    save_data(clothing_index, page_items)
    return jsonify({'success': True, 'message': f'Merged {len(items_to_merge)} items into "{target_name}"'})

@app.route('/clean/delete', methods=['POST'])
def delete_item():
    """Delete a clothing item"""
    data = request.get_json()
    item_name = data['item_name']
    
    clothing_index, page_items = load_data()
    
    if item_name in clothing_index:
        del clothing_index[item_name]
        
        # Remove from page items
        for page, items in page_items.items():
            if item_name in items:
                items.remove(item_name)
        
        save_data(clothing_index, page_items)
        return jsonify({'success': True, 'message': f'Deleted "{item_name}"'})
    
    return jsonify({'success': False, 'message': 'Item not found'})

@app.route('/clean/export')
def export_cleaned_data():
    """Export cleaned data as JSON"""
    clothing_index, page_items = load_data()
    
    export_data = {
        'clothing_index': clothing_index,
        'page_items': page_items,
        'statistics': {
            'total_items': len(clothing_index),
            'total_pages': len(page_items),
            'most_common_items': sorted(clothing_index.items(), key=lambda x: len(x[1]), reverse=True)[:10]
        }
    }
    
    return jsonify(export_data)

def find_potential_duplicates(clothing_index):
    """Find potential duplicate items based on similarity"""
    items = list(clothing_index.keys())
    duplicates = []
    
    for i, item1 in enumerate(items):
        for item2 in items[i+1:]:
            # Check for similar items
            if are_similar(item1, item2):
                duplicates.append({
                    'item1': item1,
                    'item2': item2,
                    'pages1': len(clothing_index[item1]),
                    'pages2': len(clothing_index[item2]),
                    'similarity_reason': get_similarity_reason(item1, item2)
                })
    
    return duplicates[:20]  # Return top 20 potential duplicates

def are_similar(item1, item2):
    """Check if two items are potentially similar/duplicates"""
    item1_lower = item1.lower()
    item2_lower = item2.lower()
    
    # Check for common patterns that indicate duplicates
    patterns = [
        # Same brand and item type
        lambda x, y: any(brand in x and brand in y for brand in ['saint laurent', 'boglioli', 'lardini', 'dries', 'prada']),
        # Similar descriptions with extra details
        lambda x, y: len(set(x.split()) & set(y.split())) >= 3,
        # One is subset of another
        lambda x, y: x in y or y in x,
    ]
    
    return any(pattern(item1_lower, item2_lower) for pattern in patterns)

def get_similarity_reason(item1, item2):
    """Get reason why items are considered similar"""
    item1_lower = item1.lower()
    item2_lower = item2.lower()
    
    if item1_lower in item2_lower or item2_lower in item1_lower:
        return "One item contains the other"
    
    common_words = set(item1_lower.split()) & set(item2_lower.split())
    if len(common_words) >= 3:
        return f"Share {len(common_words)} common words: {', '.join(list(common_words)[:3])}"
    
    return "Similar patterns detected"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)