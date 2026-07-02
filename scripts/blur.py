#!/usr/bin/env python3
"""Mask faces / plates / other-brand signage and export web images.
Originals in images/ are never modified; outputs go to images/web/."""
import os
from PIL import Image, ImageFilter

SRC = "images"
OUT = "images/web"
MAXW = 1600  # cap width for web

# output_name: (source_file, [ (x, y, w, h) as fractions of image w/h ])
# empty list = no masking, just re-encode/resize.
JOBS = {
    "hero.jpg":      ("S__52854819_0.jpg", []),
    "svc-home.jpg":  ("S__52854796_0.jpg", []),
    "svc-office.jpg":("S__52854810_0.jpg", []),  # + face region below
    "svc-heavy.jpg": ("S__52854811_0.jpg", []),
    "svc-waste.jpg": ("S__52854812_0.jpg", []),   # + plate region below
    "g01.jpg": ("S__52854819_0.jpg", []),
    "g02.jpg": ("S__52854797_0.jpg", []),         # + plate
    "g03.jpg": ("S__52854798_0.jpg", []),
    "g04.jpg": ("S__52854800_0.jpg", []),         # + plate
    "g05.jpg": ("S__52854803_0.jpg", []),
    "g06.jpg": ("S__52854804_0.jpg", []),
    "g07.jpg": ("S__52854806_0.jpg", []),         # + face
    "g08.jpg": ("S__52854811_0.jpg", []),
    "g09.jpg": ("S__52854812_0.jpg", []),         # + plate
    "g10.jpg": ("S__52854809_0.jpg", []),
    "g11.jpg": ("S__52854822_0.jpg", []),         # + signage
}

# Masking regions filled after viewing each source (Step 3). Keyed by SOURCE file.
# Values: list of (x, y, w, h) fractions in [0,1].
REGIONS = {
    "S__52854810_0.jpg": [(0.55, 0.22, 0.17, 0.16)],   # worker's face (hallway)
    "S__52854812_0.jpg": [(0.57, 0.86, 0.17, 0.06)],   # front license plate
    "S__52854797_0.jpg": [(0.34, 0.51, 0.13, 0.09)],   # rear license plate (garage)
    "S__52854800_0.jpg": [(0.29, 0.64, 0.10, 0.08)],   # rear license plate (outdoor)
    "S__52854806_0.jpg": [(0.50, 0.40, 0.22, 0.14)],   # worker's face (carrying bag)
    "S__52854822_0.jpg": [
        (0.00, 0.10, 0.24, 0.25),  # KFC signage
        (0.35, 0.30, 0.11, 0.12),  # 台新銀行 signage
        (0.48, 0.29, 0.11, 0.13),  # 台新證券 signage
    ],
}

def mask(img, regions):
    for (fx, fy, fw, fh) in regions:
        W, H = img.size
        box = (int(fx*W), int(fy*H), int((fx+fw)*W), int((fy+fh)*H))
        region = img.crop(box)
        # strong blur so features are unrecoverable
        region = region.filter(ImageFilter.GaussianBlur(radius=max(box[2]-box[0], box[3]-box[1]) // 8 + 8))
        img.paste(region, box)
    return img

def process():
    os.makedirs(OUT, exist_ok=True)
    for out_name, (src_name, _) in JOBS.items():
        src_path = os.path.join(SRC, src_name)
        img = Image.open(src_path).convert("RGB")
        img = mask(img, REGIONS.get(src_name, []))
        if img.width > MAXW:
            h = int(img.height * MAXW / img.width)
            img = img.resize((MAXW, h), Image.LANCZOS)
        img.save(os.path.join(OUT, out_name), "JPEG", quality=82, optimize=True)
        print(f"wrote {out_name} <- {src_name} regions={len(REGIONS.get(src_name, []))}")

if __name__ == "__main__":
    process()
