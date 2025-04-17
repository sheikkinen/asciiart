#!/usr/bin/env node
import { promises as fs } from 'fs';
import { createCanvas } from 'canvas';

async function main() {
  const args = process.argv.slice(2);
  if (args.length < 2) {
    console.error('Usage: ascii2img <input.txt> <output.png> [--fontSize=<size>] [--padding=<px>]');
    console.error('Make sure to install dependencies: npm install canvas');
    process.exit(1);
  }
  const [inputFile, outputFile, ...opts] = args;
  let fontSize = 12;
  let padding = 10;
  for (const opt of opts) {
    if (opt.startsWith('--fontSize=')) {
      fontSize = parseInt(opt.split('=')[1], 10) || fontSize;
    } else if (opt.startsWith('--padding=')) {
      padding = parseInt(opt.split('=')[1], 10) || padding;
    }
  }

  // Read ASCII art from file
  const text = await fs.readFile(inputFile, 'utf8');
  const lines = text.split(/\r?\n/);
  const maxCols = lines.reduce((max, line) => Math.max(max, line.length), 0);

  // Measure character dimensions
  const tmpCanvas = createCanvas(0, 0);
  const tmpCtx = tmpCanvas.getContext('2d');
  tmpCtx.font = `${fontSize}px monospace`;
  const charWidth = tmpCtx.measureText('M').width;
  const lineHeight = fontSize * 1.2;

  // Calculate image size
  const width = Math.ceil(charWidth * maxCols + padding * 2);
  const height = Math.ceil(lineHeight * lines.length + padding * 2);

  const canvas = createCanvas(width, height);
  const ctx = canvas.getContext('2d');
  // Background
  ctx.fillStyle = 'white';
  ctx.fillRect(0, 0, width, height);
  // Text
  ctx.fillStyle = 'black';
  ctx.font = `${fontSize}px monospace`;
  ctx.textBaseline = 'top';
  lines.forEach((line, i) => {
    ctx.fillText(line, padding, padding + i * lineHeight);
  });

  // Output image
  const buffer = canvas.toBuffer('image/png');
  await fs.writeFile(outputFile, buffer);
  console.log(`Saved image to ${outputFile}`);
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});