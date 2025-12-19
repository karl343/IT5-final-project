"""
Generate SwiftPay Logo Images
Creates PNG logo files from the SVG design
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_logo_png(size=(300, 85), output_path="SwiftPay/assets/logo.png"):
    """Create a PNG logo file"""
    # Create image with transparent background
    img = Image.new('RGBA', size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Colors
    white = (255, 255, 255)
    black = (0, 0, 0)
    orange = (245, 124, 0)
    dark_blue = (26, 35, 126)
    
    # Draw white rounded square
    square_size = 55
    square_x = 0
    square_y = 15
    # Draw shadow first
    draw.rounded_rectangle(
        [(square_x + 2, square_y + 2), (square_x + square_size + 2, square_y + square_size + 2)],
        radius=12,
        fill=(255, 255, 255, 240)
    )
    # Draw main square
    draw.rounded_rectangle(
        [(square_x, square_y), (square_x + square_size, square_y + square_size)],
        radius=12,
        fill=white
    )
    
    # Draw dollar sign
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except:
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 36)
        except:
            font = ImageFont.load_default()
    
    # Center dollar sign
    dollar_text = "$"
    bbox = draw.textbbox((0, 0), dollar_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    dollar_x = square_x + (square_size - text_width) // 2
    dollar_y = square_y + (square_size - text_height) // 2
    draw.text((dollar_x, dollar_y), dollar_text, fill=black, font=font)
    
    # Draw orange equals sign (two horizontal bars)
    bar_width = 30
    bar_height = 5
    bar_spacing = 5
    start_x = square_size + 12
    
    # First bar
    draw.rounded_rectangle(
        [(start_x, 30), (start_x + bar_width, 30 + bar_height)],
        radius=2,
        fill=orange
    )
    # Second bar
    draw.rounded_rectangle(
        [(start_x, 40), (start_x + bar_width, 40 + bar_height)],
        radius=2,
        fill=orange
    )
    
    # Draw "SwiftPay" text
    try:
        text_font = ImageFont.truetype("arial.ttf", 28)
    except:
        try:
            text_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 28)
        except:
            text_font = ImageFont.load_default()
    
    text_x = start_x + bar_width + 15
    text_y = 20
    draw.text((text_x, text_y), "SwiftPay", fill=dark_blue, font=text_font)
    
    # Save image
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, 'PNG')
    print(f"Logo saved to {output_path}")
    
    return img

if __name__ == "__main__":
    # Create different sizes
    create_logo_png((300, 85), "SwiftPay/assets/logo.png")
    create_logo_png((600, 170), "SwiftPay/assets/logo@2x.png")
    create_logo_png((150, 43), "SwiftPay/assets/logo_small.png")

