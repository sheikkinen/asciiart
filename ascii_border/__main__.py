#!/usr/bin/env python3
"""
ASCII Art Border

Wraps an existing image with an ASCII-art border, preserving the original center.
"""
import argparse
import sys
from PIL import Image, ImageDraw, ImageFont

def parse_args():
    parser = argparse.ArgumentParser(
        description="Add an ASCII art border to an image, preserving the original center.")
    parser.add_argument(
        "input", help="Path to the input image file")
    parser.add_argument(
        "output", help="Path to save the output image file")
    parser.add_argument(
        "--border", type=int, default=10,
        help="Border thickness in characters (default: 10)")
    parser.add_argument(
        "--font", help="Path to a .ttf font file (default: PIL default font)")
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
        "--fade", type=int, default=None,
        help="Fade width in characters (default: same as --border)")
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

    # Character cell size: use font metrics or mask as fallback
    try:
        # Preferred: getbbox returns (x0, y0, x1, y1)
        bbox = font.getbbox("A")
        cell_w = bbox[2] - bbox[0]
        cell_h = bbox[3] - bbox[1]
    except AttributeError:
        # Fallback: getmask returns an image of the glyph
        mask = font.getmask("A")
        cell_w, cell_h = mask.size

    # Grid size in characters
    cols = width // cell_w
    rows = height // cell_h
    if cols < 1 or rows < 1:
        print("Image too small for given font size.", file=sys.stderr)
        sys.exit(1)

    # Create grayscale thumbnail for ASCII conversion
    gs = img.convert("L").resize((cols, rows), resample=Image.BILINEAR)

    # Map brightness to ASCII chars
    chars = args.chars
    n_chars = len(chars)
    ascii_grid = []
    for y in range(rows):
        row = []
        for x in range(cols):
            pixel = gs.getpixel((x, y))
            idx = pixel * (n_chars - 1) // 255
            row.append(chars[idx])
        ascii_grid.append(row)

    # Prepare ASCII canvas on white background
    ascii_canvas = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(ascii_canvas)
    for y, row in enumerate(ascii_grid):
        for x, ch in enumerate(row):
            px = x * cell_w
            py = y * cell_h
            if args.color:
                fill = img.getpixel((min(px, width-1), min(py, height-1)))
            else:
                fill = (0, 0, 0)
            draw.text((px, py), ch, font=font, fill=fill)

    # Determine fade parameters (in character cells)
    border_chars = args.border
    fade_chars = args.fade if args.fade is not None else border_chars
    if fade_chars < 0:
        print("Fade width must be non-negative.", file=sys.stderr)
        sys.exit(1)
    if fade_chars > border_chars:
        fade_chars = border_chars

    # Build per-cell mask (low-res) and scale to full image
    # Mask value 255 = full ASCII, 0 = original image
    cell_mask = Image.new("L", (cols, rows), 0)
    for y in range(rows):
        for x in range(cols):
            d = min(x, cols - 1 - x, y, rows - 1 - y)
            if d >= border_chars:
                m = 0
            elif d < border_chars - fade_chars:
                m = 255
            else:
                m = int(round((border_chars - d) * 255.0 / fade_chars))
                m = max(0, min(255, m))
            cell_mask.putpixel((x, y), m)
    mask = cell_mask.resize((width, height), resample=Image.NEAREST)

    # Composite ASCII canvas over original image using mask
    try:
        result = Image.composite(ascii_canvas, img, mask)
    except Exception as e:
        print(f"Error compositing images: {e}", file=sys.stderr)
        sys.exit(1)

    # Save output
    try:
        result.save(args.output)
        print(f"Saved bordered image to {args.output}")
    except Exception as e:
        print(f"Error saving output image: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":  # pragma: no cover
    main()