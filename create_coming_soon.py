from PIL import Image, ImageDraw, ImageFont
import os

# Create a new image with a dark background
width = 1200
height = 630  # Good size for social media previews
image = Image.new('RGB', (width, height), '#1a1a1a')
draw = ImageDraw.Draw(image)

try:
    # Try to use a nice font if available
    font_path = "/System/Library/Fonts/Supplemental/Arial.ttf"  # Default for macOS
    title_font = ImageFont.truetype(font_path, 120)
    subtitle_font = ImageFont.truetype(font_path, 48)
except:
    # Fallback to default font
    title_font = ImageFont.load_default()
    subtitle_font = ImageFont.load_default()

# Add "COMING SOON" text
title_text = "COMING SOON"
title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
title_width = title_bbox[2] - title_bbox[0]
title_height = title_bbox[3] - title_bbox[1]
title_x = (width - title_width) // 2
title_y = (height - title_height) // 2 - 40
draw.text((title_x, title_y), title_text, font=title_font, fill='#4a90e2')

# Add subtitle
subtitle_text = "Faraday AI - Transforming Education Through AI"
subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
subtitle_x = (width - subtitle_width) // 2
subtitle_y = title_y + title_height + 20
draw.text((subtitle_x, subtitle_y), subtitle_text, font=subtitle_font, fill='#888888')

# Create directory if it doesn't exist
os.makedirs('app/static/images', exist_ok=True)

# Save the image
image.save('app/static/images/coming-soon.png', 'PNG')
print("Image created successfully at app/static/images/coming-soon.png") 