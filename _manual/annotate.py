"""Numbered callouts on screenshots for the manual: the screenshot gets a margin, each marker sits in the
margin (or inside) with a thin line to the element it explains. Run on the device (PIL is installed there).
"""
import json
import sys

from PIL import Image, ImageDraw, ImageFont

PAD = 46
ORANGE = (255, 109, 0)
FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 17)
SMALL = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)


def annotate(src, dst, marks, hide=()):
    shot = Image.open(src).convert("RGB")
    d0 = ImageDraw.Draw(shot)
    for x0, y0, x1, y1, text in hide:
        d0.rectangle((x0, y0, x1, y1), fill=(21, 50, 58))
        d0.text((x0 + 2, y0 + 2), text, font=SMALL, fill=(157, 188, 194))
    w, h = shot.size
    img = Image.new("RGB", (w + 2 * PAD, h + 2 * PAD), "white")
    img.paste(shot, (PAD, PAD))
    d = ImageDraw.Draw(img)
    d.rectangle((PAD - 1, PAD - 1, PAD + w, PAD + h), outline=(160, 160, 160))
    for mx, my, tx, ty, n in marks:
        mx, my, tx, ty = mx + PAD, my + PAD, tx + PAD, ty + PAD
        d.line((mx, my, tx, ty), fill=ORANGE, width=3)
        d.ellipse((tx - 5, ty - 5, tx + 5, ty + 5), fill=ORANGE, outline="white")
        d.ellipse((mx - 15, my - 15, mx + 15, my + 15), fill=ORANGE, outline="white", width=2)
        d.text((mx, my), str(n), font=FONT, fill="white", anchor="mm")
    img.save(dst)


if __name__ == "__main__":
    spec = json.load(open(sys.argv[1]))
    for name, item in spec.items():
        annotate("shots/%s.png" % name, "ann/%s.png" % name, item["marks"], item.get("hide", []))
        print(name)
