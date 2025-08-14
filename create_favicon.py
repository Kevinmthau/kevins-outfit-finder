#!/usr/bin/env python3
"""
Create a simple favicon for the outfit finder site.
Since we can't access the uploaded image directly, this creates a simple wardrobe icon.
"""

from PIL import Image, ImageDraw
import os

def create_favicon():
    """Create a simple wardrobe icon as favicon"""
    
    # Create a 32x32 image with transparent background
    img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a simple wardrobe shape (rectangle with doors)
    # Main cabinet
    draw.rectangle([4, 4, 28, 28], fill=(139, 90, 43), outline=(101, 67, 33), width=1)
    
    # Left door
    draw.rectangle([6, 6, 15, 26], fill=(160, 110, 60), outline=(101, 67, 33), width=1)
    # Right door
    draw.rectangle([17, 6, 26, 26], fill=(160, 110, 60), outline=(101, 67, 33), width=1)
    
    # Door handles
    draw.ellipse([12, 15, 14, 17], fill=(80, 50, 30))
    draw.ellipse([19, 15, 21, 17], fill=(80, 50, 30))
    
    # Save as PNG
    img.save('favicon.png', 'PNG')
    
    # Also save as ICO for better compatibility
    img.save('favicon.ico', 'ICO', sizes=[(32, 32)])
    
    print("✅ Created favicon.png and favicon.ico")

if __name__ == "__main__":
    create_favicon()