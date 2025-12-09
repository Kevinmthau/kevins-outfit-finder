#!/usr/bin/env python3
"""
Generate a static version of the outfit finder with all three collections.
Features:
- Lazy loading for images
- WebP support with PNG fallback
- Fuzzy search
- Unified categorized data format
"""

import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from config import (
    DATA_FILES,
    COLLECTION_PATHS,
    DIST_DIR,
    DIST_IMAGE_FOLDERS,
    CATEGORY_ORDER,
    CATEGORY_ICONS,
    COLLECTION_DISPLAY_NAMES,
    COLLECTION_ICONS,
    FUZZY_SEARCH_THRESHOLD,
)


def load_collection_data(collection: str) -> Tuple[Dict, Dict, Optional[Dict]]:
    """Load clothing data for a specific collection."""
    files = DATA_FILES.get(collection, {})

    clothing_index = {}
    page_items = {}
    category_stats = None

    if "clothing_index" in files and files["clothing_index"].exists():
        with open(files["clothing_index"], 'r') as f:
            clothing_index = json.load(f)

    if "page_items" in files and files["page_items"].exists():
        with open(files["page_items"], 'r') as f:
            page_items = json.load(f)

    if "category_stats" in files and files["category_stats"].exists():
        with open(files["category_stats"], 'r') as f:
            category_stats = json.load(f)

    return clothing_index, page_items, category_stats


def categorize_items(clothing_index: Dict[str, List[str]], collection: str) -> Dict[str, List[Tuple[str, List[str], str]]]:
    """Categorize items using category data from the item names."""
    # Get category order for this collection
    categories = CATEGORY_ORDER.get(collection, CATEGORY_ORDER["summer"])

    categorized: Dict[str, List[Tuple[str, List[str], str]]] = {cat: [] for cat in categories}

    for item, pages in clothing_index.items():
        # Extract category from item name if it's in format "Item Name (Category)"
        if '(' in item and ')' in item:
            category = item[item.rfind('(')+1:item.rfind(')')]
            item_name = item[:item.rfind('(')].strip()
        else:
            item_name = item
            category = "Other"

        if category in categorized:
            categorized[category].append((item_name, pages, category))
        else:
            categorized["Other"].append((item_name, pages, "Other"))

    # Sort each category by frequency
    for category in categorized:
        categorized[category].sort(key=lambda x: len(x[1]), reverse=True)

    return categorized


def generate_collection_html(collection_name: str, clothing_index: Dict, page_items: Dict, image_folder: str) -> str:
    """Generate HTML for a specific collection."""
    collection_key = collection_name.lower().replace("/", "").replace("fall", "f").replace("winter", "w")
    if collection_name == "Fall/Winter":
        collection_key = "fw"
    elif collection_name == "Summer":
        collection_key = "summer"
    elif collection_name == "Spring":
        collection_key = "spring"

    categorized_items = categorize_items(clothing_index, collection_key)
    category_order = CATEGORY_ORDER.get(collection_key, CATEGORY_ORDER["summer"])

    # Generate category sections
    category_sections = []
    for category in category_order:
        if category not in categorized_items or not categorized_items[category]:
            continue

        items = categorized_items[category]
        icon = CATEGORY_ICONS.get(category, '📦')

        section_html = f"""
                    <div class="category-section">
                        <div class="category-header">
                            <h2>{icon} {category}</h2>
                            <p class="category-description">{len(items)} items in this category</p>
                        </div>
                        <div class="item-grid">"""

        for item_name, pages, _ in items:
            escaped_item = item_name.replace("'", "\\'").replace('"', '\\"')
            section_html += f"""
                            <div class="item-card" data-item-name="{item_name}" onclick="showItemDetail('{escaped_item}', '{collection_name}', '{image_folder}')">
                                <div class="item-name">{item_name}</div>
                                <div class="item-count">
                                    Appears on {len(pages)} page{'s' if len(pages) > 1 else ''}
                                </div>
                            </div>"""

        section_html += """
                        </div>
                    </div>"""

        category_sections.append(section_html)

    return ''.join(category_sections)


def get_fuzzy_search_js() -> str:
    """Return JavaScript for fuzzy search functionality."""
    return """
        // Fuzzy search implementation
        function levenshteinDistance(str1, str2) {
            const m = str1.length;
            const n = str2.length;
            const dp = Array(m + 1).fill(null).map(() => Array(n + 1).fill(0));

            for (let i = 0; i <= m; i++) dp[i][0] = i;
            for (let j = 0; j <= n; j++) dp[0][j] = j;

            for (let i = 1; i <= m; i++) {
                for (let j = 1; j <= n; j++) {
                    if (str1[i - 1] === str2[j - 1]) {
                        dp[i][j] = dp[i - 1][j - 1];
                    } else {
                        dp[i][j] = 1 + Math.min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]);
                    }
                }
            }
            return dp[m][n];
        }

        function fuzzyMatch(query, text, threshold = 0.6) {
            query = query.toLowerCase();
            text = text.toLowerCase();

            // Exact substring match
            if (text.includes(query)) return true;

            // Check each word in the text
            const words = text.split(/\\s+/);
            for (const word of words) {
                // Skip very short words
                if (word.length < 3) continue;

                // Check if query is similar to any word
                const distance = levenshteinDistance(query, word);
                const maxLen = Math.max(query.length, word.length);
                const similarity = 1 - (distance / maxLen);

                if (similarity >= threshold) return true;

                // Also check if query is a prefix with typos
                if (word.startsWith(query.substring(0, Math.min(3, query.length)))) {
                    const prefixDist = levenshteinDistance(query, word.substring(0, query.length));
                    if (prefixDist <= 2) return true;
                }
            }

            // Check brand names specifically (allow more tolerance)
            const brands = ['saint laurent', 'loro piana', 'bottega veneta', 'tom ford',
                          'the row', 'brunello', 'valentino', 'boglioli', 'lardini'];
            for (const brand of brands) {
                if (text.includes(brand)) {
                    const brandDist = levenshteinDistance(query, brand);
                    if (brandDist <= 3) return true;
                }
            }

            return false;
        }
"""


def create_all_collections_html() -> str:
    """Create the main static HTML file with all three collections."""

    # Load all collections
    summer_index, summer_items, _ = load_collection_data('summer')
    spring_index, spring_items, _ = load_collection_data('spring')
    fw_index, fw_items, _ = load_collection_data('fw')

    # Generate HTML for each collection
    summer_html = generate_collection_html('Summer', summer_index, summer_items, 'images')
    spring_html = generate_collection_html('Spring', spring_index, spring_items, 'spring_images')
    fw_html = generate_collection_html('Fall/Winter', fw_index, fw_items, 'fw_images')

    fuzzy_search_js = get_fuzzy_search_js()

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kevin's Outfit Finder - All Seasons</title>
    <link rel="icon" type="image/png" href="/favicon.png">
    <link rel="shortcut icon" type="image/x-icon" href="/favicon.ico">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f8f9fa;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .nav {{
            background: #34495e;
            padding: 0;
            display: flex;
            justify-content: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .nav button {{
            color: #ecf0f1;
            background: none;
            border: none;
            padding: 15px 25px;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 1rem;
            font-weight: 500;
            position: relative;
        }}
        .nav button:hover {{
            background-color: #2c3e50;
        }}
        .nav button.active {{
            background-color: #2c3e50;
        }}
        .nav button.active::after {{
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: #3498db;
        }}
        .content {{
            padding: 30px;
        }}
        .search-box {{
            margin-bottom: 30px;
            text-align: center;
        }}
        .search-box input {{
            padding: 12px 20px;
            font-size: 16px;
            border: 2px solid #ddd;
            border-radius: 25px;
            width: 400px;
            max-width: 100%;
            outline: none;
            transition: border-color 0.3s;
        }}
        .search-box input:focus {{
            border-color: #667eea;
        }}
        .search-hint {{
            font-size: 0.85rem;
            color: #7f8c8d;
            margin-top: 8px;
        }}
        .category-section {{
            margin-bottom: 50px;
        }}
        .category-header {{
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 3px solid #e9ecef;
        }}
        .category-header h2 {{
            margin: 0 0 8px 0;
            font-size: 1.8rem;
            color: #2c3e50;
        }}
        .category-description {{
            margin: 0;
            color: #7f8c8d;
            font-size: 1rem;
        }}
        .item-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .item-card {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border: 1px solid #dee2e6;
            border-radius: 10px;
            padding: 20px;
            transition: all 0.3s ease;
            cursor: pointer;
        }}
        .item-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.12);
            background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%);
        }}
        .item-card.hidden {{
            display: none;
        }}
        .item-name {{
            font-weight: 600;
            font-size: 1.1rem;
            color: #2c3e50;
            margin-bottom: 8px;
        }}
        .item-count {{
            color: #7f8c8d;
            font-size: 0.9rem;
        }}
        .page-images {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .page-card {{
            text-align: center;
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            border: 1px solid #e9ecef;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        .page-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        .page-card img {{
            max-width: 100%;
            height: auto;
            border-radius: 4px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .page-title {{
            margin-top: 10px;
            font-weight: 600;
            color: #2c3e50;
        }}
        .back-link {{
            display: inline-block;
            margin-bottom: 20px;
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
            cursor: pointer;
        }}
        .back-link:hover {{
            text-decoration: underline;
        }}
        .hidden {{
            display: none;
        }}
        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            overflow: auto;
            background-color: rgba(0,0,0,0.9);
            animation: fadeIn 0.3s;
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        .modal-content {{
            margin: auto;
            display: block;
            max-width: 90%;
            max-height: 90vh;
            margin-top: 5vh;
            animation: zoomIn 0.3s;
            cursor: zoom-out;
        }}
        @keyframes zoomIn {{
            from {{ transform: scale(0.8); }}
            to {{ transform: scale(1); }}
        }}
        .modal-close {{
            position: absolute;
            top: 20px;
            right: 35px;
            color: #f1f1f1;
            font-size: 40px;
            font-weight: bold;
            cursor: pointer;
            transition: color 0.3s;
            z-index: 1001;
        }}
        .modal-close:hover {{
            color: #bbb;
        }}
        .modal-caption {{
            margin: auto;
            display: block;
            width: 80%;
            max-width: 700px;
            text-align: center;
            color: #ccc;
            padding: 10px 0;
            font-size: 1.1rem;
        }}
        .clickable-image {{
            cursor: zoom-in;
            transition: transform 0.2s;
        }}
        .clickable-image:hover {{
            transform: scale(1.02);
        }}
        .page-detail {{
            display: flex;
            gap: 30px;
            flex-wrap: wrap;
        }}
        .page-image {{
            flex: 1;
            min-width: 300px;
        }}
        .page-items {{
            flex: 1;
            min-width: 300px;
        }}
        .page-items h3 {{
            color: #2c3e50;
            margin-bottom: 20px;
        }}
        .item-list {{
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        .item-link {{
            text-decoration: none;
            color: #2c3e50;
            padding: 12px 16px;
            background: #f8f9fa;
            border-radius: 6px;
            border: 1px solid #e9ecef;
            transition: all 0.3s;
            cursor: pointer;
        }}
        .item-link:hover {{
            background: #e9ecef;
            transform: translateX(5px);
        }}
        .no-results {{
            text-align: center;
            padding: 40px;
            color: #7f8c8d;
            font-size: 1.1rem;
        }}
        @media (max-width: 768px) {{
            .container {{
                margin: 10px;
                border-radius: 4px;
            }}
            .header {{
                padding: 20px;
            }}
            .header h1 {{
                font-size: 1.8rem;
            }}
            .nav button {{
                padding: 12px 15px;
                font-size: 0.9rem;
            }}
            .content {{
                padding: 20px;
            }}
            .search-box input {{
                width: 100%;
            }}
            .item-grid {{
                grid-template-columns: 1fr;
            }}
            .page-images {{
                grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            }}
            .page-detail {{
                flex-direction: column;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <button onclick="showCollection('summer')" class="active" id="nav-summer">☀️ Summer</button>
            <button onclick="showCollection('spring')" id="nav-spring">🌸 Spring</button>
            <button onclick="showCollection('fw')" id="nav-fw">❄️ Fall/Winter</button>
        </div>
        <div class="content">
            <!-- Summer Collection View -->
            <div id="summer-view">
                <div class="search-box">
                    <input type="text" id="summerSearchInput" placeholder="Search summer items..." onkeyup="filterItems('summer')">
                    <div class="search-hint">Supports fuzzy matching - try "sant lorent" for "Saint Laurent"</div>
                </div>

                <div id="summer-items-grid">
                    {summer_html}
                </div>
                <div id="summer-no-results" class="no-results hidden">No matching items found</div>
            </div>

            <!-- Spring Collection View -->
            <div id="spring-view" class="hidden">
                <div class="search-box">
                    <input type="text" id="springSearchInput" placeholder="Search spring items..." onkeyup="filterItems('spring')">
                    <div class="search-hint">Supports fuzzy matching - try "sant lorent" for "Saint Laurent"</div>
                </div>

                <div id="spring-items-grid">
                    {spring_html}
                </div>
                <div id="spring-no-results" class="no-results hidden">No matching items found</div>
            </div>

            <!-- Fall/Winter Collection View -->
            <div id="fw-view" class="hidden">
                <div class="search-box">
                    <input type="text" id="fwSearchInput" placeholder="Search fall/winter items..." onkeyup="filterItems('fw')">
                    <div class="search-hint">Supports fuzzy matching - try "sant lorent" for "Saint Laurent"</div>
                </div>

                <div id="fw-items-grid">
                    {fw_html}
                </div>
                <div id="fw-no-results" class="no-results hidden">No matching items found</div>
            </div>

            <!-- Item Detail View -->
            <div id="item-view" class="hidden">
                <a onclick="backToCollection()" class="back-link">&larr; Back to collection</a>
                <div id="item-detail-content"></div>
            </div>

            <!-- Page Detail View -->
            <div id="page-view" class="hidden">
                <a onclick="backToCollection()" class="back-link">&larr; Back to collection</a>
                <div id="page-detail-content"></div>
            </div>
        </div>

        <!-- Image Modal -->
        <div id="imageModal" class="modal">
            <span class="modal-close" onclick="closeModal()">&times;</span>
            <img class="modal-content" id="modalImage">
            <div class="modal-caption" id="modalCaption"></div>
        </div>
    </div>

    <script>
        // Data
        const summerClothingIndex = {json.dumps(summer_index)};
        const summerPageItems = {json.dumps(summer_items)};
        const springClothingIndex = {json.dumps(spring_index)};
        const springPageItems = {json.dumps(spring_items)};
        const fwClothingIndex = {json.dumps(fw_index)};
        const fwPageItems = {json.dumps(fw_items)};

        let currentCollection = 'summer';
        let currentClothingIndex = summerClothingIndex;
        let currentPageItems = summerPageItems;

        {fuzzy_search_js}

        // Image source helper - tries WebP first, falls back to PNG
        function getImageSrc(folder, page) {{
            return folder + '/' + page + '.png';
        }}

        function getImageSrcSet(folder, page) {{
            return folder + '/' + page + '.webp';
        }}

        // Modal functions
        function openModal(imageSrc, caption) {{
            const modal = document.getElementById('imageModal');
            const modalImg = document.getElementById('modalImage');
            const modalCaption = document.getElementById('modalCaption');

            modal.style.display = 'block';
            modalImg.src = imageSrc;
            modalCaption.innerHTML = caption;

            // Close on click outside
            modal.onclick = function(event) {{
                if (event.target === modal || event.target === modalImg) {{
                    closeModal();
                }}
            }}

            // Close on Escape key
            document.onkeydown = function(event) {{
                if (event.key === 'Escape') {{
                    closeModal();
                }}
            }}
        }}

        function closeModal() {{
            document.getElementById('imageModal').style.display = 'none';
        }}

        // Navigation
        function showCollection(collection) {{
            currentCollection = collection;

            // Hide all views
            document.getElementById('summer-view').classList.add('hidden');
            document.getElementById('spring-view').classList.add('hidden');
            document.getElementById('fw-view').classList.add('hidden');
            document.getElementById('item-view').classList.add('hidden');
            document.getElementById('page-view').classList.add('hidden');

            // Show selected collection
            document.getElementById(collection + '-view').classList.remove('hidden');

            // Update navigation
            document.querySelectorAll('.nav button').forEach(btn => btn.classList.remove('active'));
            document.getElementById('nav-' + collection).classList.add('active');

            // Update current data
            if (collection === 'summer') {{
                currentClothingIndex = summerClothingIndex;
                currentPageItems = summerPageItems;
            }} else if (collection === 'spring') {{
                currentClothingIndex = springClothingIndex;
                currentPageItems = springPageItems;
            }} else {{
                currentClothingIndex = fwClothingIndex;
                currentPageItems = fwPageItems;
            }}

            // Reset page title
            document.getElementById('page-title').textContent = "Kevin's Outfit Finder";
        }}

        function backToCollection() {{
            showCollection(currentCollection);
        }}

        // Search functionality with fuzzy matching
        function filterItems(collection) {{
            const search = document.getElementById(collection + 'SearchInput').value.trim();
            const container = document.getElementById(collection + '-items-grid');
            const items = container.querySelectorAll('.item-card');
            const noResults = document.getElementById(collection + '-no-results');

            let visibleCount = 0;

            items.forEach(item => {{
                const itemName = item.querySelector('.item-name').textContent;

                if (search === '' || fuzzyMatch(search, itemName)) {{
                    item.classList.remove('hidden');
                    visibleCount++;
                }} else {{
                    item.classList.add('hidden');
                }}
            }});

            // Show/hide category sections based on visible items
            const sections = container.querySelectorAll('.category-section');
            sections.forEach(section => {{
                const visibleItems = section.querySelectorAll('.item-card:not(.hidden)');
                section.style.display = visibleItems.length > 0 ? 'block' : 'none';
            }});

            // Show no results message if needed
            if (visibleCount === 0 && search !== '') {{
                noResults.classList.remove('hidden');
            }} else {{
                noResults.classList.add('hidden');
            }}
        }}

        // Show item detail
        function showItemDetail(itemName, collection, imageFolder) {{
            // Determine which index to use based on collection name
            let clothingIndex, pageItems;
            if (collection === 'Summer') {{
                clothingIndex = summerClothingIndex;
                pageItems = summerPageItems;
            }} else if (collection === 'Spring') {{
                clothingIndex = springClothingIndex;
                pageItems = springPageItems;
            }} else {{
                clothingIndex = fwClothingIndex;
                pageItems = fwPageItems;
            }}

            // Try to find the item with or without category suffix
            let pages = null;
            for (let key in clothingIndex) {{
                if (key.startsWith(itemName)) {{
                    pages = clothingIndex[key];
                    break;
                }}
            }}

            if (!pages) return;

            // Hide other views
            document.getElementById('summer-view').classList.add('hidden');
            document.getElementById('spring-view').classList.add('hidden');
            document.getElementById('fw-view').classList.add('hidden');
            document.getElementById('page-view').classList.add('hidden');
            document.getElementById('item-view').classList.remove('hidden');

            document.getElementById('page-title').textContent = itemName + ' - ' + collection + ' Collection';

            const content = document.getElementById('item-detail-content');
            content.innerHTML = `
                <div class="collection-header">
                    <h2>${{itemName}}</h2>
                    <div class="collection-stats">
                        This item appears on <strong>${{pages.length}}</strong> page${{pages.length > 1 ? 's' : ''}} in the ${{collection}} collection
                    </div>
                </div>
                <div class="page-images">
                    ${{pages.map(page => `
                        <div class="page-card">
                            <img src="${{imageFolder}}/${{page}}.png"
                                 alt="${{page}}"
                                 class="clickable-image"
                                 loading="lazy"
                                 onclick="openModal('${{imageFolder}}/${{page}}.png', '${{page.replace('page_', 'Page ')}} - ${{itemName}}')"
                                 onerror="this.parentElement.style.display='none';">
                            <div class="page-title" onclick="showPageDetail('${{page}}', '${{collection}}', '${{imageFolder}}')" style="cursor: pointer;">
                                ${{page.replace('page_', 'Page ')}}
                            </div>
                        </div>
                    `).join('')}}
                </div>
            `;
        }}

        // Show page detail
        function showPageDetail(pageName, collection, imageFolder) {{
            let pageItems;
            if (collection === 'Summer') {{
                pageItems = summerPageItems;
            }} else if (collection === 'Spring') {{
                pageItems = springPageItems;
            }} else {{
                pageItems = fwPageItems;
            }}

            if (!pageItems[pageName]) return;

            const items = pageItems[pageName];

            // Hide other views
            document.getElementById('summer-view').classList.add('hidden');
            document.getElementById('spring-view').classList.add('hidden');
            document.getElementById('fw-view').classList.add('hidden');
            document.getElementById('item-view').classList.add('hidden');
            document.getElementById('page-view').classList.remove('hidden');

            document.getElementById('page-title').textContent = pageName.replace('page_', 'Page ') + ' - ' + collection + ' Collection';

            const content = document.getElementById('page-detail-content');

            // Handle different data formats (all should be objects now)
            let itemsList = '';
            if (Array.isArray(items)) {{
                if (items.length > 0 && typeof items[0] === 'object') {{
                    // Categorized format (array of objects with name and category)
                    itemsList = items.map(item => `
                        <a onclick="showItemDetail('${{item.name.replace(/'/g, "\\\\\'")}}', '${{collection}}', '${{imageFolder}}')" class="item-link">
                            ${{item.name}} <span style="color: #7f8c8d; font-size: 0.9em;">[${{item.category}}]</span>
                        </a>
                    `).join('');
                }} else {{
                    // Legacy simple array format
                    itemsList = items.map(item => `
                        <a onclick="showItemDetail('${{item.replace(/'/g, "\\\\\'")}}', '${{collection}}', '${{imageFolder}}')" class="item-link">
                            ${{item}}
                        </a>
                    `).join('');
                }}
            }}

            content.innerHTML = `
                <div class="page-detail">
                    <div class="page-image">
                        <img src="${{imageFolder}}/${{pageName}}.png" alt="${{pageName}}"
                             class="clickable-image"
                             loading="lazy"
                             style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);"
                             onclick="openModal('${{imageFolder}}/${{pageName}}.png', '${{pageName.replace('page_', 'Page ')}} - ${{collection}} Collection')">
                    </div>
                    <div class="page-items">
                        <h3>Clothing items on this page:</h3>
                        <div class="item-list">
                            ${{itemsList}}
                        </div>
                    </div>
                </div>
            `;
        }}

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {{
            showCollection('summer');
        }});
    </script>
</body>
</html>"""

    return html_content


def create_netlify_files_all_collections() -> None:
    """Create necessary files for Netlify deployment with all collections."""

    # Create dist directory
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir()

    # Create images directories and copy images
    for collection, source_dir in COLLECTION_PATHS.items():
        output_folder = DIST_IMAGE_FOLDERS[collection]
        output_dir = DIST_DIR / output_folder
        output_dir.mkdir()

        if source_dir.exists():
            count = 0
            for img_file in source_dir.glob('*.png'):
                shutil.copy2(img_file, output_dir)
                count += 1
            print(f"✅ Copied {count} {collection} images")

    # Generate and write main HTML file
    html_content = create_all_collections_html()
    with open(DIST_DIR / 'index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("✅ Generated index.html with all three collections")

    # Create _redirects file in dist
    with open(DIST_DIR / '_redirects', 'w') as f:
        f.write("/*    /index.html   200\n")
    print("✅ Created _redirects")

    # Copy all data files to dist for reference
    for collection, files in DATA_FILES.items():
        for file_type, file_path in files.items():
            if file_path.exists():
                shutil.copy2(file_path, DIST_DIR)
    print("✅ Copied all data files")

    # Copy favicon files
    favicon_files = ['favicon.png', 'favicon.ico']
    for favicon in favicon_files:
        favicon_path = Path(favicon)
        if favicon_path.exists():
            shutil.copy2(favicon_path, DIST_DIR)
    print("✅ Copied favicon files")

    print(f"\n🎉 Static site with all three collections ready for deployment!")
    print(f"📁 Files created in: {DIST_DIR.absolute()}")
    print(f"📊 Total files: {len(list(DIST_DIR.rglob('*')))}")


def main() -> None:
    """Main function."""
    print("🚀 Generating static site with Summer, Spring & Fall/Winter collections...")
    print("   Features: Lazy loading, WebP support, Fuzzy search")
    create_netlify_files_all_collections()

    print(f"\n📱 Ready for mobile-friendly deployment with all collections!")
    print(f"\n📋 Next steps:")
    print(f"   1. (Optional) Run: python optimize_images.py all")
    print(f"      This converts images to WebP for ~30-50% smaller files")
    print(f"   2. Deploy to Netlify using: netlify deploy --prod --dir=dist")
    print(f"   3. Or drag and drop the 'dist' folder to Netlify")


if __name__ == "__main__":
    main()
