from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "geomole.png"
OUTPUT = ROOT / "assets" / "geodebug-social-preview.jpg"

WIDTH = 640
HEIGHT = 320


def _font(path: str, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidate = Path(path)
    if candidate.exists():
        return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def main() -> None:
    source = Image.open(SOURCE).convert("RGB")

    background = (248, 247, 243)
    image = Image.new("RGB", (WIDTH, HEIGHT), background)

    # Keep the mascot readable at social-card size. The source art is square and
    # includes the full GeoMole lockup; this crop isolates the character.
    crop = source.crop((70, 20, 850, 930))
    scale = 340 / crop.height
    crop = crop.resize((int(crop.width * scale), 340), Image.Resampling.LANCZOS)
    image.paste(crop, (-5, -10))

    draw = ImageDraw.Draw(image)

    # Clean text panel.
    draw.rectangle((300, 0, WIDTH, HEIGHT), fill=background)

    # Light map/grid texture.
    grid = (217, 230, 228)
    for x in range(320, WIDTH + 1, 40):
        draw.line((x, 0, x, HEIGHT), fill=grid, width=1)
    for y in range(0, HEIGHT + 1, 40):
        draw.line((300, y, WIDTH, y), fill=grid, width=1)

    bold = _font("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 46)
    regular = _font("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 19)
    small = _font("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)

    x = 330
    y = 91
    draw.text((x, y), "Geo", font=bold, fill=(31, 41, 48))
    geo_width = draw.textlength("Geo", font=bold)
    draw.text((x + geo_width, y), "Debug", font=bold, fill=(20, 139, 130))

    draw.multiline_text(
        (332, 158),
        "Find the geographic bug,\nnot just the code bug.",
        font=regular,
        fill=(55, 73, 84),
        spacing=5,
    )

    # Half-pixel motif: small offset, visible consequence.
    line = (156, 179, 181)
    alert = (242, 102, 88)
    draw.rectangle((542, 35, 595, 88), outline=line, width=2)
    draw.line((568, 25, 568, 98), fill=line, width=2)
    draw.line((532, 61, 605, 61), fill=line, width=2)
    draw.line((560, 61, 576, 61), fill=alert, width=4)
    draw.line((568, 53, 568, 69), fill=alert, width=4)
    draw.text((600, 52), "0.5", font=small, fill=(80, 105, 110))

    draw.text(
        (333, 270),
        "GeoMole · small offsets, big bugs.",
        font=small,
        fill=(88, 108, 114),
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(
        OUTPUT,
        "JPEG",
        quality=88,
        optimize=True,
        progressive=True,
    )


if __name__ == "__main__":
    main()
