import sys
import os
import subprocess
import tempfile
import unittest

try:
    from PIL import Image, ImageChops, ImageFont, ImageDraw
except ImportError:
    Image = None
    ImageChops = None
    ImageFont = None

@unittest.skipUnless(Image, "Pillow is required for this test")
class TestAsciiBorder8bit(unittest.TestCase):
    """Automated tests for the ascii_border_8bit composite filter."""

    def test_rounded_corner_and_center(self):
        # Create verification directory for output images
        base_dir = os.path.dirname(__file__)
        verification_dir = os.path.join(base_dir, "verification")
        os.makedirs(verification_dir, exist_ok=True)
        # Prepare an input image with overlapping circles for variation
        with tempfile.TemporaryDirectory() as tmpdir:
            inp = os.path.join(tmpdir, "in.png")
            img = Image.new("RGB", (200, 200), color=(255, 255, 255))
            draw = ImageDraw.Draw(img)
            draw.ellipse((50, 50, 150, 150), fill=(255, 0, 0))  # red circle
            draw.ellipse((80, 80, 180, 180), fill=(0, 255, 0))  # green circle
            img.save(inp)
            # Parameters
            border = 4
            quant = 4
            fade_a = 1
            fade_q = 1
            font_size = 12
            chars = "@%#*+=-:. "
            colors = 8
            # Test radii: 0, equal to border, larger than border (clamped)
            radii = [0, border, border * 2]
            outputs = {}
            for r in radii:
                outp = os.path.join(verification_dir, f"out_r{r}.png")
                cmd = [
                    sys.executable, "-m", "ascii_border_8bit",
                    inp, outp,
                    "--border", str(border),
                    "--quant", str(quant),
                    "--radius", str(r),
                    "--fade_ascii", str(fade_a),
                    "--fade_quant", str(fade_q),
                    "--font_size", str(font_size),
                    "--chars", chars,
                    "--color",
                    "--colors", str(colors),
                    "--dither"
                ]
                subprocess.run(cmd, check=True)
                outputs[r] = outp
            # Load images
            img0 = Image.open(outputs[0])
            imgB = Image.open(outputs[border])
            imgL = Image.open(outputs[border * 2])
            # All outputs should have the same size
            self.assertEqual(img0.size, imgB.size)
            self.assertEqual(img0.size, imgL.size)
            w, h = img0.size
            # Center pixel should match the original input at center
            center_color = img.getpixel((w//2, h//2))
            for im in (img0, imgB, imgL):
                self.assertEqual(im.getpixel((w//2, h//2)), center_color)
            # Radius >= border should round top-left to white
            self.assertEqual(imgB.getpixel((0, 0)), (255, 255, 255))
            self.assertEqual(imgL.getpixel((0, 0)), (255, 255, 255))
            # radius=0 vs border should differ
            diff0B = ImageChops.difference(img0, imgB)
            self.assertIsNotNone(diff0B.getbbox())
            # border vs larger (clamped) should be identical
            diffBL = ImageChops.difference(imgB, imgL)
            self.assertIsNone(diffBL.getbbox())
            # Close images
            for im in (img0, imgB, imgL, diff0B, diffBL):
                try:
                    im.close()
                except Exception:
                    pass

    def test_ascii_quant_original_regions(self):
        """
        Verify that with single-space ASCII ramp, the ASCII border is white,
        the quantized mid-region is original blue, and the center is blue.
        """
        if not ImageFont:
            self.skipTest("Pillow ImageFont is required for this test")
        with tempfile.TemporaryDirectory() as tmpdir:
            inp = os.path.join(tmpdir, "in.png")
            outp = os.path.join(tmpdir, "out.png")
            # Create input image with overlapping circles
            img = Image.new("RGB", (200, 200), color=(255, 255, 255))
            draw = ImageDraw.Draw(img)
            draw.ellipse((50, 50, 150, 150), fill=(255, 0, 0))
            draw.ellipse((80, 80, 180, 180), fill=(0, 255, 0))
            img.save(inp)
            border = 2
            quant = 3
            # Run with blank ASCII (space), no fades, radius=0, no color/dither
            cmd = [
                sys.executable, "-m", "ascii_border_8bit",
                inp, outp,
                "--border", str(border),
                "--quant", str(quant),
                "--radius", "0",
                "--fade_ascii", "0",
                "--fade_quant", "0",
                "--font_size", "12",
                "--chars", " ",
            ]
            subprocess.run(cmd, check=True)
            out_img = Image.open(outp)
            # Determine cell size
            try:
                font = ImageFont.load_default()
                bbox = font.getbbox("A")
                cw = bbox[2] - bbox[0]
                ch = bbox[3] - bbox[1]
            except Exception:
                mask = font.getmask("A")
                cw, ch = mask.size
            w, h = out_img.size
            # Sample positions
            # ASCII region: center of first cell
            ax, ay = cw//2, ch//2
            # Quant region: just inside quant band after ASCII border
            qx, qy = w//2, border*ch + ch//2
            # Original region: center
            ox, oy = w//2, h//2
            # ASCII region should be white
            self.assertEqual(out_img.getpixel((ax, ay)), (255, 255, 255))
            # Quant region pixel matches original input (default colors=256)
            self.assertEqual(
                out_img.getpixel((qx, qy)), img.getpixel((qx, qy))
            )
            # Original region pixel matches original input
            self.assertEqual(
                out_img.getpixel((ox, oy)), img.getpixel((ox, oy))
            )
            out_img.close()

if __name__ == '__main__':
    unittest.main()