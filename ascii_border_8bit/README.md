# ASCII + 8-bit Composite Filter

This tool wraps an image with three nested regions:
- **ASCII-art border** using a customizable character ramp.
- **8-bit quantized mid-region** (median-cut palette reduction with optional dithering).
- **Original center** untouched.

## Requirements
- Python 3
- Pillow

## Installation
```bash
pip install Pillow
```

## Usage
```bash
python3 -m ascii_border_8bit \
    INPUT_IMAGE OUTPUT_IMAGE \
    [--border N] [--quant N] [--fade_ascii N] [--fade_quant N] \
    [--font PATH] [--font_size SIZE] [--chars CHARS] [--color] \
    [--colors M] [--dither] [--radius N]
```

### Arguments
- `--border`: ASCII border thickness in characters (default: 10).
- `--quant`: 8-bit region thickness in characters (default: same as `--border`).
- `--font`: Path to a TrueType (.ttf) font file for ASCII (default: PIL default font).
- `--font_size`: Font size for ASCII characters (default: 12).
- `--chars`: Characters ordered dark-to-light for ASCII art (default: "@%#*+=-:. ").
- `--color`: Colorize ASCII by sampling original pixel colors (off by default).
- `--colors`: Number of colors for 8-bit quantization (default: 256).
    - `--dither`: Enable Floyd–Steinberg dithering for quantization (off by default).
    - `--fade_ascii`: Fade width in characters between ASCII and 8-bit region (default: same as --border).
    - `--fade_quant`: Fade width in characters between 8-bit region and original (default: same as --quant).
    - `--radius`: Corner rounding radius in characters for the ASCII border (default: 0).

### Example
```bash
python3 -m ascii_border_8bit photo.jpg out.png \
    --border 12 --quant 8 \
    --font "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf" \
    --font_size 14 --chars "@%#*+=-:. " --color \
    --colors 64 --dither
```