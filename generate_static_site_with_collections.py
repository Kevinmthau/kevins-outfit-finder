#!/usr/bin/env python3
"""
Generate a static version of the outfit finder with both Summer and Spring collections.
"""

import json
import os
import shutil
from pathlib import Path

def load_collection_data(collection):
    """Load clothing data for a specific collection"""
    if collection == 'summer':
        with open('clothing_index.json', 'r') as f:
            clothing_index = json.load(f)
        with open('page_items.json', 'r') as f:
            page_items = json.load(f)
    elif collection == 'spring':
        with open('clothing_index_spring.json', 'r') as f:
            clothing_index = json.load(f)
        with open('page_items_spring.json', 'r') as f:
            page_items = json.load(f)
        # Load category stats for Spring
        with open('category_stats_spring.json', 'r') as f:
            category_stats = json.load(f)
        return clothing_index, page_items, category_stats
    
    return clothing_index, page_items, None

def categorize_by_spring_categories(clothing_index):
    """Categorize items using Spring category data from the item names"""
    categorized = {
        'Outerwear': [],
        'Tops': [],
        'Bottoms': [],
        'Footwear': [],
        'Accessories': [],
        'Other': []
    }
    
    for item, pages in clothing_index.items():
        # Extract category from item name if it's in format "Item Name (Category)"
        if '(' in item and ')' in item:
            category = item[item.rfind('(')+1:item.rfind(')')]
            item_name = item[:item.rfind('(')].strip()
            if category in categorized:
                categorized[category].append((item_name, pages, category))
            else:
                categorized['Other'].append((item_name, pages, 'Other'))
        else:
            # Fallback categorization for items without explicit category
            categorized['Other'].append((item, pages, 'Other'))
    
    # Sort each category by frequency
    for category in categorized:
        categorized[category].sort(key=lambda x: len(x[1]), reverse=True)
    
    return categorized

def categorize_summer_items(clothing_index):
    """Categorize Summer items into standard categories"""
    categorized = {
        'Bottoms': [],
        'Tops': [],
        'Footwear': [],
        'Accessories': []
    }
    
    for item, pages in clothing_index.items():
        item_lower = item.lower()
        
        # Categorize based on keywords
        if any(keyword in item_lower for keyword in ['trouser', 'short', 'jean', '5-pocket', 'khaki', 'pant']):
            categorized['Bottoms'].append((item, pages, 'Bottoms'))
        elif any(keyword in item_lower for keyword in ['loafer', 'espadrille', 'sandal', 'shoe']):
            categorized['Footwear'].append((item, pages, 'Footwear'))
        else:
            # Everything else is tops for Summer collection
            categorized['Tops'].append((item, pages, 'Tops'))
    
    # Sort each category by frequency
    for category in categorized:
        categorized[category].sort(key=lambda x: len(x[1]), reverse=True)
    
    return categorized

def generate_collection_html(collection_name, clothing_index, page_items, image_folder):
    """Generate HTML for a specific collection"""
    
    # Categorize items based on collection
    if collection_name == 'Spring':
        categorized_items = categorize_by_spring_categories(clothing_index)
        category_order = ['Outerwear', 'Tops', 'Bottoms', 'Footwear', 'Accessories', 'Other']
    else:  # Summer
        categorized_items = categorize_summer_items(clothing_index)
        category_order = ['Bottoms', 'Tops', 'Footwear', 'Accessories']
    
    # Generate category sections
    category_sections = []
    for category in category_order:
        if category not in categorized_items or not categorized_items[category]:
            continue
        
        items = categorized_items[category]
        
        # Category icon mapping
        category_icons = {
            'Outerwear': '🧥',
            'Tops': '👔',
            'Bottoms': '👖',
            'Footwear': '👞',
            'Accessories': '🎩',
            'Other': '📦'
        }
        
        icon = category_icons.get(category, '📦')
        
        section_html = f"""
                    <div class="category-section">
                        <div class="category-header">
                            <h2>{icon} {category}</h2>
                            <p class="category-description">{len(items)} items in this category</p>
                        </div>
                        <div class="item-grid">"""
        
        for item_name, pages, _ in items:
            escaped_item = item_name.replace("'", "\\'")
            full_item = f"{item_name}|{collection_name}"  # Add collection identifier
            section_html += f"""
                            <div class="item-card" onclick="showItemDetail('{escaped_item}', '{collection_name}', '{image_folder}')">
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

def create_combined_static_html():
    """Create the main static HTML file with both collections"""
    
    # Load both collections
    summer_index, summer_items, _ = load_collection_data('summer')
    spring_index, spring_items, spring_stats = load_collection_data('spring')
    
    # Generate HTML for each collection
    summer_html = generate_collection_html('Summer', summer_index, summer_items, 'images')
    spring_html = generate_collection_html('Spring', spring_index, spring_items, 'spring_images')
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kevin's Outfit Finder - Summer & Spring Collections</title>
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
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px 20px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.95;
            font-size: 1.1rem;
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
            padding: 15px 30px;
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
        .collection-header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 8px;
        }}
        .collection-header h2 {{
            margin: 0 0 10px 0;
            color: #2c3e50;
            font-size: 2rem;
        }}
        .collection-stats {{
            color: #5a6c7d;
            font-size: 1.1rem;
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
                padding: 12px 20px;
                font-size: 0.95rem;
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
            <p>Explore Summer & Spring Collections</p>
        </div>
        <div class="nav">
            <button onclick="showCollection('summer')" class="active" id="nav-summer">☀️ Summer Collection</button>
            <button onclick="showCollection('spring')" id="nav-spring">🌸 Spring Collection</button>
        </div>
        <div class="content">
            <!-- Summer Collection View -->
            <div id="summer-view">
                <div class="collection-header">
                    <h2>☀️ Summer Collection</h2>
                    <div class="collection-stats">
                        <strong>{len(summer_index)}</strong> unique items across <strong>{len(summer_items)}</strong> outfit pages
                    </div>
                </div>

                <div class="search-box">
                    <input type="text" id="summerSearchInput" placeholder="Search summer items..." onkeyup="filterItems('summer')">
                </div>

                <div id="summer-items-grid">
                    {summer_html}
                </div>
            </div>

            <!-- Spring Collection View -->
            <div id="spring-view" class="hidden">
                <div class="collection-header">
                    <h2>🌸 Spring Collection</h2>
                    <div class="collection-stats">
                        <strong>{len(spring_index)}</strong> unique items across <strong>{len(spring_items)}</strong> outfit pages
                    </div>
                </div>

                <div class="search-box">
                    <input type="text" id="springSearchInput" placeholder="Search spring items..." onkeyup="filterItems('spring')">
                </div>

                <div id="spring-items-grid">
                    {spring_html}
                </div>
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
        
        let currentCollection = 'summer';
        let currentClothingIndex = summerClothingIndex;
        let currentPageItems = summerPageItems;

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
            }} else {{
                currentClothingIndex = springClothingIndex;
                currentPageItems = springPageItems;
            }}
        }}

        function backToCollection() {{
            showCollection(currentCollection);
        }}

        // Search functionality
        function filterItems(collection) {{
            const search = document.getElementById(collection + 'SearchInput').value.toLowerCase();
            const container = document.getElementById(collection + '-items-grid');
            const items = container.querySelectorAll('.item-card');
            
            items.forEach(item => {{
                const itemName = item.querySelector('.item-name').textContent.toLowerCase();
                item.style.display = itemName.includes(search) ? 'block' : 'none';
            }});
        }}

        // Show item detail
        function showItemDetail(itemName, collection, imageFolder) {{
            // Find the item in the correct index
            let clothingIndex = collection === 'Summer' ? summerClothingIndex : springClothingIndex;
            let pageItems = collection === 'Summer' ? summerPageItems : springPageItems;
            
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
                                 onclick="openModal('${{imageFolder}}/${{page}}.png', '${{page.replace('page_', 'Page ')}} - ${{itemName}}')"
                                 onerror="this.style.display='none';">
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
            let pageItems = collection === 'Summer' ? summerPageItems : springPageItems;
            
            if (!pageItems[pageName]) return;
            
            const items = pageItems[pageName];
            
            // Hide other views
            document.getElementById('summer-view').classList.add('hidden');
            document.getElementById('spring-view').classList.add('hidden');
            document.getElementById('item-view').classList.add('hidden');
            document.getElementById('page-view').classList.remove('hidden');
            
            document.getElementById('page-title').textContent = pageName.replace('page_', 'Page ') + ' - ' + collection + ' Collection';
            
            const content = document.getElementById('page-detail-content');
            
            // Handle different data formats
            let itemsList = '';
            if (Array.isArray(items)) {{
                // Summer format (simple array)
                itemsList = items.map(item => `
                    <a onclick="showItemDetail('${{item.replace(/'/g, "\\\'")}}', '${{collection}}', '${{imageFolder}}')" class="item-link">
                        ${{item}}
                    </a>
                `).join('');
            }} else if (items && items.length > 0 && typeof items[0] === 'object') {{
                // Spring format (array of objects with name and category)
                itemsList = items.map(item => `
                    <a onclick="showItemDetail('${{item.name.replace(/'/g, "\\\'")}}', '${{collection}}', '${{imageFolder}}')" class="item-link">
                        ${{item.name}} <span style="color: #7f8c8d; font-size: 0.9em;">[${{item.category}}]</span>
                    </a>
                `).join('');
            }}
            
            content.innerHTML = `
                <div class="page-detail">
                    <div class="page-image">
                        <img src="${{imageFolder}}/${{pageName}}.png" alt="${{pageName}}" 
                             class="clickable-image"
                             style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);"
                             onclick="openModal('${{imageFolder}}/${{pageName}}.png', '${{pageName.replace('page_', 'Page ')}} - ${{collection}} Collection')"
                             onerror="this.style.display='none';">
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

def create_netlify_files_with_collections():
    """Create necessary files for Netlify deployment with both collections"""
    
    # Create dist directory
    dist_dir = Path('dist')
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir()
    
    # Create images directories and copy images
    summer_images_dir = dist_dir / 'images'
    summer_images_dir.mkdir()
    
    spring_images_dir = dist_dir / 'spring_images'
    spring_images_dir.mkdir()
    
    # Copy Summer images
    summer_source = Path('Kevin_Summer_Looks_Pages')
    if summer_source.exists():
        for img_file in summer_source.glob('*.png'):
            shutil.copy2(img_file, summer_images_dir)
        print(f"✅ Copied {len(list(summer_source.glob('*.png')))} Summer images")
    
    # Copy Spring images
    spring_source = Path('KEVIN_Spring_Looks_Images')
    if spring_source.exists():
        for img_file in spring_source.glob('*.png'):
            shutil.copy2(img_file, spring_images_dir)
        print(f"✅ Copied {len(list(spring_source.glob('*.png')))} Spring images")
    
    # Generate and write main HTML file
    html_content = create_combined_static_html()
    with open(dist_dir / 'index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("✅ Generated index.html with both collections")
    
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
    
    # Copy all data files to dist for reference
    data_files = [
        'clothing_index.json', 'page_items.json',
        'clothing_index_spring.json', 'page_items_spring.json',
        'category_stats_spring.json'
    ]
    
    for data_file in data_files:
        if Path(data_file).exists():
            shutil.copy2(data_file, dist_dir)
    
    print("✅ Copied all data files")
    
    print(f"\n🎉 Static site with both collections ready for deployment!")
    print(f"📁 Files created in: {dist_dir.absolute()}")
    print(f"📊 Total files: {len(list(dist_dir.rglob('*')))}")

def main():
    """Main function"""
    print("🚀 Generating static site with Summer & Spring collections...")
    create_netlify_files_with_collections()
    
    print(f"\n📱 Ready for mobile-friendly deployment with both collections!")
    print(f"📋 Next steps:")
    print(f"   1. Deploy to Netlify using: netlify deploy --prod --dir=dist")
    print(f"   2. Or drag and drop the 'dist' folder to Netlify")
    print(f"   3. Your outfit finder with both collections will be live!")

if __name__ == "__main__":
    main()