"""
TechIT Banner Generator
Creates professional banners for X/Twitter, LinkedIn, Facebook
"""
from PIL import Image, ImageDraw, ImageFont
import os

OUTPUT_DIR = r"C:\Claude\AI_\TechIT_Logo"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_banner(width, height, filename, platform_name=""):
    """Create banner with TechIT branding"""

    # Colors
    BG_DARK = (15, 23, 42)
    BG_MID = (30, 41, 59)
    BG_LIGHT = (51, 65, 85)
    CYAN = (6, 182, 212)
    BLUE = (59, 130, 246)
    PURPLE = (167, 139, 250)
    WHITE = (255, 255, 255)
    GRAY = (148, 163, 184)
    DIM_GRAY = (100, 116, 139)
    SAFFRON = (255, 153, 51)
    GREEN = (19, 136, 8)
    NAVY = (0, 0, 128)
    DARK_CYAN = (8, 145, 178)

    img = Image.new('RGB', (width, height), BG_DARK)
    draw = ImageDraw.Draw(img)

    # Gradient background (diagonal)
    for y in range(height):
        for x_step in range(0, width, 50):
            ratio_y = y / height
            ratio_x = x_step / width
            ratio = (ratio_x + ratio_y) / 2
            r = int(BG_DARK[0] + (BG_LIGHT[0] - BG_DARK[0]) * ratio * 0.5)
            g = int(BG_DARK[1] + (BG_LIGHT[1] - BG_DARK[1]) * ratio * 0.5)
            b = int(BG_DARK[2] + (BG_LIGHT[2] - BG_DARK[2]) * ratio * 0.5)
            draw.rectangle([(x_step, y), (x_step + 50, y + 1)], fill=(r, g, b))

    # Simpler gradient
    for y in range(height):
        ratio = y / height
        r = int(BG_DARK[0] * (1 - ratio * 0.3) + BG_MID[0] * (ratio * 0.3))
        g = int(BG_DARK[1] * (1 - ratio * 0.3) + BG_MID[1] * (ratio * 0.3))
        b = int(BG_DARK[2] * (1 - ratio * 0.3) + BG_MID[2] * (ratio * 0.3))
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Decorative circuit lines (top and bottom)
    line_width = max(1, height // 200)

    # Top circuit
    draw.line([(0, int(height*0.1)), (int(width*0.15), int(height*0.1))],
              fill=CYAN, width=line_width)
    draw.ellipse([int(width*0.15)-6, int(height*0.1)-6,
                  int(width*0.15)+6, int(height*0.1)+6], outline=CYAN, width=2)
    draw.line([(int(width*0.15), int(height*0.1)),
               (int(width*0.15), int(height*0.25))], fill=CYAN, width=line_width)

    # Right side circuit
    draw.line([(width, int(height*0.3)), (int(width*0.85), int(height*0.3))],
              fill=BLUE, width=line_width)
    draw.ellipse([int(width*0.85)-6, int(height*0.3)-6,
                  int(width*0.85)+6, int(height*0.3)+6], outline=BLUE, width=2)

    # Bottom circuit
    draw.line([(0, int(height*0.85)), (int(width*0.2), int(height*0.85))],
              fill=DARK_CYAN, width=line_width)
    draw.ellipse([int(width*0.2)-5, int(height*0.85)-5,
                  int(width*0.2)+5, int(height*0.85)+5], outline=DARK_CYAN, width=2)

    # Dots pattern (subtle grid)
    dot_color = (51, 65, 85)
    spacing = max(40, height // 12)
    for x in range(0, width, spacing):
        for y in range(0, height, spacing):
            draw.ellipse([x-1, y-1, x+1, y+1], fill=dot_color)

    # Left section: Brand text
    left_x = int(width * 0.07)
    center_y = height // 2

    # Code symbol </> on left side
    code_font_size = int(height * 0.32)
    try:
        code_font = ImageFont.truetype("consolab.ttf", code_font_size)
    except:
        try:
            code_font = ImageFont.truetype("consola.ttf", code_font_size)
        except:
            try:
                code_font = ImageFont.truetype("cour.ttf", code_font_size)
            except:
                code_font = ImageFont.load_default()

    code_text = "</>"
    bbox = draw.textbbox((0, 0), code_text, font=code_font)
    code_w = bbox[2] - bbox[0]
    code_h = bbox[3] - bbox[1]
    draw.text((left_x, center_y - code_h // 2 - bbox[1]),
              code_text, font=code_font, fill=CYAN)

    # Brand text TechIT (center-left)
    brand_x = left_x + code_w + int(width * 0.04)
    brand_font_size = int(height * 0.28)
    try:
        brand_font = ImageFont.truetype("arialbd.ttf", brand_font_size)
    except:
        try:
            brand_font = ImageFont.truetype("arial.ttf", brand_font_size)
        except:
            brand_font = ImageFont.load_default()

    brand_text = "TechIT"
    bbox = draw.textbbox((0, 0), brand_text, font=brand_font)
    brand_w = bbox[2] - bbox[0]
    brand_h = bbox[3] - bbox[1]
    draw.text((brand_x, int(height * 0.28)),
              brand_text, font=brand_font, fill=WHITE)

    # Tagline below brand
    tag_font_size = int(height * 0.08)
    try:
        tag_font = ImageFont.truetype("arial.ttf", tag_font_size)
    except:
        tag_font = ImageFont.load_default()

    tag_text = "TECH IN HINDI"
    bbox = draw.textbbox((0, 0), tag_text, font=tag_font)
    spaced_tag = "T E C H   I N   H I N D I"
    bbox = draw.textbbox((0, 0), spaced_tag, font=tag_font)
    draw.text((brand_x, int(height * 0.62)),
              spaced_tag, font=tag_font, fill=GRAY)

    # Right section: Subtitle features
    right_x = int(width * 0.62)

    # "What I Teach" mini-header
    feat_header_size = int(height * 0.07)
    try:
        feat_header_font = ImageFont.truetype("arialbd.ttf", feat_header_size)
    except:
        feat_header_font = ImageFont.load_default()

    draw.text((right_x, int(height * 0.2)),
              "WHAT I TEACH", font=feat_header_font, fill=CYAN)

    # Features list
    feat_size = int(height * 0.075)
    try:
        feat_font = ImageFont.truetype("arial.ttf", feat_size)
    except:
        feat_font = ImageFont.load_default()

    features = [
        "✓  MERN Stack (Hindi)",
        "✓  AI Tools & Tutorials",
        "✓  Web Development",
        "✓  Coding for Indians"
    ]
    feat_y = int(height * 0.35)
    feat_spacing = int(height * 0.11)
    for i, feat in enumerate(features):
        draw.text((right_x, feat_y + i * feat_spacing),
                  feat, font=feat_font, fill=WHITE)

    # Bottom Indian flag stripe (full width)
    flag_y = height - int(height * 0.04)
    flag_height = int(height * 0.025)
    third = width // 3
    draw.rectangle([0, flag_y, third, flag_y + flag_height], fill=SAFFRON)
    draw.rectangle([third, flag_y, 2*third, flag_y + flag_height], fill=WHITE)
    draw.rectangle([2*third, flag_y, width, flag_y + flag_height], fill=GREEN)
    # Chakra
    chakra_x = third + third // 2
    chakra_y = flag_y + flag_height // 2
    chakra_r = max(3, flag_height // 2 - 2)
    draw.ellipse([chakra_x - chakra_r, chakra_y - chakra_r,
                  chakra_x + chakra_r, chakra_y + chakra_r],
                 outline=NAVY, width=2)

    # Bottom text - URL
    url_size = int(height * 0.06)
    try:
        url_font = ImageFont.truetype("arial.ttf", url_size)
    except:
        url_font = ImageFont.load_default()

    url_text = "itinfohubs.blogspot.com"
    bbox = draw.textbbox((0, 0), url_text, font=url_font)
    url_w = bbox[2] - bbox[0]
    draw.text((width // 2 - url_w // 2, flag_y - int(height * 0.1)),
              url_text, font=url_font, fill=CYAN)

    # Save
    img.save(filename, 'PNG', quality=95)
    return filename


# Banner sizes for different platforms
BANNERS = {
    'twitter_x': (1500, 500),       # X header
    'linkedin': (1584, 396),         # LinkedIn cover
    'facebook': (1640, 624),         # Facebook cover
    'youtube': (2560, 1440),         # YouTube channel art
}

print("Generating TechIT banners...")
print("=" * 50)
for platform, (w, h) in BANNERS.items():
    filename = os.path.join(OUTPUT_DIR, f"techit_banner_{platform}_{w}x{h}.png")
    create_banner(w, h, filename, platform)
    file_size_kb = os.path.getsize(filename) / 1024
    print(f"[OK] {platform} -> {w}x{h}px ({file_size_kb:.1f} KB)")

print("=" * 50)
print("All banners saved to:", OUTPUT_DIR)
