#!/usr/bin/env python3
"""
Script to extract and categorize clothing items from Spring outfit pages.
"""

import os
import json
from PIL import Image
import pytesseract
from collections import defaultdict
import re

# Set tesseract path for Homebrew installation
pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'

# Define clothing categories
CATEGORIES = {
    'Outerwear': ['jacket', 'coat', 'blazer', 'windbreaker', 'bomber', 'trench', 'parka', 'vest'],
    'Tops': ['shirt', 'polo', 't-shirt', 'tee', 'blouse', 'sweater', 'pullover', 'hoodie', 'cardigan', 'knit', 'henley', 'tank'],
    'Bottoms': ['trouser', 'pant', 'jean', 'chino', 'short', 'slack', 'jogger'],
    'Footwear': ['shoe', 'sneaker', 'loafer', 'boot', 'sandal', 'slipper', 'oxford', 'derby', 'moccasin', 'espadrille'],
    'Accessories': ['belt', 'watch', 'sunglasses', 'hat', 'cap', 'scarf', 'tie', 'bag', 'wallet', 'bracelet', 'necklace'],
    'Suits': ['suit', 'tuxedo'],
    'Activewear': ['tracksuit', 'sweatpant', 'athletic', 'gym', 'running', 'training']
}

# Common Spring brands to look for
SPRING_BRANDS = [
    'Saint Laurent', 'Boglioli', 'The Row', 'Prada', 'Iris Von Arnim', 
    'Lardini', 'Tom Ford', 'Brunello', 'Gucci', 'Lacoste', 'Loro Piana',
    'Zegna', 'Hermès', 'Bottega Veneta', 'Celine', 'Dior', 'Valentino',
    'Balenciaga', 'Acne Studios', 'Stone Island', 'Moncler', 'Burberry',
    'Ralph Lauren', 'Polo Ralph Lauren', 'Off-White', 'Fear of God',
    'Thom Browne', 'Maison Margiela', 'Rick Owens', 'Common Projects'
]

def extract_text_from_image(image_path):
    """Extract text from image using OCR"""
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return ""

def categorize_item(item_text):
    """Categorize a clothing item based on keywords"""
    item_lower = item_text.lower()
    
    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword in item_lower:
                return category
    
    return 'Other'

def parse_clothing_items(text):
    """Parse and categorize clothing items from extracted text"""
    lines = text.strip().split('\n')
    clothing_items = []
    current_item = ""
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if this line starts a new item (brand name or looks like start of item)
        if any(brand in line for brand in SPRING_BRANDS):
            # Save previous item if it exists
            if current_item:
                item_data = {
                    'name': current_item.strip(),
                    'category': categorize_item(current_item)
                }
                clothing_items.append(item_data)
            current_item = line
        elif any(keyword in line.lower() for keyword in ['polo', 'shirt', 'trouser', 'blazer', 'loafer', 'sweater', 'jacket', 'pants', 'shoe', 'sneaker', 'coat', 'jean', 'short', 'boot', 'belt', 'watch', 'sunglasses']):
            # This might be a continuation or standalone item
            if current_item and not any(keyword in current_item.lower() for keyword in CATEGORIES['Tops'] + CATEGORIES['Bottoms'] + CATEGORIES['Footwear'] + CATEGORIES['Outerwear']):
                # Continuation of previous item
                current_item += " " + line
            else:
                # Save previous and start new
                if current_item:
                    item_data = {
                        'name': current_item.strip(),
                        'category': categorize_item(current_item)
                    }
                    clothing_items.append(item_data)
                current_item = line
        else:
            # Might be a continuation
            if current_item:
                current_item += " " + line
    
    # Don't forget the last item
    if current_item:
        item_data = {
            'name': current_item.strip(),
            'category': categorize_item(current_item)
        }
        clothing_items.append(item_data)
    
    # Clean up items
    cleaned_items = []
    for item in clothing_items:
        # Remove extra whitespace and filter out very short items
        item['name'] = ' '.join(item['name'].split())
        if len(item['name']) > 3:
            cleaned_items.append(item)
    
    return cleaned_items

def main():
    """Main function to process all Spring images and create categorized clothing index"""
    pages_dir = "KEVIN_Spring_Looks_Images"
    clothing_index = defaultdict(list)
    page_items = {}
    category_stats = defaultdict(int)
    
    if not os.path.exists(pages_dir):
        print(f"Directory {pages_dir} not found!")
        return
    
    # Get all PNG files and sort them numerically
    png_files = [f for f in os.listdir(pages_dir) if f.endswith('.png')]
    png_files.sort(key=lambda x: int(re.findall(r'\d+', x)[0]))
    
    print(f"Processing {len(png_files)} Spring collection images...")
    print("=" * 60)
    
    for filename in png_files:
        if filename.endswith('.png'):
            page_num = filename.replace('.png', '')
            image_path = os.path.join(pages_dir, filename)
            
            print(f"\nProcessing {filename}...")
            
            # Extract text from image
            text = extract_text_from_image(image_path)
            
            # Parse and categorize clothing items
            items = parse_clothing_items(text)
            
            if items:
                page_items[page_num] = items
                
                # Add to clothing index and track categories
                for item in items:
                    item_key = f"{item['name']} ({item['category']})"
                    clothing_index[item_key].append(page_num)
                    category_stats[item['category']] += 1
                
                print(f"  Found {len(items)} items:")
                for item in items:
                    print(f"    - {item['name']} [{item['category']}]")
            else:
                print(f"  No items found")
    
    # Save the index to JSON files
    with open('clothing_index_spring.json', 'w') as f:
        json.dump(dict(clothing_index), f, indent=2)
    
    with open('page_items_spring.json', 'w') as f:
        json.dump(page_items, f, indent=2)
    
    # Save category statistics
    with open('category_stats_spring.json', 'w') as f:
        json.dump(dict(category_stats), f, indent=2)
    
    print(f"\n{'=' * 60}")
    print(f"Processing complete!")
    print(f"Total unique clothing items: {len(clothing_index)}")
    print(f"Pages processed: {len(page_items)}")
    
    # Print category statistics
    print("\nCategory breakdown:")
    for category, count in sorted(category_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  {category}: {count} items")
    
    # Print most common items
    print("\nMost common items:")
    sorted_items = sorted(clothing_index.items(), key=lambda x: len(x[1]), reverse=True)
    for item, pages in sorted_items[:15]:
        print(f"  {item}: appears on {len(pages)} pages")

if __name__ == "__main__":
    main()