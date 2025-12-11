#!/usr/bin/env python3
"""
Web interface to categorize Fall/Winter pages into separate Fall and Winter collections.
Run this script and visit http://localhost:5002 to categorize pages.
"""

import json
from flask import Flask, render_template_string, request, jsonify
from pathlib import Path

app = Flask(__name__)

BASE_DIR = Path(__file__).parent
PAGE_SEASONS_FILE = BASE_DIR / "page_seasons_fw.json"
PAGE_ITEMS_FILE = BASE_DIR / "page_items_fw.json"
IMAGES_DIR = BASE_DIR / "Fall_Winter_Looks_Images"

def load_page_seasons():
    if PAGE_SEASONS_FILE.exists():
        with open(PAGE_SEASONS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_page_seasons(data):
    with open(PAGE_SEASONS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_all_pages():
    """Get all page names from page_items_fw.json"""
    if PAGE_ITEMS_FILE.exists():
        with open(PAGE_ITEMS_FILE, 'r') as f:
            data = json.load(f)
            return sorted(data.keys(), key=lambda x: int(x.replace('page_', '')))
    return []

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Categorize Fall/Winter Pages</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 12px;
            background: #f5f5f5;
        }
        .header {
            background: #2c3e50;
            color: white;
            padding: 16px;
            margin: -12px -12px 16px -12px;
            text-align: center;
        }
        .header h1 { margin: 0 0 8px 0; font-size: 1.4rem; }
        .stats {
            display: flex;
            justify-content: center;
            gap: 20px;
            font-size: 0.9rem;
        }
        .stat { padding: 4px 12px; background: rgba(255,255,255,0.1); border-radius: 4px; }
        .filters {
            display: flex;
            gap: 8px;
            margin-bottom: 16px;
            flex-wrap: wrap;
        }
        .filter-btn {
            padding: 8px 16px;
            border: none;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.9rem;
            transition: all 0.2s;
        }
        .filter-btn.active { background: #3498db; color: white; }
        .filter-btn:not(.active) { background: #ddd; }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 12px;
        }
        .card {
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .card img {
            width: 100%;
            height: auto;
            display: block;
        }
        .card-footer {
            padding: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .page-name { font-weight: 600; color: #2c3e50; }
        .btn-group { display: flex; gap: 6px; }
        .season-btn {
            padding: 6px 14px;
            border: 2px solid #ddd;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.85rem;
            background: white;
            transition: all 0.2s;
        }
        .season-btn:hover { border-color: #aaa; }
        .season-btn.fall.selected { background: #e67e22; color: white; border-color: #e67e22; }
        .season-btn.winter.selected { background: #3498db; color: white; border-color: #3498db; }
        .card.categorized-fall { border-left: 4px solid #e67e22; }
        .card.categorized-winter { border-left: 4px solid #3498db; }
        .hidden { display: none; }
        .save-indicator {
            position: fixed;
            bottom: 20px;
            right: 20px;
            padding: 12px 20px;
            background: #27ae60;
            color: white;
            border-radius: 8px;
            opacity: 0;
            transition: opacity 0.3s;
        }
        .save-indicator.show { opacity: 1; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Categorize Fall/Winter Pages</h1>
        <div class="stats">
            <span class="stat">🍂 Fall: <span id="fall-count">0</span></span>
            <span class="stat">❄️ Winter: <span id="winter-count">0</span></span>
            <span class="stat">❓ Uncategorized: <span id="uncat-count">0</span></span>
        </div>
    </div>

    <div class="filters">
        <button class="filter-btn active" onclick="filterPages('all')">All</button>
        <button class="filter-btn" onclick="filterPages('uncategorized')">Uncategorized</button>
        <button class="filter-btn" onclick="filterPages('fall')">Fall</button>
        <button class="filter-btn" onclick="filterPages('winter')">Winter</button>
    </div>

    <div class="grid" id="grid"></div>

    <div class="save-indicator" id="save-indicator">Saved!</div>

    <script>
        let pageSeasons = {{ page_seasons | tojson }};
        const allPages = {{ pages | tojson }};
        let currentFilter = 'all';

        function updateStats() {
            let fall = 0, winter = 0, uncat = 0;
            allPages.forEach(page => {
                if (pageSeasons[page] === 'fall') fall++;
                else if (pageSeasons[page] === 'winter') winter++;
                else uncat++;
            });
            document.getElementById('fall-count').textContent = fall;
            document.getElementById('winter-count').textContent = winter;
            document.getElementById('uncat-count').textContent = uncat;
        }

        function renderGrid() {
            const grid = document.getElementById('grid');
            grid.innerHTML = allPages.map(page => {
                const season = pageSeasons[page] || '';
                const cardClass = season ? `categorized-${season}` : '';
                const pageNum = page.replace('page_', 'Page ');
                return `
                    <div class="card ${cardClass}" data-page="${page}" data-season="${season}">
                        <img src="/image/${page}" alt="${page}" loading="lazy">
                        <div class="card-footer">
                            <span class="page-name">${pageNum}</span>
                            <div class="btn-group">
                                <button class="season-btn fall ${season === 'fall' ? 'selected' : ''}"
                                        onclick="setSeason('${page}', 'fall')">🍂 Fall</button>
                                <button class="season-btn winter ${season === 'winter' ? 'selected' : ''}"
                                        onclick="setSeason('${page}', 'winter')">❄️ Winter</button>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
            applyFilter();
        }

        function applyFilter() {
            const cards = document.querySelectorAll('.card');
            cards.forEach(card => {
                const season = card.dataset.season;
                let show = false;
                if (currentFilter === 'all') show = true;
                else if (currentFilter === 'uncategorized') show = !season;
                else show = season === currentFilter;
                card.classList.toggle('hidden', !show);
            });
        }

        function filterPages(filter) {
            currentFilter = filter;
            document.querySelectorAll('.filter-btn').forEach(btn => {
                btn.classList.toggle('active', btn.textContent.toLowerCase().includes(filter) ||
                    (filter === 'all' && btn.textContent === 'All') ||
                    (filter === 'uncategorized' && btn.textContent === 'Uncategorized'));
            });
            applyFilter();
        }

        async function setSeason(page, season) {
            // Toggle off if already selected
            if (pageSeasons[page] === season) {
                delete pageSeasons[page];
            } else {
                pageSeasons[page] = season;
            }

            // Update UI
            const card = document.querySelector(`[data-page="${page}"]`);
            const newSeason = pageSeasons[page] || '';
            card.dataset.season = newSeason;
            card.className = `card ${newSeason ? `categorized-${newSeason}` : ''}`;
            card.querySelectorAll('.season-btn').forEach(btn => {
                btn.classList.toggle('selected', btn.classList.contains(newSeason));
            });

            updateStats();
            applyFilter();

            // Save to server
            const response = await fetch('/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ page, season: newSeason })
            });

            if (response.ok) {
                const indicator = document.getElementById('save-indicator');
                indicator.classList.add('show');
                setTimeout(() => indicator.classList.remove('show'), 1000);
            }
        }

        renderGrid();
        updateStats();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    pages = get_all_pages()
    page_seasons = load_page_seasons()
    return render_template_string(HTML_TEMPLATE, pages=pages, page_seasons=page_seasons)

@app.route('/image/<page>')
def get_image(page):
    from flask import send_file
    image_path = IMAGES_DIR / f"{page}.png"
    if image_path.exists():
        return send_file(image_path, mimetype='image/png')
    return "Not found", 404

@app.route('/save', methods=['POST'])
def save():
    data = request.json
    page = data.get('page')
    season = data.get('season')

    page_seasons = load_page_seasons()
    if season:
        page_seasons[page] = season
    elif page in page_seasons:
        del page_seasons[page]

    save_page_seasons(page_seasons)
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    print("🍂❄️ Fall/Winter Page Categorizer")
    print("   Visit http://localhost:5002 to categorize pages")
    print("   Press Ctrl+C to stop")
    app.run(port=5002, debug=True)
