# 8-bit Color Quantization Filter

This tool reduces an image to an 8-bit (256-color) palette using median-cut quantization,
optionally applying Floyd–Steinberg dithering.

Requirements:
- Python 3
- Pillow

Installation:
```bash
pip install Pillow
```

Usage:
```bash
python -m eightbit_filter INPUT_IMAGE OUTPUT_IMAGE [--colors N] [--dither]
```

Arguments:
- `--colors`: Number of colors in the output palette (default: 256).
- `--dither`: Enable Floyd–Steinberg dithering (off by default).

Example:
```bash
python -m eightbit_filter photo.jpg output.png --colors 128 --dither
```