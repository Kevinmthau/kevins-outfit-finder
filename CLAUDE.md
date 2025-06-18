# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Kevin's Outfit Finder is a mobile-first web application for browsing and discovering clothing combinations from a curated summer wardrobe collection. The project uses OCR to extract clothing items from outfit images and provides a visual discovery interface optimized for mobile devices.

## Architecture

### Dual Development Approach
- **Development Mode**: Flask web application (`app.py`) for local development and testing
- **Production Mode**: Static site generation (`generate_static_site.py`) for Netlify deployment

### Data Architecture
The application uses a dual-index system with two core JSON files:
- `clothing_index.json`: Maps clothing items → pages where they appear
- `page_items.json`: Maps outfit pages → clothing items they contain

This bidirectional mapping enables efficient lookups for both "show me all outfits with this item" and "show me all items on this page" queries.

### OCR Processing Pipeline
1. **Raw extraction**: `extract_clothing_items.py` uses Tesseract OCR on images in `Kevin_Summer_Looks_Pages/`
2. **Manual curation**: `page_items.json` is manually edited for accuracy
3. **Index rebuilding**: `rebuild_index.py` regenerates `clothing_index.json` from curated page data

## Essential Commands

### Local Development
```bash
# Start Flask development server
python3 app.py
# Visit http://localhost:5000

# Start data cleaning web interface
python3 data_cleaner.py
# Visit http://localhost:5001/clean
```

### Data Processing
```bash
# Extract clothing items from images using OCR
export PATH="/opt/homebrew/bin:$PATH"  # Ensure Tesseract is available
python3 extract_clothing_items.py

# Rebuild clothing index after manual edits to page_items.json
python3 rebuild_index.py

# Analyze data for cleaning opportunities
python3 analyze_data.py
```

### Static Site Generation
```bash
# Generate static site for deployment
python3 generate_static_site.py
# Output created in dist/ directory

# Test static site locally
cd dist && python3 -m http.server 8080
```

### Data Management Workflow
When updating clothing data:
1. Edit `page_items.json` manually for accuracy
2. Run `python3 rebuild_index.py` to regenerate clothing_index.json
3. Run `python3 generate_static_site.py` to update static site
4. Commit and push for automatic Netlify deployment

## Key Technical Details

### OCR Configuration
- Tesseract path set to `/opt/homebrew/bin/tesseract` for macOS Homebrew installations
- OCR parsing logic in `extract_clothing_items.py` handles multi-line brand names and item descriptions
- Manual data curation recommended for production accuracy

### Static Site Generation
- `generate_static_site.py` creates a complete SPA in the `dist/` directory
- Embeds JSON data directly into HTML for offline functionality
- Copies all images from `Kevin_Summer_Looks_Pages/` to `dist/images/`
- Mobile-first responsive design with touch-friendly interface

### Flask Routes Architecture
- `/`: Main item directory sorted by frequency
- `/item/<item_name>`: Show all outfit pages containing specific item
- `/page/<page_name>`: Show all items on specific outfit page
- `/images/<filename>`: Serve outfit images
- `/api/search/<query>`: JSON search endpoint

### Deployment Configuration
- Netlify builds using `python3 generate_static_site.py`
- Python 3.9 runtime specified in `netlify.toml`
- SPA routing handled via `_redirects` file

## Data Structure Notes

### Image Naming Convention
- Outfit images: `page_1.png`, `page_2.png`, ..., `page_90.png`
- Stored in `Kevin_Summer_Looks_Pages/` directory
- Copied to `dist/images/` during static site generation

### JSON Data Format
- Page identifiers use format: `"page_1"`, `"page_2"`, etc.
- Item names include full brand and description: `"Saint Laurent ivory trouser"`
- Pages arrays are sorted numerically by page number

### Mobile Optimization Strategy
- CSS Grid/Flexbox for responsive layouts
- Touch-friendly minimum 44px tap targets
- Optimized image loading with error fallbacks
- Single-page application for smooth mobile navigation