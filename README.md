# ASCII Art Toolkit

A collection of command-line tools for converting and styling images and ASCII art.

## Contents
- **ascii_border**: Python CLI to wrap an image with an ASCII-art border while preserving the original center.
- **eightbit_filter**: Python CLI to quantize images to an 8-bit (256-color) palette with optional dithering.
- **ascii-art.mjs**: Node.js script to convert images into ASCII art printed to the console.
- **ascii2img.mjs**: Node.js script to render ASCII text files into PNG images.

## Requirements
- **Python 3**
- **Pillow** (for Python tools)
- **Node.js**
- **npm** (for installing Node dependencies)

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
3. Install Node.js dependencies:
   ```bash
   npm install
   ```

## Usage

### Python Tools
Each Python tool includes its own `README.md` in its directory.

#### ascii_border
```bash
python3 -m ascii_border \
    INPUT_IMAGE OUTPUT_IMAGE [--border N] [--fade N] [--font PATH] [--font_size SIZE] [--chars CHARS] [--color]
```

#### eightbit_filter
```bash
python3 -m eightbit_filter \
    INPUT_IMAGE OUTPUT_IMAGE [--colors N] [--dither]
```

### Node.js Scripts

#### ascii-art.mjs
```bash
node ascii-art.mjs <image_path> [width]
```

#### ascii2img.mjs
```bash
node ascii2img.mjs <input.txt> <output.png> [--fontSize=SIZE] [--padding=PX]
```

## License
This project is released under the MIT License.