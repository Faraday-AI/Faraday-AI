from PIL import Image, ImageDraw, ImageFont
import os

# Create a new image with a gradient background
width = 800
height = 400
img = Image.new('RGB', (width, height))
draw = ImageDraw.Draw(img)

# Create a gradient background (dark blue to lighter blue)
for y in range(height):
    r = int(0 + (y / height) * 20)  # Dark to slightly lighter
    g = int(40 + (y / height) * 60)  # More blue variation
    b = int(80 + (y / height) * 100)  # Strong blue gradient
    draw.line([(0, y), (width, y)], fill=(r, g, b))

# Try to use a system font with fallbacks
font_size = 80
font_path = None
system_fonts = [
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/SFPro.ttf",
    "/Library/Fonts/Arial.ttf"
]

for font_file in system_fonts:
    if os.path.exists(font_file):
        font_path = font_file
        break

try:
    if font_path:
        font = ImageFont.truetype(font_path, font_size)
    else:
        font = ImageFont.load_default()
except Exception:
    font = ImageFont.load_default()

# Main text
main_text = "Coming Soon"
bbox = draw.textbbox((0, 0), main_text, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]
x = (width - text_width) // 2
y = (height - text_height) // 2 - 20

# Add a subtle shadow effect
shadow_offset = 3
draw.text((x + shadow_offset, y + shadow_offset), main_text, font=font, fill=(0, 0, 0, 128))
draw.text((x, y), main_text, font=font, fill=(255, 255, 255))

# Subtitle
subtitle = "Faraday AI Educational Platform"
subtitle_font_size = 30
try:
    subtitle_font = ImageFont.truetype(font_path, subtitle_font_size) if font_path else ImageFont.load_default()
except Exception:
    subtitle_font = ImageFont.load_default()

bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
subtitle_width = bbox[2] - bbox[0]
x = (width - subtitle_width) // 2
y = y + text_height + 20

# Add subtitle with shadow
draw.text((x + 2, y + 2), subtitle, font=subtitle_font, fill=(0, 0, 0, 128))
draw.text((x, y), subtitle, font=subtitle_font, fill=(200, 200, 200))

# Save the image
if not os.path.exists('static/images'):
    os.makedirs('static/images')
img.save('static/images/coming-soon.png', quality=95) 