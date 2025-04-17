# ASCII Art Border

This tool wraps an existing image with an ASCII-art border, preserving the original center.

Requirements:
- Python 3
- Pillow (PIL)

Installation:
```bash
pip install Pillow
```  

Usage:
```bash
python -m ascii_border INPUT_IMAGE OUTPUT_IMAGE [--border BORDER_SIZE] \
    [--fade FADE_SIZE] [--font FONT_PATH] [--font_size SIZE] [--chars CHARS] [--color]
```

Options:
- `--border`: Thickness of the border in characters (default: 10).
- `--font`: Path to a TrueType (.ttf) font file. If omitted, uses PIL's default font.
- `--font_size`: Font size for ASCII characters (default: 12).
- `--chars`: Characters ordered dark-to-light (default: "@%#*+=-:. ").
- `--color`: Sample color from original image for ASCII characters (monochrome by default).
- `--fade`: Fade width in characters; the border will transition from ASCII to the original image over this many character cells (default: same as --border).

Example:
```bash
python -m ascii_border photo.jpg output.png --border 15 \
    --font "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf" \
    --font_size 14 --color
```