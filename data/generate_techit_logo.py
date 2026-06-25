"""
TechIT Logo Generator
Creates PNG logos in multiple sizes for all social media platforms
"""
from PIL import Image, ImageDraw, ImageFont
import os

OUTPUT_DIR = r"C:\Claude\AI_\TechIT_Logo"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_logo(size, filename):
    """Create TechIT logo at specified size"""

    # Colors
    BG_DARK = (15, 23, 42)
    BG_LIGHT = (30, 41, 59)
    CYAN = (6, 182, 212)
    BLUE = (59, 130, 246)
    PURPLE = (167, 139, 250)
    WHITE = (255, 255, 255)
    GRAY = (148, 163, 184)
    SAFFRON = (255, 153, 51)
    GREEN = (19, 136, 8)
    NAVY = (0, 0, 128)

    # Create base image
    img = Image.new('RGB', (size, size), BG_DARK)
    draw = ImageDraw.Draw(img)

    # Gradient background (simple version)
    for y in range(size):
        ratio = y / size
        r = int(BG_DARK[0] + (BG_LIGHT[0] - BG_DARK[0]) * ratio)
        g = int(BG_DARK[1] + (BG_LIGHT[1] - BG_DARK[1]) * ratio)
        b = int(BG_DARK[2] + (BG_LIGHT[2] - BG_DARK[2]) * ratio)
        draw.line([(0, y), (size, y)], fill=(r, g, b))

    # Rounded corners (mask)
    corner_radius = int(size * 0.18)
    mask = Image.new('L', (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([(0, 0), (size, size)], corner_radius, fill=255)

    # Apply rounded corners
    rounded = Image.new('RGB', (size, size), (0, 0, 0))
    rounded.paste(img, (0, 0), mask)
    img = rounded
    draw = ImageDraw.Draw(img)

    # Decorative circuit lines (subtle)
    line_color = (6, 182, 212, 30)
    # Top left circuit
    draw.line([(0, int(size*0.15)), (int(size*0.3), int(size*0.15))],
              fill=CYAN, width=max(1, size//400))
    draw.ellipse([int(size*0.3)-4, int(size*0.15)-4,
                  int(size*0.3)+4, int(size*0.15)+4], outline=CYAN, width=1)
    # Bottom right circuit
    draw.line([(size, int(size*0.85)), (int(size*0.7), int(size*0.85))],
              fill=CYAN, width=max(1, size//400))
    draw.ellipse([int(size*0.7)-4, int(size*0.85)-4,
                  int(size*0.7)+4, int(size*0.85)+4], outline=CYAN, width=1)

    # Decorative rings around code symbol
    cx, cy = size // 2, int(size * 0.4)
    ring1 = int(size * 0.27)
    ring2 = int(size * 0.24)
    draw.ellipse([cx-ring1, cy-ring1, cx+ring1, cy+ring1],
                outline=BLUE, width=max(2, size//300))
    draw.ellipse([cx-ring2, cy-ring2, cx+ring2, cy+ring2],
                outline=CYAN, width=max(1, size//500))

    # Code brackets </>
    code_font_size = int(size * 0.22)
    try:
        # Try to use a monospace font
        code_font = ImageFont.truetype("consola.ttf", code_font_size)
    except:
        try:
            code_font = ImageFont.truetype("cour.ttf", code_font_size)
        except:
            code_font = ImageFont.load_default()

    code_text = "</>"
    bbox = draw.textbbox((0, 0), code_text, font=code_font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    draw.text((cx - text_w//2, cy - text_h//2 - bbox[1]),
              code_text, font=code_font, fill=CYAN)

    # Brand name "TechIT"
    brand_font_size = int(size * 0.14)
    try:
        brand_font = ImageFont.truetype("arialbd.ttf", brand_font_size)
    except:
        try:
            brand_font = ImageFont.truetype("arial.ttf", brand_font_size)
        except:
            brand_font = ImageFont.load_default()

    brand_text = "TechIT"
    bbox = draw.textbbox((0, 0), brand_text, font=brand_font)
    text_w = bbox[2] - bbox[0]
    draw.text((cx - text_w//2, int(size*0.68)),
              brand_text, font=brand_font, fill=WHITE)

    # Tagline
    tag_font_size = int(size * 0.035)
    try:
        tag_font = ImageFont.truetype("arial.ttf", tag_font_size)
    except:
        tag_font = ImageFont.load_default()

    tag_text = "TECH IN HINDI"
    bbox = draw.textbbox((0, 0), tag_text, font=tag_font)
    text_w = bbox[2] - bbox[0]
    # Letter spacing
    spaced = "T E C H   I N   H I N D I"
    bbox = draw.textbbox((0, 0), spaced, font=tag_font)
    text_w = bbox[2] - bbox[0]
    draw.text((cx - text_w//2, int(size*0.82)),
              spaced, font=tag_font, fill=GRAY)

    # Indian flag accent
    flag_width = int(size * 0.35)
    flag_height = max(4, int(size * 0.012))
    flag_x = cx - flag_width // 2
    flag_y = int(size * 0.88)

    part_width = flag_width // 3
    draw.rectangle([flag_x, flag_y, flag_x + part_width, flag_y + flag_height],
                   fill=SAFFRON)
    draw.rectangle([flag_x + part_width, flag_y,
                    flag_x + 2*part_width, flag_y + flag_height],
                   fill=WHITE)
    draw.rectangle([flag_x + 2*part_width, flag_y,
                    flag_x + flag_width, flag_y + flag_height],
                   fill=GREEN)
    # Chakra dot in center
    chakra_x = flag_x + flag_width // 2
    chakra_y = flag_y + flag_height // 2
    chakra_r = max(2, flag_height // 2)
    draw.ellipse([chakra_x - chakra_r, chakra_y - chakra_r,
                  chakra_x + chakra_r, chakra_y + chakra_r],
                 fill=NAVY)

    # Save
    img.save(filename, 'PNG', quality=95)
    return filename

# Generate logos for different platforms
SIZES = {
    'instagram_profile': 1080,        # 1080x1080
    'profile_high_res': 2000,         # For print/banner use
    'whatsapp': 640,                  # WhatsApp profile
    'favicon_blogger': 512,           # Favicon size
    'small_preview': 256,             # General small
}

print("Generating TechIT logos...")
print("=" * 50)
for name, size in SIZES.items():
    filename = os.path.join(OUTPUT_DIR, f"techit_logo_{name}_{size}x{size}.png")
    create_logo(size, filename)
    file_size_kb = os.path.getsize(filename) / 1024
    print(f"[OK] {name} -> {size}x{size}px ({file_size_kb:.1f} KB)")

print("=" * 50)
print("All logos saved to:", OUTPUT_DIR)
