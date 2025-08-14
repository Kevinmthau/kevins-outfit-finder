# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Kevin's Outfit Finder is a mobile-first web application for browsing and discovering clothing combinations from curated wardrobe collections (Summer and Spring). The project uses OCR to extract clothing items from outfit images and provides a visual discovery interface with image modal/lightbox functionality.

## Architecture

### Dual Development Approach
- **Development Mode**: Flask web application (`app.py`) for local development and testing
- **Production Mode**: Static site generation (`generate_static_site_with_collections.py`) for Netlify deployment

### Data Architecture
The application maintains separate datasets for each collection:

**Summer Collection:**
- `clothing_index.json`: Maps clothing items → pages where they appear
- `page_items.json`: Maps outfit pages → clothing items they contain
- Images in `Kevin_Summer_Looks_Pages/` (90 pages)

**Spring Collection:**
- `clothing_index_spring.json`: Categorized items with format "Item Name (Category)"
- `page_items_spring.json`: Includes category metadata for each item
- `category_stats_spring.json`: Category statistics
- Images in `KEVIN_Spring_Looks_Images/` (109 pages)

## Essential Commands

### Local Development
```bash
# Start Flask development server (Summer collection only)
python3 app.py
# Visit http://localhost:5000

# Start data cleaning web interface
python3 data_cleaner.py
# Visit http://localhost:5001/clean

# Test static site locally
cd dist && python3 -m http.server 8080
# Visit http://localhost:8080
```

### OCR Processing
```bash
# Extract Summer collection items
export PATH="/opt/homebrew/bin:$PATH"  # Ensure Tesseract is available
python3 extract_clothing_items.py

# Extract Spring collection with improved separation and categorization
python3 extract_spring_clothing_improved.py

# Clean OCR artifacts (e.g., "i The Row" → "The Row")
python3 clean_ocr_artifacts.py

# Merge duplicate items across collections
python3 merge_duplicates.py
```

### Data Management
```bash
# Rebuild clothing index after manual edits to page_items.json
python3 rebuild_index.py

# Analyze data for cleaning opportunities
python3 analyze_data.py

# Clean data directly with interactive prompts
python3 clean_data_directly.py
```

### Static Site Generation
```bash
# Generate static site with both collections (PREFERRED)
python3 generate_static_site_with_collections.py

# Legacy: Generate Summer-only site
python3 generate_static_site.py
```

### Deployment
```bash
# After generating static site
netlify deploy --prod --dir=dist

# Or drag and drop the 'dist' folder to Netlify web interface
```

## Key Technical Details

### OCR Configuration
- Tesseract path: `/opt/homebrew/bin/tesseract` (macOS Homebrew)
- Spring extraction (`extract_spring_clothing_improved.py`) includes:
  - Automatic item separation for combined entries
  - Category detection (Outerwear, Tops, Bottoms, Footwear, Accessories)
  - Brand recognition for 30+ luxury brands
  - Artifact cleaning (removes OCR noise like leading characters)

### Static Site Features
- **Dual Collection Support**: Tab-based navigation between Summer/Spring
- **Image Modal**: Click any outfit image for full-screen lightbox view
- **Categorized Display**: Items grouped by type (Bottoms, Tops, Footwear, etc.)
- **Search**: Real-time filtering within each collection
- **Mobile Optimized**: Touch-friendly with responsive grid layouts

### Data Cleaning Workflow
1. Run OCR extraction: `python3 extract_spring_clothing_improved.py`
2. Clean artifacts: `python3 clean_ocr_artifacts.py`
3. Manual review: Edit `page_items_spring.json` if needed
4. Rebuild index: `python3 rebuild_index.py`
5. Generate site: `python3 generate_static_site_with_collections.py`

## Data Structure Notes

### Image Naming Convention
- Summer: `Kevin_Summer_Looks_Pages/page_1.png` through `page_90.png`
- Spring: `KEVIN_Spring_Looks_Images/page_1.png` through `page_109.png`
- Static site copies to: `dist/images/` and `dist/spring_images/`

### Spring Collection Categories
- **Outerwear**: jackets, coats, blazers, trenches
- **Tops**: shirts, polos, sweaters, cardigans, hoodies
- **Bottoms**: trousers, jeans, shorts, corduroys
- **Footwear**: loafers, boots, slippers, sneakers
- **Accessories**: belts, watches, sunglasses
- **Other**: items that don't fit standard categories

### JSON Data Format
**Summer format (simple):**
```json
{
  "page_1": ["Saint Laurent ivory trouser", "The Row brown tassel loafer"]
}
```

**Spring format (categorized):**
```json
{
  "page_1": [
    {"name": "Saint Laurent blush sweater", "category": "Tops"},
    {"name": "The Row brown tassel loafer", "category": "Footwear"}
  ]
}
```

## Common Issues and Solutions

### OCR Artifacts
- Problem: Items like "i The Row brown tassel loafer" or "eS) Saint Laurent loafer"
- Solution: Run `python3 clean_ocr_artifacts.py` to automatically clean

### Combined Items
- Problem: "Caruso camel blazer Drake's ivory corduroy" as single item
- Solution: Use `extract_spring_clothing_improved.py` which automatically separates

### Duplicate Items
- Problem: "Loro Piana sandal" and "Loro piana sandal" (capitalization)
- Solution: Run `python3 merge_duplicates.py` to consolidate

## Testing Checklist
When making changes, verify:
1. Images display correctly in both collections
2. Modal/lightbox opens on image click
3. Search filters work within each collection
4. Category groupings display properly (Spring)
5. Navigation between items and pages works
6. Mobile responsive layout functions