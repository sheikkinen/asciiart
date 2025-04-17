#!/usr/bin/env python3
"""
Composite filter: ASCII border, 8-bit mid-region, original center
"""
import argparse
import sys
from PIL import Image, ImageDraw, ImageFont

def parse_args():
    parser = argparse.ArgumentParser(
        description="Wrap image with ASCII-art border, 8-bit quantized mid-region, and original center.")
    parser.add_argument("input", help="Path to input image file")
    parser.add_argument("output", help="Path to save output image file")
    parser.add_argument(
        "--border", type=int, default=10,
        help="ASCII border thickness in characters (default: 10)")
    parser.add_argument(
        "--quant", type=int, default=None,
        help="8-bit region thickness in characters (default: same as --border)")
    parser.add_argument(
        "--font", help="Path to a .ttf font file for ASCII (default: PIL default font)")
    parser.add_argument(
        "--font_size", type=int, default=12,
        help="Font size for ASCII characters (default: 12)")
    parser.add_argument(
        "--chars", default="@%#*+=-:. ",
        help="Characters ordered dark-to-light for ASCII art (default: '@%#*+=-:. ')")
    parser.add_argument(
        "--color", action="store_true",
        help="Colorize ASCII characters sampling from original image")
    parser.add_argument(
        "--colors", type=int, default=256,
        help="Number of colors for 8-bit quantization (default: 256)")
    parser.add_argument(
        "--dither", action="store_true",
        help="Enable Floyd–Steinberg dithering for quantization")
    parser.add_argument(
        "--fade_ascii", type=int, default=None,
        help="Fade width in characters between ASCII and 8-bit region (default: same as --border)")
    parser.add_argument(
        "--fade_quant", type=int, default=None,
        help="Fade width in characters between 8-bit region and original (default: same as --quant)")
    parser.add_argument(
        "--radius", type=int, default=0,
        help="Corner rounding radius in characters for the ASCII border (default: 0)")
    return parser.parse_args()

def main():
    args = parse_args()
    # Load original image
    try:
        img = Image.open(args.input).convert("RGB")
    except Exception as e:
        print(f"Error opening input image: {e}", file=sys.stderr)
        sys.exit(1)
    width, height = img.size

    # Load font
    if args.font:
        try:
            font = ImageFont.truetype(args.font, args.font_size)
        except Exception as e:
            print(f"Error loading font '{args.font}': {e}", file=sys.stderr)
            sys.exit(1)
    else:
        try:
            font = ImageFont.load_default()
        except Exception:
            print("Could not load default font; specify --font", file=sys.stderr)
            sys.exit(1)

    # Character cell size
    try:
        bbox = font.getbbox("A")
        cell_w = bbox[2] - bbox[0]
        cell_h = bbox[3] - bbox[1]
    except AttributeError:
        mask = font.getmask("A")
        cell_w, cell_h = mask.size
    if cell_w <= 0 or cell_h <= 0:
        print("Invalid font cell size.", file=sys.stderr)
        sys.exit(1)

    # Grid dimensions
    cols = width // cell_w
    rows = height // cell_h
    if cols < 1 or rows < 1:
        print("Image too small for given font size.", file=sys.stderr)
        sys.exit(1)

    # Precompute grayscale thumbnail for ASCII mapping
    gs = img.convert("L").resize((cols, rows), resample=Image.BILINEAR)
    # Build ASCII canvas with white background
    ascii_canvas = Image.new("RGB", (width, height), color="white")
    draw_ascii = ImageDraw.Draw(ascii_canvas)
    chars = args.chars
    n_chars = len(chars)
    for y in range(rows):
        for x in range(cols):
            p = gs.getpixel((x, y))
            idx = p * (n_chars - 1) // 255
            ch = chars[idx]
            px = x * cell_w
            py = y * cell_h
            if args.color:
                fill = img.getpixel((min(px, width-1), min(py, height-1)))
            else:
                fill = (0, 0, 0)
            draw_ascii.text((px, py), ch, font=font, fill=fill)

    # 8-bit quantization canvas
    dither = Image.FLOYDSTEINBERG if args.dither else Image.NONE
    try:
        quant_canvas = img.quantize(
            colors=args.colors,
            method=Image.MEDIANCUT,
            dither=dither
        ).convert("RGB")
    except Exception as e:
        print(f"Error quantizing image: {e}", file=sys.stderr)
        sys.exit(1)

    # Determine region thickness and fade widths
    bc = args.border
    qc = args.quant if args.quant is not None else bc
    fade_a = args.fade_ascii if args.fade_ascii is not None else bc
    fade_q = args.fade_quant if args.fade_quant is not None else qc
    if bc < 0 or qc < 0:
        print("--border and --quant must be non-negative", file=sys.stderr)
        sys.exit(1)
    max_d = min(cols, rows) // 2
    if bc + qc > max_d:
        print("Combined border exceeds image size.", file=sys.stderr)
        sys.exit(1)
    # Determine rounding radius (in character cells), clamp to border thickness
    rr = max(0, args.radius)
    rr = min(rr, bc)

    # Build cell-level masks with fades
    cell_mask_ascii = Image.new("L", (cols, rows), 0)
    cell_mask_quant = Image.new("L", (cols, rows), 0)
    for y in range(rows):
        for x in range(cols):
            d = min(x, cols - 1 - x, y, rows - 1 - y)
            # ASCII fade region
            if fade_a > 0:
                if d <= bc - fade_a:
                    m1 = 255
                elif d < bc:
                    m1 = int(round((bc - d) * 255.0 / fade_a))
                else:
                    m1 = 0
            else:
                m1 = 255 if d < bc else 0
            # Apply corner rounding to ASCII mask: fill white background in rounded corners
            if rr > 0:
                # Top-left corner
                if x < rr and y < rr:
                    dx = rr - x - 0.5
                    dy = rr - y - 0.5
                    if dx*dx + dy*dy > rr*rr:
                        m1 = 255
                # Top-right corner
                elif x >= cols - rr and y < rr:
                    dx = x - (cols - rr) + 0.5
                    dy = rr - y - 0.5
                    if dx*dx + dy*dy > rr*rr:
                        m1 = 255
                # Bottom-left corner
                elif x < rr and y >= rows - rr:
                    dx = rr - x - 0.5
                    dy = y - (rows - rr) + 0.5
                    if dx*dx + dy*dy > rr*rr:
                        m1 = 255
                # Bottom-right corner
                elif x >= cols - rr and y >= rows - rr:
                    dx = x - (cols - rr) + 0.5
                    dy = y - (rows - rr) + 0.5
                    if dx*dx + dy*dy > rr*rr:
                        m1 = 255
            cell_mask_ascii.putpixel((x, y), max(0, min(255, m1)))
            # Quant fade region
            if d < bc:
                m2 = 0
            elif d < bc + fade_a and fade_a > 0:
                m2 = int(round((d - bc) * 255.0 / fade_a))
            elif d <= bc + qc - fade_q:
                m2 = 255
            elif d < bc + qc and fade_q > 0:
                m2 = int(round((bc + qc - d) * 255.0 / fade_q))
            else:
                m2 = 0
            # Apply corner rounding to quant region boundary (ascii-8bit transition)
            if rr > 0 and m2 > 0:
                # Quant region outer corners at distance bc from edge
                # Top-left
                if x < bc + rr and y < bc + rr:
                    dx = (bc + rr) - x - 0.5
                    dy = (bc + rr) - y - 0.5
                    if dx*dx + dy*dy > rr*rr:
                        m2 = 0
                # Top-right
                elif x >= cols - (bc + rr) and y < bc + rr:
                    dx = x - (cols - (bc + rr)) + 0.5
                    dy = (bc + rr) - y - 0.5
                    if dx*dx + dy*dy > rr*rr:
                        m2 = 0
                # Bottom-left
                elif x < bc + rr and y >= rows - (bc + rr):
                    dx = (bc + rr) - x - 0.5
                    dy = y - (rows - (bc + rr)) + 0.5
                    if dx*dx + dy*dy > rr*rr:
                        m2 = 0
                # Bottom-right
                elif x >= cols - (bc + rr) and y >= rows - (bc + rr):
                    dx = x - (cols - (bc + rr)) + 0.5
                    dy = y - (rows - (bc + rr)) + 0.5
                    if dx*dx + dy*dy > rr*rr:
                        m2 = 0
            cell_mask_quant.putpixel((x, y), max(0, min(255, m2)))
    # Upscale masks to full image size
    mask_ascii = cell_mask_ascii.resize((width, height), resample=Image.NEAREST)
    mask_quant = cell_mask_quant.resize((width, height), resample=Image.NEAREST)

    # Composite 8-bit region over original with fade
    try:
        base = Image.composite(quant_canvas, img, mask_quant)
    except Exception as e:
        print(f"Error compositing quant region: {e}", file=sys.stderr)
        sys.exit(1)
    # Composite ASCII canvas over quantized base with fade
    try:
        result = Image.composite(ascii_canvas, base, mask_ascii)
    except Exception as e:
        print(f"Error compositing ASCII region: {e}", file=sys.stderr)
        sys.exit(1)
    # Apply outer rounding to final image over white background
    if rr > 0:
        mask = Image.new("L", (width, height), 0)
        draw_mask = ImageDraw.Draw(mask)
        radius_px = rr * cell_w
        draw_mask.rounded_rectangle(
            [(0, 0), (width, height)], radius=radius_px, fill=255
        )
        white_bg = Image.new("RGB", (width, height), "white")
        result = Image.composite(result, white_bg, mask)
    # Save output
    try:
        result.save(args.output)
        print(f"Saved composite image to {args.output}")
    except Exception as e:
        print(f"Error saving output image: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":  # pragma: no cover
    main()