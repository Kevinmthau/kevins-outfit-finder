#!/usr/bin/env python3
"""
Generate a static version of the outfit finder for Netlify deployment.
"""

import json
import os
import shutil
from pathlib import Path

def load_data():
    """Load clothing data"""
    with open('clothing_index.json', 'r') as f:
        clothing_index = json.load(f)
    with open('page_items.json', 'r') as f:
        page_items = json.load(f)
    return clothing_index, page_items

def categorize_clothing_item(item_name):
    """Categorize clothing items into bottoms, tops, and shoes"""
    item_lower = item_name.lower()
    
    # Bottoms (pants, trousers, shorts, jeans)
    if any(keyword in item_lower for keyword in ['trouser', 'short', 'jean', '5-pocket', 'khaki', 'pant']):
        return 'bottoms'
    
    # Shoes (loafers, espadrilles, sandals)
    elif any(keyword in item_lower for keyword in ['loafer', 'espadrille', 'sandal', 'shoe']):
        return 'shoes'
    
    # Everything else is considered tops (shirts, polos, blazers, sweaters, etc.)
    else:
        return 'tops'

def sort_items_by_category(clothing_index):
    """Sort items by category: bottoms, tops, then shoes"""
    categorized_items = {'bottoms': [], 'tops': [], 'shoes': []}
    
    # Categorize all items
    for item, pages in clothing_index.items():
        category = categorize_clothing_item(item)
        categorized_items[category].append((item, pages))
    
    # Sort each category by frequency (most common first)
    for category in categorized_items:
        categorized_items[category].sort(key=lambda x: len(x[1]), reverse=True)
    
    # Combine in order: bottoms, tops, shoes
    sorted_items = (categorized_items['bottoms'] + 
                   categorized_items['tops'] + 
                   categorized_items['shoes'])
    
    return sorted_items, categorized_items

def create_static_html():
    """Create the main static HTML file"""
    clothing_index, page_items = load_data()
    
    # Sort items by category: bottoms, tops, shoes
    sorted_items, categorized_items = sort_items_by_category(clothing_index)
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kevin's Outfit Finder</title>
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
        .header {{
            background: #2c3e50;
            color: white;
            padding: 20px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2rem;
        }}
        .nav {{
            background: #34495e;
            padding: 10px 20px;
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }}
        .nav button {{
            color: #ecf0f1;
            background: none;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.3s;
        }}
        .nav button:hover, .nav button.active {{
            background-color: #2c3e50;
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
            width: 300px;
            max-width: 100%;
            outline: none;
            transition: border-color 0.3s;
        }}
        .search-box input:focus {{
            border-color: #3498db;
        }}
        .stats {{
            background: #ecf0f1;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 20px;
            text-align: center;
            color: #2c3e50;
        }}
        .item-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .item-card {{
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            transition: all 0.3s ease;
            cursor: pointer;
        }}
        .item-card:hover {{
            background: #e9ecef;
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
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
        .category-section {{
            margin-bottom: 40px;
        }}
        .category-header {{
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #e9ecef;
        }}
        .category-header h2 {{
            margin: 0 0 8px 0;
            font-size: 1.5rem;
            color: #2c3e50;
        }}
        .category-description {{
            margin: 0;
            color: #7f8c8d;
            font-size: 0.95rem;
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
            color: #3498db;
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
        }}
        .item-link:hover {{
            background: #e9ecef;
            transform: translateX(5px);
        }}
        @media (max-width: 768px) {{
            .container {{
                margin: 10px;
                border-radius: 4px;
            }}
            .header {{
                padding: 15px;
            }}
            .header h1 {{
                font-size: 1.5rem;
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
        <div class="header">
            <h1 id="page-title">Kevin's Outfit Finder</h1>
        </div>
        <div class="nav">
            <button onclick="showAllItems()" class="active" id="nav-all">All Items</button>
            <button onclick="showHome()" id="nav-home">Home</button>
        </div>
        <div class="content">
            <!-- Home View -->
            <div id="home-view">
                <div class="stats">
                    <strong>{len(clothing_index)}</strong> unique clothing items across <strong>{len(page_items)}</strong> outfit pages
                </div>

                <div class="search-box">
                    <input type="text" id="searchInput" placeholder="Search for clothing items..." onkeyup="filterItems()">
                </div>

                <div id="items-grid">
                    {generate_categorized_item_cards(categorized_items)}
                </div>
            </div>

            <!-- Item Detail View -->
            <div id="item-view" class="hidden">
                <a onclick="showAllItems()" class="back-link">&larr; Back to all items</a>
                <div id="item-detail-content"></div>
            </div>

            <!-- Page Detail View -->
            <div id="page-view" class="hidden">
                <a onclick="showAllItems()" class="back-link">&larr; Back to all items</a>
                <div id="page-detail-content"></div>
            </div>
        </div>
    </div>

    <script>
        // Data
        const clothingIndex = {json.dumps(clothing_index)};
        const pageItems = {json.dumps(page_items)};

        // Navigation
        function showAllItems() {{
            document.getElementById('home-view').classList.remove('hidden');
            document.getElementById('item-view').classList.add('hidden');
            document.getElementById('page-view').classList.add('hidden');
            document.getElementById('page-title').textContent = "Kevin's Outfit Finder";
            updateNavigation('nav-all');
        }}

        function showHome() {{
            showAllItems();
            updateNavigation('nav-home');
        }}

        function updateNavigation(activeId) {{
            document.querySelectorAll('.nav button').forEach(btn => btn.classList.remove('active'));
            document.getElementById(activeId).classList.add('active');
        }}

        // Search functionality
        function filterItems() {{
            const search = document.getElementById('searchInput').value.toLowerCase();
            const items = document.querySelectorAll('.item-card');
            
            items.forEach(item => {{
                const itemName = item.querySelector('.item-name').textContent.toLowerCase();
                item.style.display = itemName.includes(search) ? 'block' : 'none';
            }});
        }}

        // Show item detail
        function showItemDetail(itemName) {{
            if (!clothingIndex[itemName]) return;
            
            const pages = clothingIndex[itemName];
            document.getElementById('home-view').classList.add('hidden');
            document.getElementById('page-view').classList.add('hidden');
            document.getElementById('item-view').classList.remove('hidden');
            document.getElementById('page-title').textContent = itemName;
            
            const content = document.getElementById('item-detail-content');
            content.innerHTML = `
                <div class="stats">
                    This item appears on <strong>${{pages.length}}</strong> page${{pages.length > 1 ? 's' : ''}}
                </div>
                <div class="page-images">
                    ${{pages.map(page => `
                        <div class="page-card" onclick="showPageDetail('${{page}}')">
                            <img src="images/${{page}}.png" alt="${{page}}" onerror="this.style.display='none';">
                            <div class="page-title">${{page.replace('page_', 'Page ')}}</div>
                        </div>
                    `).join('')}}
                </div>
            `;
        }}

        // Show page detail
        function showPageDetail(pageName) {{
            if (!pageItems[pageName]) return;
            
            const items = pageItems[pageName];
            document.getElementById('home-view').classList.add('hidden');
            document.getElementById('item-view').classList.add('hidden');
            document.getElementById('page-view').classList.remove('hidden');
            document.getElementById('page-title').textContent = pageName.replace('page_', 'Page ');
            
            const content = document.getElementById('page-detail-content');
            content.innerHTML = `
                <div class="page-detail">
                    <div class="page-image">
                        <img src="images/${{pageName}}.png" alt="${{pageName}}" 
                             style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);"
                             onerror="this.style.display='none';">
                    </div>
                    <div class="page-items">
                        <h3>Clothing items on this page:</h3>
                        <div class="item-list">
                            ${{items.map(item => `
                                <a onclick="showItemDetail('${{item.replace(/'/g, "\\\'")}}')" class="item-link">
                                    ${{item}}
                                </a>
                            `).join('')}}
                        </div>
                    </div>
                </div>
            `;
        }}

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {{
            showAllItems();
        }});
    </script>
</body>
</html>"""

    return html_content

def generate_categorized_item_cards(categorized_items):
    """Generate HTML for categorized item cards"""
    html_sections = []
    
    # Category information
    categories = {
        'bottoms': {'title': '👖 Bottoms', 'description': 'Trousers, shorts, and pants'},
        'tops': {'title': '👔 Tops', 'description': 'Shirts, polos, blazers, and sweaters'},
        'shoes': {'title': '👞 Shoes', 'description': 'Loafers, espadrilles, and sandals'}
    }
    
    for category in ['bottoms', 'tops', 'shoes']:
        items = categorized_items[category]
        if not items:
            continue
            
        category_info = categories[category]
        
        # Category header
        category_html = f"""
                <div class="category-section">
                    <div class="category-header">
                        <h2>{category_info['title']}</h2>
                        <p class="category-description">{category_info['description']} ({len(items)} items)</p>
                    </div>
                    <div class="item-grid">"""
        
        # Generate cards for this category
        for item, pages in items:
            escaped_item = item.replace("'", "\\'")
            card = f"""
                        <div class="item-card" onclick="showItemDetail('{escaped_item}')">
                            <div class="item-name">{item}</div>
                            <div class="item-count">
                                Appears on {len(pages)} page{'s' if len(pages) > 1 else ''}
                            </div>
                        </div>"""
            category_html += card
        
        category_html += """
                    </div>
                </div>"""
        
        html_sections.append(category_html)
    
    return ''.join(html_sections)

def create_netlify_files():
    """Create necessary files for Netlify deployment"""
    
    # Create dist directory
    dist_dir = Path('dist')
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir()
    
    # Create images directory and copy images
    images_dir = dist_dir / 'images'
    images_dir.mkdir()
    
    source_images = Path('Kevin_Summer_Looks_Pages')
    if source_images.exists():
        for img_file in source_images.glob('*.png'):
            shutil.copy2(img_file, images_dir)
        print(f"✅ Copied {len(list(source_images.glob('*.png')))} images")
    
    # Generate and write main HTML file
    html_content = create_static_html()
    with open(dist_dir / 'index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("✅ Generated index.html")
    
    # Create netlify.toml for configuration
    netlify_config = """[build]
  publish = "dist"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
"""
    with open('netlify.toml', 'w') as f:
        f.write(netlify_config)
    print("✅ Created netlify.toml")
    
    # Create _redirects file in dist
    with open(dist_dir / '_redirects', 'w') as f:
        f.write("/*    /index.html   200\n")
    print("✅ Created _redirects")
    
    # Copy data files to dist for reference
    shutil.copy2('clothing_index.json', dist_dir)
    shutil.copy2('page_items.json', dist_dir)
    print("✅ Copied data files")
    
    print(f"\n🎉 Static site ready for deployment!")
    print(f"📁 Files created in: {dist_dir.absolute()}")
    print(f"📊 Total files: {len(list(dist_dir.rglob('*')))}")

def main():
    """Main function"""
    print("🚀 Generating static site for Netlify deployment...")
    create_netlify_files()
    
    print(f"\n📱 Ready for mobile-friendly deployment!")
    print(f"📋 Next steps:")
    print(f"   1. Create a new site on Netlify")
    print(f"   2. Drag and drop the 'dist' folder to Netlify")
    print(f"   3. Your outfit finder will be live!")

if __name__ == "__main__":
    main()