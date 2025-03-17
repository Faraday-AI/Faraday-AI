#!/usr/bin/env python3
import os
from pathlib import Path
import cairosvg

def convert_icons():
    # Get the absolute path to the icons directory
    base_dir = Path(__file__).resolve().parent.parent
    icons_dir = base_dir / "app" / "static" / "icons"
    
    # Convert favicon.svg to favicon.ico (32x32)
    favicon_svg = icons_dir / "favicon.svg"
    favicon_ico = icons_dir / "favicon.ico"
    if favicon_svg.exists():
        cairosvg.svg2png(
            url=str(favicon_svg),
            write_to=str(favicon_ico),
            output_width=32,
            output_height=32
        )
        print(f"Generated {favicon_ico}")
    
    # Convert apple-touch-icon.svg to apple-touch-icon.png (180x180)
    apple_icon_svg = icons_dir / "apple-touch-icon.svg"
    apple_icon_png = icons_dir / "apple-touch-icon.png"
    if apple_icon_svg.exists():
        cairosvg.svg2png(
            url=str(apple_icon_svg),
            write_to=str(apple_icon_png),
            output_width=180,
            output_height=180
        )
        print(f"Generated {apple_icon_png}")

if __name__ == "__main__":
    convert_icons() 