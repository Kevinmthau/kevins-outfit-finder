# 👔 Kevin's Outfit Finder

A mobile-friendly web application to browse and discover clothing combinations from Kevin's summer wardrobe collection.

## 🌟 Features

- **Browse 76 unique clothing items** organized by popularity
- **Search functionality** to quickly find specific items
- **Visual outfit browser** with 90+ outfit images
- **Item-based discovery** - click any item to see all outfits featuring it
- **Mobile-optimized** responsive design
- **Fast and lightweight** static site deployment

## 📱 Live Demo

Visit the deployed site: [Your Netlify URL will go here]

## 🚀 Quick Start

### Local Development
```bash
# Start the Flask development server
python3 app.py
# Visit http://localhost:5000
```

### Static Site Generation
```bash
# Generate static files for deployment
python3 generate_static_site.py
# Files will be created in the 'dist' directory
```

## 📊 Data Overview

- **76 clothing items** from luxury brands (Saint Laurent, Boglioli, Lardini, etc.)
- **89 outfit pages** with complete styling
- **Top items**: The Row brown tassel loafer (54 appearances), Saint Laurent loafer (33 appearances)
- **Clean, manually curated data** with proper item separation

## 🛠️ Technology Stack

- **Backend**: Python Flask (development)
- **Frontend**: Vanilla JavaScript, CSS Grid/Flexbox
- **Data Processing**: OCR with Tesseract, manual curation
- **Deployment**: Static site generation for Netlify
- **Mobile**: Responsive design, touch-friendly interface

## 📁 Project Structure

```
├── app.py                     # Flask development server
├── extract_clothing_items.py  # OCR extraction script
├── clean_data_directly.py     # Data cleaning utilities
├── generate_static_site.py    # Static site generator
├── clothing_index.json       # Item → pages mapping
├── page_items.json           # Page → items mapping
├── Kevin_Summer_Looks_Pages/  # Original outfit images
├── templates/                 # Flask templates
├── dist/                      # Generated static site
└── DEPLOYMENT_GUIDE.md       # Deployment instructions
```

## 🎯 Key Features Explained

### Smart Item Discovery
- Click any clothing item to see all outfits where it appears
- Visual grid of outfit images for easy browsing
- Back-navigation between item views and outfit pages

### Advanced Search
- Real-time search filtering
- Search by brand, item type, or specific names
- Mobile-friendly search interface

### Mobile Optimization
- Touch-friendly buttons and navigation
- Responsive grid layouts
- Optimized image loading
- Swipe-friendly interface

## 🔄 Data Management

The application uses a dual-index system:
- `clothing_index.json`: Maps each clothing item to pages where it appears
- `page_items.json`: Maps each page to the items it contains

To update the data:
1. Edit `page_items.json` with new items
2. Run `python3 rebuild_index.py` to regenerate the clothing index
3. Run `python3 generate_static_site.py` to update the static site

## 🎨 Design Philosophy

- **Mobile-first**: Designed primarily for phone usage
- **Visual discovery**: Images are the primary navigation method
- **Speed**: Lightweight, fast-loading interface
- **Accessibility**: High contrast, readable fonts, touch-friendly targets

## 📈 Statistics

- **Most versatile piece**: The Row brown tassel loafer (appears in 54 outfits)
- **Key layering pieces**: Lardini blazers (green and prince of wales)
- **Color palette**: Strong representation of blues, greens, and neutrals
- **Seasonal focus**: Summer wardrobe with lightweight fabrics

## 🚀 Deployment

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed deployment instructions to Netlify.

## 🤝 Contributing

This is a personal wardrobe project, but feel free to fork and adapt for your own clothing collection!

---

Built with ❤️ for style discovery and mobile browsing.