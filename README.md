# ASCII Art Toolkit

A collection of command-line tools for converting and styling images and ASCII art.

## Contents
- **ascii_border**: Python CLI to wrap an image with an ASCII-art border while preserving the original center.
- **ascii_border_8bit**: Python CLI to wrap an image with an ASCII-art border, a quantized 8-bit mid-region, and preserve the original center.
- **eightbit_filter**: Python CLI to quantize images to an 8-bit (256-color) palette with optional dithering.
- **samples**: Directory containing example input and output images.
- **tests**: Directory containing automated unit tests for the tools.

## Requirements
- **Python 3**
- **Pillow** (for Python tools)

## Setup
1. Clone this repository:
   ```bash
   git clone https://github.com/sheikkinen/asciiart.git
   cd asciiart
   ```
2. Install Python dependencies:
   ```bash
   pip install --upgrade Pillow
   ```

## Usage

### Python Tools
Each Python tool includes its own `README.md` in its directory.

#### ascii_border
```bash
python3 -m ascii_border \
    INPUT_IMAGE OUTPUT_IMAGE [--border N] [--fade N] [--font PATH] [--font_size SIZE] [--chars CHARS] [--color]
```

#### ascii_border_8bit
```bash
python3 -m ascii_border_8bit \
    INPUT_IMAGE OUTPUT_IMAGE [--border N] [--quant N] [--font PATH] [--font_size SIZE] \
    [--chars CHARS] [--color] [--colors M] [--dither] [--fade_ascii N] [--fade_quant N] [--radius N]
```

#### eightbit_filter
```bash
python3 -m eightbit_filter \
    INPUT_IMAGE OUTPUT_IMAGE [--colors N] [--dither]
```


## Testing

To run the automated Python test suite, ensure you have Pillow installed, then execute:
```bash
python3 -m unittest discover tests
```

## License
This project is released under the MIT License.