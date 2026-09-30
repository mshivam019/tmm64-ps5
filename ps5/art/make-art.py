#!/usr/bin/env python3
"""Generate PS5 launcher art for 2 Ship 2 Harkinian from the official 2S2H icon.

Outputs (next to this script):
  icon0.png            512x512 RGB launcher icon
  pic0-source.png      3840x2160 selection background (converted to pic0.dds)
  pic1-source.png      3840x2160 launch background   (converted to pic1.dds)
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
SRC = Image.open(HERE / "2s2hIcon-source.png").convert("RGBA")

# The icon's flat purple background; everything else is the ship artwork.
BG = (157, 107, 167)
SKY_TOP = (172, 126, 196)
SKY_BOTTOM = (120, 78, 138)
NIGHT = (26, 16, 44)

TITLE_FONT = "/usr/share/fonts/opentype/cantarell/Cantarell-Bold.otf"
BODY_FONT = "/usr/share/fonts/opentype/cantarell/Cantarell-Regular.otf"


def vertical_gradient(size, top, bottom):
    w, h = size
    column = Image.new("RGB", (1, h))
    for y in range(h):
        t = y / max(h - 1, 1)
        column.putpixel((0, y), tuple(round(a + (b - a) * t) for a, b in zip(top, bottom)))
    return column.resize((w, h))


def ship_only(fade_bottom=True):
    """The ship artwork with the flat purple background removed (transparent sky)."""
    tile = SRC.copy()
    px = tile.load()
    mask = Image.new("L", tile.size, 0)
    mp = mask.load()
    for y in range(tile.height):
        for x in range(tile.width):
            pr, pg, pb, pa = px[x, y]
            is_bg = max(abs(pr - BG[0]), abs(pg - BG[1]), abs(pb - BG[2])) < 46
            mp[x, y] = 0 if is_bg or pa < 16 else pa
    mask = mask.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
    fade = Image.new("L", tile.size, 255)
    if not fade_bottom:
        tile.putalpha(mask)
        return tile
    fd = ImageDraw.Draw(fade)
    for i in range(90):
        fd.line((0, tile.height - 1 - i, tile.width, tile.height - 1 - i), fill=round(255 * i / 90))
    mask = Image.composite(mask, Image.new("L", tile.size, 0), fade)
    tile.putalpha(mask)
    return tile


def make_icon():
    base = vertical_gradient((512, 512), SKY_TOP, SKY_BOTTOM).convert("RGBA")
    ship = ship_only(fade_bottom=False).resize((512, 512), Image.LANCZOS)
    base.alpha_composite(ship)
    base.convert("RGB").resize((512, 512), Image.LANCZOS).save(HERE / "icon0.png", optimize=True)


def make_background(name, ship_box, title_xy, title_size, subtitle, align="left"):
    W, H = 3840, 2160
    bg = vertical_gradient((W, H), SKY_TOP, NIGHT).convert("RGBA")

    # Soft light behind the ship.
    glow = Image.new("L", (W, H), 0)
    gx0, gy0, gx1, gy1 = ship_box
    pad = (gx1 - gx0) // 3
    ImageDraw.Draw(glow).ellipse((gx0 - pad, gy0 - pad, gx1 + pad, gy1 + pad), fill=110)
    glow = glow.filter(ImageFilter.GaussianBlur(220))
    bg.alpha_composite(Image.merge("RGBA", (
        Image.new("L", (W, H), 200), Image.new("L", (W, H), 170), Image.new("L", (W, H), 255), glow)))

    ship = ship_only().resize((gx1 - gx0, gy1 - gy0), Image.LANCZOS)
    shadow = Image.new("RGBA", ship.size, (0, 0, 0, 0))
    shadow.putalpha(ship.getchannel("A").point(lambda v: v * 0.45))
    shadow = shadow.filter(ImageFilter.GaussianBlur(28))
    bg.alpha_composite(shadow, (gx0 + 30, gy0 + 40))
    bg.alpha_composite(ship, (gx0, gy0))

    draw = ImageDraw.Draw(bg)
    title = ImageFont.truetype(TITLE_FONT, title_size)
    body = ImageFont.truetype(BODY_FONT, round(title_size * 0.34))
    lines = [("2 Ship 2", title), ("Harkinian", title)]
    x, y = title_xy
    for text, font in lines:
        tw = draw.textlength(text, font=font)
        tx = x - tw / 2 if align == "center" else x
        draw.text((tx + 8, y + 10), text, font=font, fill=(0, 0, 0, 120))
        draw.text((tx, y), text, font=font, fill=(255, 255, 255, 255))
        y += round(title_size * 1.02)
    y += round(title_size * 0.18)
    tw = draw.textlength(subtitle, font=body)
    tx = x - tw / 2 if align == "center" else x
    draw.text((tx, y), subtitle, font=body, fill=(228, 214, 255, 235))

    bg.convert("RGB").save(HERE / name, optimize=True)


if __name__ == "__main__":
    make_icon()
    # Selection background: ship on the right, title on the left.
    make_background("pic0-source.png", (2120, 330, 3700, 1910), (260, 640), 300,
                    "The Legend of Zelda: Majora's Mask  ·  PS5")
    # Launch background: ship centred above the title.
    make_background("pic1-source.png", (1420, 150, 2420, 1150), (1920, 1230), 250,
                    "The Legend of Zelda: Majora's Mask", align="center")
    print("ok")
