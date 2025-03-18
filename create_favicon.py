from PIL import Image, ImageDraw

# Create a 32x32 image with a transparent background
size = 32
img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Draw a simple 'F' for Faraday
draw.rectangle([4, 4, 28, 8], fill=(0, 119, 182))  # Top horizontal line
draw.rectangle([4, 4, 8, 28], fill=(0, 119, 182))  # Vertical line
draw.rectangle([4, 14, 20, 18], fill=(0, 119, 182))  # Middle horizontal line

# Save as ICO file
img.save('static/favicon.ico', format='ICO') 