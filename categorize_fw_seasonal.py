#!/usr/bin/env python3
"""
Web interface to manage all collections - categorize seasons, delete pages.
"""

from flask import Flask, render_template_string, request, jsonify, send_from_directory
import json
from pathlib import Path

app = Flask(__name__)

# Collection configs
COLLECTIONS = {
    'summer': {
        'name': 'Summer',
        'icon': '☀️',
        'page_items_file': 'page_items.json',
        'clothing_index_file': 'clothing_index.json',
        'image_folder': 'Kevin_Summer_Looks_Pages',
        'seasons': ['Summer']
    },
    'spring': {
        'name': 'Spring',
        'icon': '🌸',
        'page_items_file': 'page_items_spring.json',
        'clothing_index_file': 'clothing_index_spring.json',
        'image_folder': 'KEVIN_Spring_Looks_Images',
        'seasons': ['Spring']
    },
    'fw': {
        'name': 'Fall/Winter',
        'icon': '🍂❄️',
        'page_items_file': 'page_items_fw.json',
        'clothing_index_file': 'clothing_index_fw.json',
        'image_folder': 'Fall_Winter_Looks_Images',
        'seasons': ['Fall', 'Winter']
    }
}

# All available seasons for cross-collection moves
ALL_SEASONS = ['Summer', 'Spring', 'Fall', 'Winter']

# Map season to collection
SEASON_TO_COLLECTION = {
    'Summer': 'summer',
    'Spring': 'spring',
    'Fall': 'fw',
    'Winter': 'fw'
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Outfit Manager</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 0;
            background: #f5f5f5;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 { color: #333; margin: 0 0 20px 0; }

        /* Tab Navigation */
        .nav {
            background: #34495e;
            padding: 0;
            display: flex;
            justify-content: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .nav button {
            color: #ecf0f1;
            background: none;
            border: none;
            padding: 15px 25px;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 1rem;
            font-weight: 500;
            position: relative;
        }
        .nav button:hover { background-color: #2c3e50; }
        .nav button.active { background-color: #2c3e50; }
        .nav button.active::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: #3498db;
        }
        .nav a {
            color: #ecf0f1;
            text-decoration: none;
            padding: 15px 25px;
            font-size: 1rem;
            font-weight: 500;
            transition: all 0.3s;
        }
        .nav a:hover { background-color: #2c3e50; }

        .stats {
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .stats span {
            display: inline-block;
            margin-right: 20px;
            padding: 5px 10px;
            border-radius: 4px;
        }
        .stats .total { background: #e0e0e0; }
        .stats .uncategorized { background: #ffeb3b; }
        .stats .fall { background: #ff9800; color: white; }
        .stats .winter { background: #2196f3; color: white; }
        .controls {
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        .controls button {
            padding: 10px 20px;
            margin-right: 10px;
            margin-bottom: 5px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        .btn-summer { background: #ffc107; color: #333; }
        .btn-spring { background: #e91e63; color: white; }
        .btn-fall { background: #ff9800; color: white; }
        .btn-winter { background: #2196f3; color: white; }
        .btn-clear { background: #9e9e9e; color: white; }
        .btn-delete { background: #f44336; color: white; }
        .btn-save { background: #4caf50; color: white; font-weight: bold; }
        .filter-btns button {
            padding: 8px 16px;
            margin: 5px;
            border: 2px solid #ddd;
            border-radius: 4px;
            cursor: pointer;
            background: white;
        }
        .filter-btns button.active { border-color: #333; background: #333; color: white; }
        .pages-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
        }
        .page-card {
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .page-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        .page-card.selected { outline: 3px solid #2196f3; }
        .page-card.summer { border-top: 4px solid #ffc107; }
        .page-card.spring { border-top: 4px solid #e91e63; }
        .page-card.fall { border-top: 4px solid #ff9800; }
        .page-card.winter { border-top: 4px solid #2196f3; }
        .page-card.deleted { opacity: 0.4; border-top: 4px solid #f44336; }
        .page-card img {
            width: 100%;
            height: auto;
            cursor: pointer;
        }
        .page-info { padding: 12px; }
        .page-info h3 {
            margin: 0 0 8px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .page-info .item-count {
            font-size: 12px;
            color: #666;
            font-weight: normal;
        }
        .season-badge {
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
        }
        .season-badge.summer { background: #ffc107; color: #333; }
        .season-badge.spring { background: #e91e63; color: white; }
        .season-badge.fall { background: #ff9800; color: white; }
        .season-badge.winter { background: #2196f3; color: white; }
        .season-badge.deleted { background: #f44336; color: white; }
        .page-actions {
            display: flex;
            gap: 8px;
            margin-top: 10px;
        }
        .page-actions button {
            flex: 1;
            padding: 8px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
        }
        .items-preview {
            font-size: 11px;
            color: #666;
            max-height: 60px;
            overflow: hidden;
            margin-top: 8px;
        }
        .message {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 25px;
            border-radius: 4px;
            color: white;
            font-weight: bold;
            z-index: 1000;
            display: none;
        }
        .message.success { background: #4caf50; }
        .message.error { background: #f44336; }
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.9);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }
        .modal.active { display: flex; }
        .modal img {
            max-width: 90%;
            max-height: 90%;
            object-fit: contain;
        }
        .modal-close {
            position: absolute;
            top: 20px;
            right: 30px;
            color: white;
            font-size: 40px;
            cursor: pointer;
        }
        .hidden { display: none; }
    </style>
</head>
<body>
    <div class="nav">
        <button onclick="switchCollection('summer')" id="nav-summer">☀️ Summer</button>
        <button onclick="switchCollection('spring')" id="nav-spring">🌸 Spring</button>
        <button onclick="switchCollection('fw')" id="nav-fw" class="active">🍂❄️ Fall/Winter</button>
        <a href="/" style="margin-left: auto;">← Back to Finder</a>
    </div>

    <div class="container">
        <h1 id="page-title">Manage Fall/Winter Collection</h1>

        <div class="stats">
            <span class="total">Total: <strong id="total-count">0</strong> pages</span>
            <span style="background: #ffcdd2;">To Delete: <strong id="deleted-count">0</strong></span>
        </div>

        <div class="controls">
            <div style="margin-bottom: 15px;">
                <strong>Recategorize selected pages:</strong>
                <button class="btn-summer" onclick="setSeasonForSelected('Summer')">☀️ Summer</button>
                <button class="btn-spring" onclick="setSeasonForSelected('Spring')">🌸 Spring</button>
                <button class="btn-fall" onclick="setSeasonForSelected('Fall')">🍂 Fall</button>
                <button class="btn-winter" onclick="setSeasonForSelected('Winter')">❄️ Winter</button>
                <button class="btn-delete" onclick="markDeleteSelected()">🗑️ Delete</button>
                <button class="btn-save" onclick="saveChanges()">💾 Save All Changes</button>
            </div>
            <div class="filter-btns">
                <strong>Show:</strong>
                <button class="active" data-filter="all" onclick="setFilter('all')">All Pages</button>
                <button data-filter="uncategorized" onclick="setFilter('uncategorized')">Uncategorized</button>
                <button data-filter="deleted" onclick="setFilter('deleted')">Marked for Deletion</button>
            </div>
        </div>

        <div id="pages-container" class="pages-grid"></div>
    </div>

    <div id="modal" class="modal" onclick="closeModal()">
        <span class="modal-close">&times;</span>
        <img id="modal-img" src="" alt="">
    </div>

    <div id="message" class="message"></div>

    <script>
        let currentCollection = 'fw';
        let collectionConfig = {};
        let pageData = {};
        let pageSeasons = {};  // page -> season (Summer, Spring, Fall, Winter, deleted)
        let selectedPages = new Set();
        let currentFilter = 'all';

        // Map seasons to collections
        const SEASON_TO_COLLECTION = {
            'Summer': 'summer',
            'Spring': 'spring',
            'Fall': 'fw',
            'Winter': 'fw'
        };

        async function loadCollectionConfig() {
            const response = await fetch('/api/collections');
            collectionConfig = await response.json();
        }

        async function switchCollection(collection) {
            currentCollection = collection;
            selectedPages.clear();
            currentFilter = 'all';

            // Update nav
            document.querySelectorAll('.nav button').forEach(btn => btn.classList.remove('active'));
            document.getElementById('nav-' + collection).classList.add('active');

            // Update title
            const config = collectionConfig[collection];
            document.getElementById('page-title').textContent = 'Manage ' + config.name + ' Collection';

            // Reset filter buttons
            document.querySelectorAll('.filter-btns button').forEach(btn => {
                btn.classList.toggle('active', btn.dataset.filter === 'all');
            });

            await loadData();
        }

        async function loadData() {
            const response = await fetch('/api/pages/' + currentCollection);
            const data = await response.json();
            pageData = data.pages;
            pageSeasons = data.seasons || {};
            renderPages();
            updateStats();
        }

        function renderPages() {
            const container = document.getElementById('pages-container');
            container.innerHTML = '';
            const config = collectionConfig[currentCollection];

            const sortedPages = Object.keys(pageData).sort((a, b) => {
                const numA = parseInt(a.replace('page_', ''));
                const numB = parseInt(b.replace('page_', ''));
                return numA - numB;
            });

            for (const page of sortedPages) {
                const season = pageSeasons[page];

                // Apply filter
                if (currentFilter === 'deleted' && season !== 'deleted') continue;
                if (currentFilter === 'uncategorized' && season) continue;

                const items = pageData[page];
                const pageNum = page.replace('page_', '');
                const isSelected = selectedPages.has(page);

                const card = document.createElement('div');
                card.className = `page-card ${season ? season.toLowerCase() : ''} ${isSelected ? 'selected' : ''}`;
                card.dataset.page = page;

                let seasonBadge = '';
                if (season === 'Summer') seasonBadge = '<span class="season-badge summer">☀️ Summer</span>';
                else if (season === 'Spring') seasonBadge = '<span class="season-badge spring">🌸 Spring</span>';
                else if (season === 'Fall') seasonBadge = '<span class="season-badge fall">🍂 Fall</span>';
                else if (season === 'Winter') seasonBadge = '<span class="season-badge winter">❄️ Winter</span>';
                else if (season === 'deleted') seasonBadge = '<span class="season-badge deleted">🗑️ To Delete</span>';

                // Get item names for preview
                let itemNames = [];
                if (Array.isArray(items)) {
                    itemNames = items.map(i => typeof i === 'object' ? i.name : i);
                }

                card.innerHTML = `
                    <img src="/images/${currentCollection}/page_${pageNum}.png" alt="Page ${pageNum}"
                         onclick="openModal('/images/${currentCollection}/page_${pageNum}.png', event)"
                         onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%22200%22 height=%22200%22><rect fill=%22%23ddd%22 width=%22200%22 height=%22200%22/><text x=%2250%25%22 y=%2250%25%22 dominant-baseline=%22middle%22 text-anchor=%22middle%22 fill=%22%23999%22>No Image</text></svg>'">
                    <div class="page-info">
                        <h3>
                            Page ${pageNum}
                            <span class="item-count">${items.length} items</span>
                        </h3>
                        ${seasonBadge}
                        <div class="items-preview">
                            ${itemNames.slice(0, 3).join(', ')}${itemNames.length > 3 ? '...' : ''}
                        </div>
                        <div class="page-actions">
                            <button class="btn-summer" onclick="setPageSeason('${page}', 'Summer', event)" title="Summer">☀️</button>
                            <button class="btn-spring" onclick="setPageSeason('${page}', 'Spring', event)" title="Spring">🌸</button>
                            <button class="btn-fall" onclick="setPageSeason('${page}', 'Fall', event)" title="Fall">🍂</button>
                            <button class="btn-winter" onclick="setPageSeason('${page}', 'Winter', event)" title="Winter">❄️</button>
                            <button class="btn-delete" onclick="setPageSeason('${page}', 'deleted', event)" title="Delete">🗑️</button>
                        </div>
                    </div>
                `;

                card.addEventListener('click', (e) => {
                    if (e.target.tagName !== 'BUTTON' && e.target.tagName !== 'IMG') {
                        togglePageSelection(page);
                    }
                });

                container.appendChild(card);
            }
        }

        function togglePageSelection(page) {
            if (selectedPages.has(page)) {
                selectedPages.delete(page);
            } else {
                selectedPages.add(page);
            }
            renderPages();
        }

        function setPageSeason(page, season, event) {
            if (event) event.stopPropagation();
            pageSeasons[page] = season;
            renderPages();
            updateStats();
        }

        function setSeasonForSelected(season) {
            selectedPages.forEach(page => {
                pageSeasons[page] = season;
            });
            selectedPages.clear();
            renderPages();
            updateStats();
        }

        function markDeleteSelected() {
            selectedPages.forEach(page => {
                pageSeasons[page] = 'deleted';
            });
            selectedPages.clear();
            renderPages();
            updateStats();
        }

        function setFilter(filter) {
            currentFilter = filter;
            document.querySelectorAll('.filter-btns button').forEach(btn => {
                btn.classList.toggle('active', btn.dataset.filter === filter);
            });
            renderPages();
        }

        function updateStats() {
            let total = Object.keys(pageData).length;
            let deleted = 0;

            for (const page of Object.keys(pageData)) {
                if (pageSeasons[page] === 'deleted') deleted++;
            }

            document.getElementById('total-count').textContent = total - deleted;
            document.getElementById('deleted-count').textContent = deleted;
        }

        async function saveChanges() {
            const response = await fetch('/api/save/' + currentCollection, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(pageSeasons)
            });
            const result = await response.json();
            showMessage(result.success ? 'success' : 'error', result.message);
            if (result.success) {
                loadData();
            }
        }

        function openModal(src, event) {
            event.stopPropagation();
            document.getElementById('modal-img').src = src;
            document.getElementById('modal').classList.add('active');
        }

        function closeModal() {
            document.getElementById('modal').classList.remove('active');
        }

        function showMessage(type, text) {
            const msg = document.getElementById('message');
            msg.className = 'message ' + type;
            msg.textContent = text;
            msg.style.display = 'block';
            setTimeout(() => msg.style.display = 'none', 3000);
        }

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') closeModal();
        });

        // Initialize
        (async function init() {
            await loadCollectionConfig();
            await switchCollection('fw');
        })();
    </script>
</body>
</html>
"""

def load_collection_data(collection):
    """Load page items for a collection."""
    config = COLLECTIONS[collection]
    filepath = config['page_items_file']
    if Path(filepath).exists():
        with open(filepath, 'r') as f:
            return json.load(f)
    return {}

def save_collection_data(collection, data):
    """Save page items for a collection."""
    config = COLLECTIONS[collection]
    with open(config['page_items_file'], 'w') as f:
        json.dump(data, f, indent=2)

def rebuild_index(collection, page_items):
    """Rebuild clothing index from page_items."""
    config = COLLECTIONS[collection]
    clothing_index = {}

    for page, items in page_items.items():
        page_num = int(page.replace('page_', ''))
        for item in items:
            # Handle both object format and simple string format
            if isinstance(item, dict):
                name = item.get('name', str(item))
            else:
                name = item

            if name not in clothing_index:
                clothing_index[name] = []
            if page_num not in clothing_index[name]:
                clothing_index[name].append(page_num)

    # Sort page numbers
    for name in clothing_index:
        clothing_index[name].sort()

    with open(config['clothing_index_file'], 'w') as f:
        json.dump(clothing_index, f, indent=2)

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/images/<collection>/page_<int:page_num>.png')
def serve_image(collection, page_num):
    """Serve images for any collection."""
    config = COLLECTIONS.get(collection)
    if not config:
        return "Collection not found", 404
    return send_from_directory(config['image_folder'], f'page_{page_num}.png')

@app.route('/api/collections')
def get_collections():
    """Return collection configurations."""
    return jsonify(COLLECTIONS)

@app.route('/api/pages/<collection>')
def get_pages(collection):
    """Get pages for a specific collection."""
    if collection not in COLLECTIONS:
        return jsonify({'error': 'Collection not found'}), 404

    config = COLLECTIONS[collection]
    data = load_collection_data(collection)

    pages = {}
    seasons = {}

    for page, items in data.items():
        # Normalize items to list of objects
        if isinstance(items, list):
            if len(items) > 0 and isinstance(items[0], dict):
                pages[page] = items
                # Get season from first item if applicable
                if items[0].get('season'):
                    seasons[page] = items[0]['season']
            else:
                # Simple string list (summer format)
                pages[page] = [{'name': item, 'category': 'Other'} for item in items]
        else:
            pages[page] = []

    return jsonify({'pages': pages, 'seasons': seasons})

@app.route('/api/save/<collection>', methods=['POST'])
def save_collection(collection):
    """Save changes for a collection, including cross-collection moves."""
    if collection not in COLLECTIONS:
        return jsonify({'error': 'Collection not found'}), 404

    page_seasons = request.get_json()
    data = load_collection_data(collection)

    pages_to_delete = []
    pages_to_move = {}  # {target_collection: [(page, items, season), ...]}
    updated = 0

    for page, season in page_seasons.items():
        if page not in data:
            continue

        if season == 'deleted':
            pages_to_delete.append(page)
        elif season in ALL_SEASONS:
            target_collection = SEASON_TO_COLLECTION[season]

            if target_collection != collection:
                # Moving to a different collection
                if target_collection not in pages_to_move:
                    pages_to_move[target_collection] = []
                pages_to_move[target_collection].append((page, data[page], season))
                pages_to_delete.append(page)  # Remove from current collection
            else:
                # Staying in same collection, just update season
                for item in data[page]:
                    if isinstance(item, dict):
                        item['season'] = season
                updated += 1

    # Delete/move pages from current collection
    for page in pages_to_delete:
        del data[page]

    save_collection_data(collection, data)
    rebuild_index(collection, data)

    # Add pages to target collections
    moved_count = 0
    for target_collection, pages in pages_to_move.items():
        target_data = load_collection_data(target_collection)

        for page, items, season in pages:
            # Find next available page number in target
            existing_nums = [int(p.replace('page_', '')) for p in target_data.keys()]
            next_num = max(existing_nums, default=0) + 1
            new_page = f'page_{next_num}'

            # Convert items to target format and set season
            new_items = []
            for item in items:
                if isinstance(item, dict):
                    new_item = {'name': item.get('name', str(item)), 'category': item.get('category', 'Other')}
                    new_item['season'] = season
                    new_items.append(new_item)
                else:
                    new_items.append({'name': item, 'category': 'Other', 'season': season})

            target_data[new_page] = new_items
            moved_count += 1

        save_collection_data(target_collection, target_data)
        rebuild_index(target_collection, target_data)

    deleted_count = len(pages_to_delete) - moved_count
    msg = f'Saved!'
    if updated:
        msg += f' Updated {updated} pages.'
    if moved_count:
        msg += f' Moved {moved_count} pages to other collections.'
    if deleted_count > 0:
        msg += f' Deleted {deleted_count} pages.'

    return jsonify({'success': True, 'message': msg})

if __name__ == '__main__':
    print("\n" + "="*50)
    print("Outfit Manager")
    print("="*50)
    print("\nVisit: http://localhost:5002")
    print("\nManage all collections - Summer, Spring, Fall/Winter")
    print("="*50 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5002)
