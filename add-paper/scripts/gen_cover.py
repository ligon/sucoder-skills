#!/usr/bin/env python3
"""Generate a cover image for a paper on ligon.github.io.

Usage:
    python gen_cover.py --title "PAPER TITLE" --output static/images/key.png
    python gen_cover.py --title "PAPER TITLE" --output static/images/key.png \
                        --background /tmp/vis.png

Produces a 1536x1024 PNG in the site palette (cream/navy/amber).

Modes:
  - Text-only (default): title on cream background.
  - With background: composites a provided image (figure or illustration)
    behind the title with an alpha mask for legibility.
"""

import argparse
from PIL import Image, ImageDraw, ImageFont

# ── Colour constants ──────────────────────────────────────────────
NAVY  = (26, 39, 68)
CREAM = (232, 220, 200)
AMBER = (181, 101, 29)

CANVAS_W, CANVAS_H = 1536, 1024
FONT_PATH = "/usr/share/fonts/truetype/ebgaramond/EBGaramond12-Bold.ttf"


def make_title_lines(title: str) -> list[tuple[str, int]]:
    """Split a title into display lines with font sizes.

    Heuristic: short words (<=3 chars) get smaller font; key phrases
    get larger font.  Override by passing --lines directly.
    """
    words = title.upper().split()
    lines = []
    current = []
    for w in words:
        current.append(w)
        # Break roughly every 3-4 words or 30 chars
        line = " ".join(current)
        if len(line) > 28 or len(current) >= 4:
            lines.append(line)
            current = []
    if current:
        lines.append(" ".join(current))

    # Assign sizes: shorter lines get bigger font
    sized = []
    for line in lines:
        if len(line) <= 15:
            sized.append((line, 78))
        elif len(line) <= 25:
            sized.append((line, 58))
        else:
            sized.append((line, 46))
    return sized


def apply_alpha_mask(canvas, vis):
    """Composite a background image onto canvas with fade mask."""
    # Scale to overfill canvas ~105%
    scale = max(CANVAS_W / vis.width, CANVAS_H / vis.height) * 1.05
    new_w = int(vis.width * scale)
    new_h = int(vis.height * scale)
    vis = vis.resize((new_w, new_h), Image.LANCZOS)

    # Centre-crop
    left = (new_w - CANVAS_W) // 2
    top  = (new_h - CANVAS_H) // 2
    if new_w >= CANVAS_W and new_h >= CANVAS_H:
        vis = vis.crop((left, top, left + CANVAS_W, top + CANVAS_H))
    else:
        # Image narrower than canvas: paste centred
        tmp = Image.new("RGB", (CANVAS_W, CANVAS_H), CREAM)
        paste_x = max(0, (CANVAS_W - new_w) // 2)
        paste_y = max(0, (CANVAS_H - new_h) // 2)
        crop_vis = vis.crop((max(0, -paste_x), max(0, -paste_y),
                             min(new_w, CANVAS_W), min(new_h, CANVAS_H)))
        tmp.paste(crop_vis, (paste_x, paste_y))
        vis = tmp

    # Alpha mask: full opacity at edges, fading in upper region
    mask = Image.new("L", (CANVAS_W, CANVAS_H), 255)
    mask_draw = ImageDraw.Draw(mask)

    cx, cy = CANVAS_W // 2, int(CANVAS_H * 0.30)
    ew, eh = int(CANVAS_W * 0.55), int(CANVAS_H * 0.40)

    for i in range(50):
        frac = i / 50.0
        alpha = int(255 * (0.25 + 0.75 * frac))
        sw = int(ew * (1 - frac))
        sh = int(eh * (1 - frac))
        bbox = (cx - sw, cy - sh, cx + sw, cy + sh)
        mask_draw.ellipse(bbox, fill=alpha)

    # Edge vignette
    border = int(CANVAS_W * 0.03)
    for i in range(border):
        frac = i / border
        alpha = int(255 * frac)
        mask_draw.rectangle([i, i, CANVAS_W - 1 - i, CANVAS_H - 1 - i],
                            outline=alpha)

    canvas.paste(vis, (0, 0), mask)
    return canvas


def draw_title(canvas, lines):
    """Overlay title text with cream halo for legibility."""
    draw = ImageDraw.Draw(canvas)

    total_h = 0
    line_spacing = 14
    rendered = []
    for text, size in lines:
        font = ImageFont.truetype(FONT_PATH, size)
        bbox = draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        rendered.append((text, font, w, h))
        total_h += h + line_spacing
    total_h -= line_spacing

    y = int(CANVAS_H * 0.06)

    for text, font, w, h in rendered:
        x = (CANVAS_W - w) // 2
        # Cream halo (radius ~3px)
        for ox in range(-3, 4):
            for oy in range(-3, 4):
                if ox * ox + oy * oy <= 9:
                    draw.text((x + ox, y + oy), text, font=font,
                              fill=CREAM + (220,))
        draw.text((x, y), text, font=font, fill=NAVY)
        y += h + line_spacing

    return canvas


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--title", required=True,
                        help="Paper title (will be uppercased)")
    parser.add_argument("--output", required=True,
                        help="Output PNG path")
    parser.add_argument("--background", default=None,
                        help="Optional background image (figure or illustration)")
    parser.add_argument("--lines", nargs="*", default=None,
                        help="Manual title lines as 'TEXT:SIZE' pairs, "
                             "e.g. 'RISK SHARING:78' 'IN VILLAGES:58'")
    args = parser.parse_args()

    canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), CREAM)

    if args.background:
        bg = Image.open(args.background).convert("RGB")
        canvas = apply_alpha_mask(canvas, bg)

    if args.lines:
        title_lines = []
        for spec in args.lines:
            text, size = spec.rsplit(":", 1)
            title_lines.append((text, int(size)))
    else:
        title_lines = make_title_lines(args.title)

    canvas = draw_title(canvas, title_lines)
    canvas.save(args.output, "PNG")
    print(f"Saved {CANVAS_W}x{CANVAS_H} cover to {args.output}")


if __name__ == "__main__":
    main()
