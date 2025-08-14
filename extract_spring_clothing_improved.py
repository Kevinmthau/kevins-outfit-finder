#!/usr/bin/env python3
"""
Improved script to extract and categorize clothing items from Spring outfit pages.
Better separation of individual items to avoid combining multiple pieces.
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
    'Outerwear': ['jacket', 'coat', 'blazer', 'windbreaker', 'bomber', 'trench', 'parka', 'vest', 'overcoat'],
    'Tops': ['shirt', 'polo', 't-shirt', 'tee', 'blouse', 'sweater', 'pullover', 'hoodie', 'cardigan', 'knit', 'henley', 'tank', 'turtleneck', 'sweatshirt'],
    'Bottoms': ['trouser', 'pant', 'jean', 'chino', 'short', 'slack', 'jogger', 'corduroy', '5 pocket', '5-pocket'],
    'Footwear': ['shoe', 'sneaker', 'loafer', 'boot', 'sandal', 'slipper', 'oxford', 'derby', 'moccasin', 'espadrille', 'desert boot'],
    'Accessories': ['belt', 'watch', 'sunglasses', 'hat', 'cap', 'scarf', 'tie', 'bag', 'wallet', 'bracelet', 'necklace'],
    'Suits': ['suit', 'tuxedo'],
    'Activewear': ['tracksuit', 'sweatpant', 'athletic', 'gym', 'running', 'training']
}

# Common Spring brands to look for
SPRING_BRANDS = [
    'Saint Laurent', 'Boglioli', 'The Row', 'Prada', 'Iris Von Arnim', 
    'Lardini', 'Tom Ford', 'Brunello', 'Gucci', 'Lacoste', 'Loro Piana',
    'Zegna', 'Hermès', 'Hermes', 'Bottega Veneta', 'Celine', 'Dior', 'Valentino',
    'Balenciaga', 'Acne Studios', 'Stone Island', 'Moncler', 'Burberry',
    'Ralph Lauren', 'Polo Ralph Lauren', 'Off-White', 'Fear of God',
    'Thom Browne', 'Maison Margiela', 'Rick Owens', 'Common Projects',
    'Altea', "Drake's", 'Drakes', 'Lanvin', 'Dries', 'Beams',
    'Caruso', 'Le Kasha', 'Officine', 'Loewe', 'Fedeli', 'Frame', 'APC',
    'Barneys', 'Clarks', 'Frankie Shop', 'Brioni', 'Sunspel', 'Massimo Alba'
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

def is_brand_name(text):
    """Check if text contains a brand name"""
    for brand in SPRING_BRANDS:
        if brand.lower() in text.lower():
            return True
    return False

def has_clothing_keyword(text):
    """Check if text contains any clothing-related keyword"""
    all_keywords = []
    for keywords in CATEGORIES.values():
        all_keywords.extend(keywords)
    
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in all_keywords)

def split_combined_items(text):
    """Split text that might contain multiple items"""
    items = []
    
    # Common patterns that indicate multiple items
    # Pattern 1: Brand + item + Brand + item
    words = text.split()
    current_item = []
    
    for i, word in enumerate(words):
        current_item.append(word)
        
        # Check if this word is a clothing type and the next word might be a brand
        if has_clothing_keyword(' '.join(current_item)):
            # Look ahead to see if next word starts a new brand
            if i + 1 < len(words) and is_brand_name(words[i + 1]):
                # We found a complete item
                items.append(' '.join(current_item).strip())
                current_item = []
    
    # Add any remaining words as the last item
    if current_item:
        items.append(' '.join(current_item).strip())
    
    # If we didn't split anything, return the original text
    if len(items) <= 1:
        return [text]
    
    return items

def parse_clothing_items(text):
    """Parse and categorize clothing items from extracted text"""
    lines = text.strip().split('\n')
    clothing_items = []
    current_item = ""
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Remove common OCR artifacts
        line = line.replace('_', '').replace('|', '').replace('"', '').replace('"', '').replace("'", "'")
        line = re.sub(r'^[^\w]+', '', line)  # Remove leading non-word characters
        line = re.sub(r'\s+', ' ', line)  # Normalize spaces
        
        # Skip lines that are just numbers or very short
        if line.isdigit() or len(line) < 3:
            continue
            
        # Check if this line starts a new item (contains a brand name)
        if is_brand_name(line):
            # Save previous item if it exists
            if current_item and has_clothing_keyword(current_item):
                # Check if current_item contains multiple items
                split_items = split_combined_items(current_item.strip())
                for split_item in split_items:
                    if has_clothing_keyword(split_item):
                        item_data = {
                            'name': split_item.strip(),
                            'category': categorize_item(split_item)
                        }
                        clothing_items.append(item_data)
            current_item = line
        elif has_clothing_keyword(line):
            # This might be a continuation or standalone item
            if current_item and not has_clothing_keyword(current_item):
                # Continuation of previous item (brand + item type)
                current_item += " " + line
            else:
                # Save previous and start new
                if current_item and has_clothing_keyword(current_item):
                    # Check if current_item contains multiple items
                    split_items = split_combined_items(current_item.strip())
                    for split_item in split_items:
                        if has_clothing_keyword(split_item):
                            item_data = {
                                'name': split_item.strip(),
                                'category': categorize_item(split_item)
                            }
                            clothing_items.append(item_data)
                current_item = line
        else:
            # Might be a continuation (color, material, etc.)
            if current_item:
                # Only add if it's not too long (avoid combining multiple items)
                if len(current_item) < 40:
                    current_item += " " + line
    
    # Don't forget the last item
    if current_item and has_clothing_keyword(current_item):
        # Check if current_item contains multiple items
        split_items = split_combined_items(current_item.strip())
        for split_item in split_items:
            if has_clothing_keyword(split_item):
                item_data = {
                    'name': split_item.strip(),
                    'category': categorize_item(split_item)
                }
                clothing_items.append(item_data)
    
    # Clean up items and remove duplicates
    seen = set()
    cleaned_items = []
    for item in clothing_items:
        # Remove extra whitespace
        item['name'] = ' '.join(item['name'].split())
        
        # Create a unique key for deduplication
        item_key = item['name'].lower() + "_" + item['category']
        
        if item_key not in seen and len(item['name']) > 3:
            seen.add(item_key)
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
    
    # Process a sample first to show the improvement
    sample_pages = ['page_43.png', 'page_44.png', 'page_52.png']  # Pages with known combined items
    
    for filename in png_files:
        if filename.endswith('.png'):
            page_num = filename.replace('.png', '')
            image_path = os.path.join(pages_dir, filename)
            
            # Show more detail for sample pages
            if filename in sample_pages:
                print(f"\n🔍 Detailed processing of {filename}...")
            else:
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
                
                if filename in sample_pages or len(items) > 5:
                    print(f"  Found {len(items)} items:")
                    for item in items:
                        print(f"    - {item['name']} [{item['category']}]")
                else:
                    print(f"  Found {len(items)} items")
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
    
    # Show specific improvements
    print("\n📋 Sample of improved item separation:")
    for page in ['page_43', 'page_44', 'page_52']:
        if page in page_items:
            print(f"\n{page}:")
            for item in page_items[page]:
                print(f"  - {item['name']} [{item['category']}]")

if __name__ == "__main__":
    main()