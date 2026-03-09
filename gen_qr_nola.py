#!/usr/bin/env python3
"""Generate a vintage New Orleans jazz club style QR code poster for James O'Donnell."""

import math
import random
import qrcode
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# --- Config ---
WIDTH, HEIGHT = 560, 880
QR_URL = "https://jodonnel.github.io/james-resume/"
OUT = "/home/jodonnell/chloe/tools/james-resume/qr-agent-nola.png"

# Colors
MIDNIGHT = (25, 25, 55)
BURNT_SIENNA = (175, 85, 45)
CREAM = (245, 235, 215)
BRASS = (205, 170, 90)
DEEP_RED = (140, 35, 35)
GOLD_DIM = (180, 150, 70)
WARM_BLACK = (30, 28, 26)

# Fonts
SERIF = "/usr/share/fonts/google-noto-vf/NotoSerif[wght].ttf"
SERIF_IT = "/usr/share/fonts/google-noto-vf/NotoSerif-Italic[wght].ttf"

def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

def text_width(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]

def text_height(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[3] - bbox[1]

def draw_centered(draw, y, text, font, fill):
    w = text_width(draw, text, font)
    draw.text(((WIDTH - w) // 2, y), text, font=font, fill=fill)

def add_texture(img):
    """Add subtle grain/texture for that worn poster feel."""
    draw = ImageDraw.Draw(img)
    random.seed(42)
    for _ in range(8000):
        x = random.randint(0, WIDTH - 1)
        y = random.randint(0, HEIGHT - 1)
        v = random.randint(-20, 20)
        px = img.getpixel((x, y))
        new_px = tuple(max(0, min(255, c + v)) for c in px[:3])
        draw.point((x, y), fill=new_px)

ABSINTHE_GREEN = (120, 180, 100)
ABSINTHE_PALE = (170, 210, 150)

def draw_coupe_glass(draw, cx, cy, scale=1.0):
    """Draw a bold Obituary Cocktail coupe — absinthe-green liquid, prominent lemon twist."""
    s = scale * 1.4  # bigger overall

    # Bowl - wide shallow coupe curve
    bowl_pts = []
    for i in range(60):
        t = math.pi * i / 59
        x = cx + math.cos(t) * 32 * s
        y = cy - 10 * s + math.sin(t) * 18 * s
        bowl_pts.append((x, y))

    # Liquid fill — pale absinthe green
    if len(bowl_pts) > 2:
        draw.polygon(bowl_pts, fill=ABSINTHE_PALE)

    # Bowl outline — bold brass
    for i in range(len(bowl_pts) - 1):
        draw.line([bowl_pts[i], bowl_pts[i + 1]], fill=BRASS, width=max(2, int(3 * s)))
    # Rim line across top
    draw.line([bowl_pts[0], bowl_pts[-1]], fill=BRASS, width=max(2, int(3 * s)))

    # Liquid surface line (slightly below rim, absinthe green)
    surface_y = cy - 8 * s
    rim_w = 30 * s
    draw.line([(cx - rim_w, surface_y), (cx + rim_w, surface_y)],
              fill=ABSINTHE_GREEN, width=max(2, int(2.5 * s)))

    # Stem — bold
    stem_top = cy + 8 * s
    stem_bot = cy + 32 * s
    draw.line([(cx, stem_top), (cx, stem_bot)], fill=BRASS, width=max(2, int(3 * s)))

    # Base — wider, bolder
    base_w = 16 * s
    draw.line([(cx - base_w, stem_bot), (cx + base_w, stem_bot)], fill=BRASS, width=max(2, int(3 * s)))
    draw.ellipse([cx - base_w - 2, stem_bot - 3, cx + base_w + 2, stem_bot + 3], fill=BRASS)

    # Lemon swath — wide ribbon of peel draped over the rim
    LEMON_YELLOW = (220, 195, 60)
    LEMON_SHADOW = (180, 155, 40)
    rim_x = cx + 26 * s
    rim_y = cy - 10 * s
    # Build two edges of a wide ribbon that curls over and drapes down
    edge1 = []
    edge2 = []
    ribbon_w = 6 * s  # width of the swath
    for i in range(50):
        t = i / 49.0
        # Gentle arc: rises slightly from rim, curls over, hangs
        px = rim_x + t * 12 * s + math.sin(t * 3.2) * 6 * s
        py = rim_y - (1 - t) * 8 * s * math.sin(t * 1.5) + t * 24 * s
        # Perpendicular offset for ribbon width
        if i < 49:
            t2 = (i + 1) / 49.0
            nx = rim_x + t2 * 12 * s + math.sin(t2 * 3.2) * 6 * s - px
            ny = rim_y - (1 - t2) * 8 * s * math.sin(t2 * 1.5) + t2 * 24 * s - py
        else:
            nx, ny = edge1[-1][0] - edge1[-2][0], edge1[-1][1] - edge1[-2][1] if len(edge1) > 1 else (1, 0)
        length = math.sqrt(nx * nx + ny * ny) + 0.001
        perp_x = -ny / length * ribbon_w
        perp_y = nx / length * ribbon_w
        edge1.append((px + perp_x, py + perp_y))
        edge2.append((px - perp_x, py - perp_y))

    # Draw as filled polygon (both edges combined)
    swath = edge1 + list(reversed(edge2))
    if len(swath) > 2:
        draw.polygon(swath, fill=LEMON_YELLOW, outline=LEMON_SHADOW)
    # Center highlight stripe
    center_pts = []
    for i in range(50):
        t = i / 49.0
        px = rim_x + t * 12 * s + math.sin(t * 3.2) * 6 * s
        py = rim_y - (1 - t) * 8 * s * math.sin(t * 1.5) + t * 24 * s
        center_pts.append((px, py))
    for i in range(len(center_pts) - 1):
        draw.line([center_pts[i], center_pts[i + 1]], fill=(240, 220, 100), width=max(1, int(1.5 * s)))

def draw_ornamental_line(draw, y, color, style="double"):
    """Draw a decorative divider line."""
    margin = 60
    if style == "double":
        draw.line([(margin, y), (WIDTH - margin, y)], fill=color, width=1)
        draw.line([(margin, y + 4), (WIDTH - margin, y + 4)], fill=color, width=1)
        # Center diamond
        cx = WIDTH // 2
        draw.polygon([(cx - 6, y + 2), (cx, y - 3), (cx + 6, y + 2), (cx, y + 7)], fill=color)
    elif style == "dots":
        for x in range(margin, WIDTH - margin, 8):
            draw.ellipse([x, y, x + 3, y + 3], fill=color)

def draw_border(draw):
    """Double-line vintage poster border."""
    m1, m2 = 12, 20
    draw.rectangle([m1, m1, WIDTH - m1, HEIGHT - m1], outline=BRASS, width=2)
    draw.rectangle([m2, m2, WIDTH - m2, HEIGHT - m2], outline=GOLD_DIM, width=1)
    # Corner ornaments
    for cx, cy in [(m2, m2), (WIDTH - m2, m2), (m2, HEIGHT - m2), (WIDTH - m2, HEIGHT - m2)]:
        draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=BRASS)


def main():
    # --- Background ---
    img = Image.new("RGB", (WIDTH, HEIGHT), MIDNIGHT)
    draw = ImageDraw.Draw(img)

    # Subtle radial gradient overlay
    for y in range(HEIGHT):
        for x in range(WIDTH):
            dx = (x - WIDTH / 2) / (WIDTH / 2)
            dy = (y - HEIGHT / 2) / (HEIGHT / 2)
            dist = math.sqrt(dx * dx + dy * dy)
            factor = min(1.0, dist * 0.3)
            r, g, b = img.getpixel((x, y))
            r = max(0, int(r * (1 - factor * 0.4)))
            g = max(0, int(g * (1 - factor * 0.4)))
            b = max(0, int(b * (1 - factor * 0.4)))
            draw.point((x, y), fill=(r, g, b))

    draw_border(draw)

    # --- Fonts ---
    font_name = load_font(SERIF, 52)
    font_sub = load_font(SERIF_IT, 22)
    font_quote = load_font(SERIF_IT, 20)
    font_detail = load_font(SERIF, 14)
    font_feat = load_font(SERIF_IT, 13)
    font_scan = load_font(SERIF, 13)

    # --- Top Section ---
    y = 38
    draw_centered(draw, y, "JAMES", font_name, CREAM)
    y += 56
    draw_centered(draw, y, "O'DONNELL", font_name, CREAM)
    y += 62

    draw_ornamental_line(draw, y, BRASS, "double")
    y += 18

    draw_centered(draw, y, "Bartender & Mixologist", font_sub, BURNT_SIENNA)
    y += 36

    draw_ornamental_line(draw, y, GOLD_DIM, "dots")
    y += 18

    # Quote
    draw_centered(draw, y, '"It\'s just drinks."', font_quote, BRASS)
    y += 34

    draw_ornamental_line(draw, y, GOLD_DIM, "dots")
    y += 20

    # --- QR Code (martini-glass shaped modules) ---
    qr = qrcode.QRCode(version=4, error_correction=qrcode.constants.ERROR_CORRECT_H,
                        box_size=1, border=0)
    qr.add_data(QR_URL)
    qr.make(fit=True)
    matrix = qr.get_matrix()
    mod_count = len(matrix)

    qr_size = 310
    cell = qr_size / mod_count
    qr_img = Image.new("RGB", (qr_size, qr_size), CREAM)
    qr_draw = ImageDraw.Draw(qr_img)

    def draw_mini_martini(draw, cx, cy, sz):
        """Draw a tiny martini/coupe glass in place of a QR module."""
        half = sz * 0.45
        # V-shaped bowl (triangle pointing down)
        top_l = (cx - half, cy - half * 0.6)
        top_r = (cx + half, cy - half * 0.6)
        bottom = (cx, cy + half * 0.15)
        draw.polygon([top_l, top_r, bottom], fill=WARM_BLACK)
        # Stem
        stem_top = cy + half * 0.15
        stem_bot = cy + half * 0.65
        draw.line([(cx, stem_top), (cx, stem_bot)], fill=WARM_BLACK, width=max(1, int(sz * 0.12)))
        # Base
        base_w = half * 0.6
        draw.line([(cx - base_w, stem_bot), (cx + base_w, stem_bot)], fill=WARM_BLACK, width=max(1, int(sz * 0.14)))

    def is_finder_pattern(r, c, n):
        """Check if module is part of a finder pattern (corners)."""
        if r < 7 and c < 7: return True
        if r < 7 and c >= n - 7: return True
        if r >= n - 7 and c < 7: return True
        return False

    for r, row in enumerate(matrix):
        for c, val in enumerate(row):
            if not val:
                continue
            cx = c * cell + cell / 2
            cy = r * cell + cell / 2
            # Finder patterns stay as squares (required for scanning)
            if is_finder_pattern(r, c, mod_count):
                qr_draw.rectangle([c * cell, r * cell, (c + 1) * cell - 1, (r + 1) * cell - 1],
                                  fill=WARM_BLACK)
            else:
                draw_mini_martini(qr_draw, cx, cy, cell)

    # Clear center circle for the big coupe glass
    qr_cx, qr_cy = qr_size // 2, qr_size // 2
    circle_r = 62
    qr_draw.ellipse([qr_cx - circle_r, qr_cy - circle_r,
                      qr_cx + circle_r, qr_cy + circle_r], fill=CREAM)
    qr_draw.ellipse([qr_cx - circle_r, qr_cy - circle_r,
                      qr_cx + circle_r, qr_cy + circle_r], outline=BURNT_SIENNA, width=2)

    draw_coupe_glass(qr_draw, qr_cx, qr_cy - 4, scale=1.1)

    # Paste QR onto poster
    qr_x = (WIDTH - qr_size) // 2
    qr_y = y
    img.paste(qr_img, (qr_x, qr_y))

    # Decorative frame around QR
    pad = 8
    draw.rectangle([qr_x - pad, qr_y - pad, qr_x + qr_size + pad, qr_y + qr_size + pad],
                   outline=BRASS, width=2)
    draw.rectangle([qr_x - pad - 4, qr_y - pad - 4,
                    qr_x + qr_size + pad + 4, qr_y + qr_size + pad + 4],
                   outline=GOLD_DIM, width=1)

    y = qr_y + qr_size + 22

    # --- Bottom Section ---
    draw_centered(draw, y, "SCAN FOR FULL RÉSUMÉ", font_scan, BRASS)
    y += 24

    draw_ornamental_line(draw, y, BRASS, "double")
    y += 20

    draw_centered(draw, y, "New Orleans Trained · North Carolina", font_detail, CREAM)
    y += 26

    draw_centered(draw, y, "As featured in The New York Times", font_feat, DEEP_RED)
    y += 30

    draw_ornamental_line(draw, y, GOLD_DIM, "dots")

    # --- Texture ---
    add_texture(img)

    img.save(OUT, "PNG")
    print(f"Saved: {OUT}")
    print(f"Size: {img.size}")

if __name__ == "__main__":
    main()
