#!/usr/bin/env python3
"""
Flask web application for browsing clothing items and outfits.
"""

from flask import Flask, render_template, jsonify, send_from_directory
import json
import os

app = Flask(__name__)

# Load clothing data
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

@app.route('/')
def index():
    """Main page showing all clothing items"""
    clothing_index, page_items = load_data()
    
    # Sort items by frequency (most common first)
    sorted_items = sorted(clothing_index.items(), key=lambda x: len(x[1]), reverse=True)
    
    return render_template('index.html', 
                         clothing_items=sorted_items,
                         total_items=len(clothing_index))

@app.route('/item/<path:item_name>')
def item_detail(item_name):
    """Show pages where a specific item appears"""
    clothing_index, page_items = load_data()
    
    if item_name in clothing_index:
        pages = clothing_index[item_name]
        # Sort pages numerically
        pages.sort(key=lambda x: int(x.split('_')[1]) if '_' in x else int(x))
        return render_template('item_detail.html', 
                             item_name=item_name,
                             pages=pages)
    else:
        return "Item not found", 404

@app.route('/page/<page_name>')
def page_detail(page_name):
    """Show all items on a specific page"""
    clothing_index, page_items = load_data()
    
    if page_name in page_items:
        items = page_items[page_name]
        return render_template('page_detail.html',
                             page_name=page_name,
                             items=items)
    else:
        return "Page not found", 404

@app.route('/images/<path:filename>')
def serve_image(filename):
    """Serve images from the Kevin_Summer_Looks_Pages directory"""
    return send_from_directory('Kevin_Summer_Looks_Pages', filename)

@app.route('/api/search/<query>')
def search_items(query):
    """API endpoint to search for clothing items"""
    clothing_index, page_items = load_data()
    
    query_lower = query.lower()
    matching_items = {}
    
    for item, pages in clothing_index.items():
        if query_lower in item.lower():
            matching_items[item] = pages
    
    return jsonify(matching_items)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)