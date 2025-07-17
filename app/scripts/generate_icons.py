#!/usr/bin/env python3
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def create_icon(size, text="F"):
    # Create a new image with a blue background
    image = Image.new('RGB', (size, size), '#1a73e8')
    draw = ImageDraw.Draw(image)
    
    # Try to load Arial font, fallback to default if not available
    try:
        font = ImageFont.truetype("Arial.ttf", size=int(size * 0.6))
    except:
        font = ImageFont.load_default()
    
    # Calculate text position to center it
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    # Draw the text
    draw.text((x, y), text, fill='white', font=font)
    return image

def convert_icons():
    # Get the absolute path to the project root (one level up from scripts)
    base_dir = Path(__file__).resolve().parent.parent
    icons_dir = base_dir / "static" / "icons"
    images_dir = base_dir / "static" / "images"
    
    # Create directories if they don't exist
    icons_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate favicon (32x32)
    favicon = create_icon(32)
    favicon.save(icons_dir / "favicon.ico", format='ICO')
    print(f"Generated favicon.ico")
    
    # Apple Touch Icon sizes
    apple_icon_sizes = [
        (180, 180, ""),
        (152, 152, "-152x152"),
        (120, 120, "-120x120"),
        (76, 76, "-76x76"),
        (60, 60, "-60x60")
    ]
    
    # Generate all Apple Touch Icon sizes
    for width, height, suffix in apple_icon_sizes:
        # Generate regular version
        icon = create_icon(width)
        output_file = images_dir / f"apple-touch-icon{suffix}.png"
        icon.save(output_file, format='PNG')
        print(f"Generated {output_file}")
        
        # Generate precomposed version
        precomposed_file = images_dir / f"apple-touch-icon-precomposed{suffix}.png"
        icon.save(precomposed_file, format='PNG')
        print(f"Generated {precomposed_file}")

if __name__ == "__main__":
    convert_icons() 