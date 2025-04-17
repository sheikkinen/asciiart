#!/usr/bin/env node
/*
  ascii-art.mjs
  Converts an image to ASCII art.

  Usage:
    node ascii-art.mjs <image_path> [width]

  Requires:
    npm install jimp
*/
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
// Import Jimp class and utility functions
const { Jimp, intToRGBA } = require('jimp');

async function main() {
  const args = process.argv.slice(2);
  if (args.length < 1) {
    console.error('Usage: node ascii-art.mjs <image_path> [width]');
    process.exit(1);
  }
  const [imagePath, widthArg] = args;
  const width = parseInt(widthArg, 10) || 80;

  try {
    const image = await Jimp.read(imagePath);
    const asciiChars = '@%#*+=-:. ';
    // Adjust height to account for character aspect ratio
    const charAspect = 0.5;
    const newHeight = Math.round(image.bitmap.height * (width / image.bitmap.width) * charAspect);
    // Resize image to desired dimensions (using object options for plugin-resize)
    image.resize({ w: width, h: newHeight });

    let output = '';
    for (let y = 0; y < image.bitmap.height; y++) {
      let line = '';
      for (let x = 0; x < image.bitmap.width; x++) {
        const hex = image.getPixelColor(x, y);
        // Convert integer color to RGBA components
        const { r, g, b } = intToRGBA(hex);
        const lum = 0.2126 * r + 0.7152 * g + 0.0722 * b;
        const idx = Math.floor((lum / 255) * (asciiChars.length - 1));
        line += asciiChars[idx];
      }
      output += line + '\n';
    }
    console.log(output);
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
}

main();

// End of file

// "q" task completed: no modifications were needed.

