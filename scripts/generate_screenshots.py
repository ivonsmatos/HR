"""Generate placeholder screenshots for PWA"""
from PIL import Image, ImageDraw, ImageFont
import os

SCREENSHOTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'static', 'images', 'screenshots')
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

SIZES = [
    (1280, 720, 'screenshot-1280x720.png'),
    (750, 1334, 'screenshot-750x1334.png'),
]

for width, height, filename in SIZES:
    img = Image.new('RGB', (width, height), color='#0D1F2D')
    draw = ImageDraw.Draw(img)
    
    # Draw SyncRH text
    text = "SyncRH"
    try:
        font = ImageFont.truetype("arial.ttf", 72)
    except:
        font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    draw.text((x, y), text, fill='#3B82F6', font=font)
    
    # Subtitle
    subtitle = "Sistema de RH Inteligente"
    try:
        small_font = ImageFont.truetype("arial.ttf", 32)
    except:
        small_font = ImageFont.load_default()
    
    bbox2 = draw.textbbox((0, 0), subtitle, font=small_font)
    sub_width = bbox2[2] - bbox2[0]
    draw.text(((width - sub_width) // 2, y + text_height + 20), subtitle, fill='#D0E5F2', font=small_font)
    
    filepath = os.path.join(SCREENSHOTS_DIR, filename)
    img.save(filepath, 'PNG')
    print(f'Created {filepath}')

print('Screenshots generated!')
