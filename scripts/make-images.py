#!/usr/bin/env python3
"""Make the site's screen images: the app's screenshots inside Apple's devices.

    python3 scripts/make-images.py \\
        --design ~/DrinkTracker/docs/design/marketing-design-handoff \\
        --iphone-bezel "iPhone 17 - Black - Portrait.png" \\
        --watch-bezel "Apple Watch S11 - 46mm - Aluminum Jet Black + Sport Band Black.png"

Writes img/screens/ and img/og/home.png in this repository, and
img/press/tallyist-screenshots.zip.

The two bezels come from Apple's Product Bezels downloads
(https://developer.apple.com/design/resources/#product-bezels), which open only
after agreeing to Apple's License Agreement for Apple Design Resources. They are
never committed here: the license allows images of the app shown in the device,
not the device art passed on by itself. So every image this writes is flattened,
screenshot and device together, and the bezel files stay on the machine that
ran it.

Apple's marketing guidelines also ask that a device image be used whole, with
nothing cropped, tilted or added (no shadows), so none of that happens here.
The two cropped images (a close-up of the Today counter and of the widget) are
crops of screenshots, with no device in them.

Needs Pillow with WebP support. Deterministic for the same inputs.
"""

import argparse
import pathlib
import zipfile

from PIL import Image, ImageDraw, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parents[1]

# Phone screens: 1206 x 2622, the iPhone 17 family's opening.
PHONE_SCREENS = {
    "light": ["today", "calendar", "detail-sheet", "history", "trends", "settings", "session"],
    "dark": ["today", "calendar", "history", "trends", "settings", "session"],
}
PHONE_WIDTHS = (320, 640)      # displayed at up to 320 px, so 1x and 2x
WATCH_SCREENS = ["counter", "type-picker", "face-complication", "session-dots"]
WATCH_WIDTHS = (260, 520)      # the watch bezel is 560 px wide at its own size
CROP_WIDTHS = (300, 600)
# The press page shows plain screenshots, no device, for people placing them
# themselves; the zip beside them holds the originals.
PRESS_SCREENS = ["today", "calendar", "trends", "detail-sheet", "settings"]
PRESS_WIDTHS = (300, 600)

WEBP = dict(quality=84, method=6)


def opening(bezel, threshold=10):
    """The bezel's transparent screen opening, as a mask and its bounding box."""
    alpha = bezel.getchannel("A")
    m = alpha.point(lambda v: 255 if v <= threshold else 0)
    for seed in [(0, 0), (m.width - 1, 0), (0, m.height - 1), (m.width - 1, m.height - 1)]:
        if m.getpixel(seed) == 255:
            ImageDraw.floodfill(m, seed, 128)
    inside = m.point(lambda v: 255 if v == 255 else 0)
    return inside, inside.getbbox()


def in_device(shot_path, bezel):
    """The screenshot under the device, flattened, at the bezel's own size."""
    inside, box = opening(bezel)
    shot = Image.open(shot_path).convert("RGBA")
    want = (box[2] - box[0], box[3] - box[1])
    if shot.size != want:
        raise SystemExit(f"{shot_path}: {shot.size[0]}x{shot.size[1]}, the device's opening is {want[0]}x{want[1]}")
    layer = Image.new("RGBA", bezel.size, (0, 0, 0, 0))
    layer.paste(shot, box[:2])
    # A few pixels past the opening, so the bezel's anti-aliased inner edge
    # always sits over the screen rather than over nothing.
    mask = inside.filter(ImageFilter.MaxFilter(9))
    under = Image.composite(layer, Image.new("RGBA", bezel.size, (0, 0, 0, 0)), mask)
    return Image.alpha_composite(under, bezel)


def write(image, stem, widths, png_width):
    """WebP at every width; one PNG, at the smallest, for browsers without WebP."""
    stem.parent.mkdir(parents=True, exist_ok=True)
    for w in widths:
        h = round(image.height * w / image.width)
        image.resize((w, h), Image.LANCZOS).save(f"{stem}-{w}.webp", "WEBP", **WEBP)
    h = round(image.height * png_width / image.width)
    image.resize((png_width, h), Image.LANCZOS).save(f"{stem}-{png_width}.png", "PNG", optimize=True)


def square_crop(path, y_fraction):
    """A square from a portrait screenshot, as CSS object-position 50% y% would show it."""
    im = Image.open(path).convert("RGB")
    side = im.width
    top = round((im.height - side) * y_fraction)
    return im.crop((0, top, side, top + side))


def og_card(design, phone):
    """The link preview: the design's card, with the whole phone in place of its drawn one."""
    card = Image.open(design / "img/og/home.png").convert("RGBA")
    ground = card.getpixel((card.width - 4, 4))
    draw = ImageDraw.Draw(card)
    draw.rectangle((760, 0, card.width, card.height), fill=ground)
    h = card.height - 2 * 36
    w = round(phone.width * h / phone.height)
    small = phone.resize((w, h), Image.LANCZOS)
    x = 760 + (card.width - 760 - w) // 2
    card.alpha_composite(small, (x, 36))
    out = ROOT / "img/og/home.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    card.convert("RGB").save(out, "PNG", optimize=True)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--design", required=True, type=pathlib.Path)
    ap.add_argument("--iphone-bezel", required=True, type=pathlib.Path)
    ap.add_argument("--watch-bezel", required=True, type=pathlib.Path)
    args = ap.parse_args()
    design = args.design.expanduser()
    phone_bezel = Image.open(args.iphone_bezel).convert("RGBA")
    watch_bezel = Image.open(args.watch_bezel).convert("RGBA")
    out = ROOT / "img/screens"

    today_light = None
    for scheme, names in PHONE_SCREENS.items():
        for name in names:
            img = in_device(design / "source" / scheme / f"{name}.png", phone_bezel)
            write(img, out / scheme / name, PHONE_WIDTHS, PHONE_WIDTHS[0])
            if (scheme, name) == ("light", "today"):
                today_light = img
            print(f"{scheme}/{name}")

    for scheme in ("light", "dark"):
        crop = square_crop(design / "source" / scheme / "today.png", 0.22)
        write(crop, out / scheme / "today-close", CROP_WIDTHS, CROP_WIDTHS[0])
    widget = Image.open(design / "img/screens/light/widget-home.png").convert("RGB")
    write(widget, out / "light" / "widget", CROP_WIDTHS, CROP_WIDTHS[0])

    for name in WATCH_SCREENS:
        img = in_device(design / "img/screens/watch" / f"{name}.png", watch_bezel)
        write(img, out / "watch" / name, WATCH_WIDTHS, WATCH_WIDTHS[0])
        print(f"watch/{name}")

    print(og_card(design, today_light).relative_to(ROOT))

    for name in PRESS_SCREENS:
        shot = Image.open(design / "source/light" / f"{name}.png").convert("RGB")
        write(shot, ROOT / "img/press" / name, PRESS_WIDTHS, PRESS_WIDTHS[0])

    # The press kit's screenshots: the originals, without devices, for anyone
    # who needs to place them themselves.
    press = ROOT / "img/press/tallyist-screenshots.zip"
    press.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(press, "w", zipfile.ZIP_STORED) as z:
        for scheme in ("light", "dark"):
            for p in sorted((design / "source" / scheme).glob("*.png")):
                if p.name == "widget-home-full.png":
                    continue
                info = zipfile.ZipInfo(f"tallyist-screenshots/{scheme}/{p.name}", date_time=(2026, 9, 24, 0, 0, 0))
                z.writestr(info, p.read_bytes())
    print(press.relative_to(ROOT))


if __name__ == "__main__":
    main()
