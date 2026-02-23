"""
Crop & resize logos:
  1. Read every .png from logos_or/
  2. Trim away white and transparent padding from all sides
  3. Resize the cropped result to 110×110 px
  4. Save into logos/
"""

import os
from PIL import Image, ImageChops

INPUT_DIR = "logos_or"
OUTPUT_DIR = "logos"
TARGET_SIZE = (110, 110)


def _build_content_bbox(img):
    """Return the bounding box (left, top, right, bottom) of non-background pixels."""
    pixels = img.load()
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    mask_px = mask.load()

    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            # Treat as background if transparent or white-ish
            if a < 10 or (r > 240 and g > 240 and b > 240):
                mask_px[x, y] = 0
            else:
                mask_px[x, y] = 255

    return mask.getbbox()  # (left, top, right, bottom) or None


def trim_transparent_and_white(img):
    """
    Aspect-ratio-aware trim:
      - Square  (w == h): trim all sides
      - Tall    (h > w) : trim top & bottom, then remove the same amount from left & right
      - Wide    (w > h) : trim left & right, then remove the same amount from top & bottom
    """
    img = img.convert("RGBA")
    w, h = img.size

    bbox = _build_content_bbox(img)
    if not bbox:
        return img  # nothing to crop

    left, top, right, bottom = bbox

    if w == h:
        # Square — trim all sides normally
        return img.crop(bbox)
    elif h > w:
        # Tall — primary trim is top & bottom
        crop_top = top
        crop_bottom = h - bottom
        # Apply the same offsets to left & right
        new_left = crop_top
        new_right = w - crop_bottom
        return img.crop((new_left, top, new_right, bottom))
    else:
        # Wide — primary trim is left & right
        crop_left = left
        crop_right = w - right
        # Apply the same offsets to top & bottom
        new_top = crop_left
        new_bottom = h - crop_right
        return img.crop((left, new_top, right, new_bottom))


def process_logos():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    files = [f for f in os.listdir(INPUT_DIR)
             if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))]

    if not files:
        print(f"No image files found in {INPUT_DIR}/")
        return

    for fname in files:
        src = os.path.join(INPUT_DIR, fname)
        dst = os.path.join(OUTPUT_DIR, os.path.splitext(fname)[0] + ".png")

        img = Image.open(src).convert("RGBA")
        img = trim_transparent_and_white(img)
        # Fit inside TARGET_SIZE while preserving aspect ratio
        tw, th = TARGET_SIZE
        orig_w, orig_h = img.size
        scale = min(tw / orig_w, th / orig_h)
        new_w = int(orig_w * scale)
        new_h = int(orig_h * scale)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        # Centre on transparent canvas
        canvas = Image.new("RGBA", TARGET_SIZE, (0, 0, 0, 0))
        paste_x = (tw - new_w) // 2
        paste_y = (th - new_h) // 2
        canvas.paste(img, (paste_x, paste_y), img)
        canvas.save(dst, "PNG")
        print(f"  OK {fname} -> {dst}")

    print(f"\nDone! {len(files)} logos saved to {OUTPUT_DIR}/")


if __name__ == "__main__":
    process_logos()
