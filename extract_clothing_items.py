#!/usr/bin/env python3
"""
Script to extract clothing items from outfit pages and create an index.
"""

import os
import json
from PIL import Image
import pytesseract
from collections import defaultdict
import re

# Set tesseract path for Homebrew installation
pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'

def extract_text_from_image(image_path):
    """Extract text from image using OCR"""
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return ""

def parse_clothing_items(text):
    """Parse clothing items from extracted text"""
    lines = text.strip().split('\n')
    clothing_items = []
    current_item = ""
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if this line starts a new item (brand name or looks like start of item)
        if any(brand in line for brand in ['Saint Laurent', 'Boglioli', 'The Row', 'Prada', 'Iris Von Arnim', 'Lardini', 'Tom Ford', 'Brunello', 'Gucci', 'Lacoste']):
            # Save previous item if it exists
            if current_item:
                clothing_items.append(current_item.strip())
            current_item = line
        elif any(keyword in line.lower() for keyword in ['polo', 'shirt', 'trouser', 'blazer', 'loafer', 'sweater', 'jacket', 'pants', 'shoes']):
            # This might be a continuation or standalone item
            if current_item and not any(keyword in current_item.lower() for keyword in ['polo', 'shirt', 'trouser', 'blazer', 'loafer', 'sweater']):
                # Continuation of previous item
                current_item += " " + line
            else:
                # Save previous and start new
                if current_item:
                    clothing_items.append(current_item.strip())
                current_item = line
        else:
            # Might be a continuation
            if current_item:
                current_item += " " + line
    
    # Don't forget the last item
    if current_item:
        clothing_items.append(current_item.strip())
    
    # Clean up items
    cleaned_items = []
    for item in clothing_items:
        # Remove extra whitespace and filter out very short items
        item = ' '.join(item.split())
        if len(item) > 3 and any(keyword in item.lower() for keyword in ['polo', 'shirt', 'trouser', 'blazer', 'loafer', 'sweater', 'jacket', 'pants', 'shoes']):
            cleaned_items.append(item)
    
    return cleaned_items

def main():
    """Main function to process all images and create clothing index"""
    pages_dir = "Kevin_Summer_Looks_Pages"
    clothing_index = defaultdict(list)
    page_items = {}
    
    if not os.path.exists(pages_dir):
        print(f"Directory {pages_dir} not found!")
        return
    
    # Get all PNG files and sort them numerically
    png_files = [f for f in os.listdir(pages_dir) if f.endswith('.png')]
    png_files.sort(key=lambda x: int(re.findall(r'\d+', x)[0]))
    
    print(f"Processing {len(png_files)} images...")
    
    for filename in png_files:
        if filename.endswith('.png'):
            page_num = filename.replace('.png', '')
            image_path = os.path.join(pages_dir, filename)
            
            print(f"Processing {filename}...")
            
            # Extract text from image
            text = extract_text_from_image(image_path)
            
            # Parse clothing items
            items = parse_clothing_items(text)
            
            if items:
                page_items[page_num] = items
                
                # Add to clothing index
                for item in items:
                    clothing_index[item].append(page_num)
                
                print(f"  Found {len(items)} items: {items}")
            else:
                print(f"  No items found")
    
    # Save the index to JSON files
    with open('clothing_index.json', 'w') as f:
        json.dump(dict(clothing_index), f, indent=2)
    
    with open('page_items.json', 'w') as f:
        json.dump(page_items, f, indent=2)
    
    print(f"\nProcessing complete!")
    print(f"Total unique clothing items: {len(clothing_index)}")
    print(f"Pages processed: {len(page_items)}")
    
    # Print some statistics
    print("\nMost common items:")
    sorted_items = sorted(clothing_index.items(), key=lambda x: len(x[1]), reverse=True)
    for item, pages in sorted_items[:10]:
        print(f"  {item}: appears on {len(pages)} pages")

if __name__ == "__main__":
    main()