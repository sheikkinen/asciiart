#!/usr/bin/env python3
"""
8-bit Color Quantization Filter

Reduces an image to an 8-bit (256-color) palette using median-cut quantization.
Optionally applies dithering.
"""
import argparse
import sys
from PIL import Image

def parse_args():
    parser = argparse.ArgumentParser(
        description="Apply 8-bit color quantization filter to an image.")
    parser.add_argument(
        "input", help="Path to the input image file")
    parser.add_argument(
        "output", help="Path to save the output image file")
    parser.add_argument(
        "--colors", type=int, default=256,
        help="Number of colors in the output palette (default: 256)")
    parser.add_argument(
        "--dither", action="store_true",
        help="Enable dithering (Floyd–Steinberg) in quantization")
    return parser.parse_args()

def main():
    args = parse_args()

    # Load original image
    try:
        img = Image.open(args.input).convert("RGB")
    except Exception as e:
        print(f"Error opening input image: {e}", file=sys.stderr)
        sys.exit(1)

    # Quantize to 8-bit palette
    dither = Image.FLOYDSTEINBERG if args.dither else Image.NONE
    try:
        pal = img.quantize(
            colors=args.colors,
            method=Image.MEDIANCUT,
            dither=dither
        )
    except Exception as e:
        print(f"Error quantizing image: {e}", file=sys.stderr)
        sys.exit(1)

    # Convert back to RGB for saving
    out = pal.convert("RGB")

    # Save output image
    try:
        out.save(args.output)
        print(f"Saved 8-bit filtered image to {args.output}")
    except Exception as e:
        print(f"Error saving output image: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":  # pragma: no cover
    main()