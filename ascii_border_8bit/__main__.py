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

    # ASCII canvas
    ascii_canvas = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(ascii_canvas)
    chars = args.chars
    n_chars = len(chars)
    # Precompute grayscale thumbnail for brightness
    gs = img.convert("L").resize((cols, rows), resample=Image.BILINEAR)
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
            draw.text((px, py), ch, font=font, fill=fill)

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

    # Determine region thickness
    bc = args.border
    qc = args.quant if args.quant is not None else bc
    if bc < 0 or qc < 0:
        print("--border and --quant must be non-negative", file=sys.stderr)
        sys.exit(1)
    max_d = min(cols, rows) // 2
    if bc + qc > max_d:
        print("Combined border exceeds image size.", file=sys.stderr)
        sys.exit(1)

    # Build cell-level masks for ascii and quant regions
    cell_mask_ascii = Image.new("L", (cols, rows), 0)
    cell_mask_quant = Image.new("L", (cols, rows), 0)
    for y in range(rows):
        for x in range(cols):
            d = min(x, cols-1-x, y, rows-1-y)
            if d < bc:
                cell_mask_ascii.putpixel((x, y), 255)
            elif d < bc + qc:
                cell_mask_quant.putpixel((x, y), 255)
    # Upscale masks to full resolution
    mask_ascii = cell_mask_ascii.resize((width, height), resample=Image.NEAREST)
    mask_quant = cell_mask_quant.resize((width, height), resample=Image.NEAREST)

    # Composite layers: start with original, paste quant, then ascii
    result = img.copy()
    result.paste(quant_canvas, (0, 0), mask_quant)
    result.paste(ascii_canvas, (0, 0), mask_ascii)

    # Save output
    try:
        result.save(args.output)
        print(f"Saved composite image to {args.output}")
    except Exception as e:
        print(f"Error saving output image: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":  # pragma: no cover
    main()