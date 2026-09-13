"""Генерирует PNG-иконки для PWA без внешних шрифтов (только Pillow).

Запуск: python3 tools/make_icons.py [выходная_папка]
"""
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw

BRAND = (79, 93, 255, 255)
GOLD = (255, 204, 51, 255)
WHITE = (255, 255, 255, 255)


def draw_icon(size: int, maskable: bool = False) -> Image.Image:
    # Рисуем в 4x и уменьшаем — так линии получаются гладкими.
    s = size * 4
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if maskable:
        d.rectangle([0, 0, s, s], fill=BRAND)
        pad = s * 0.20  # безопасная зона для maskable
    else:
        d.rounded_rectangle([0, 0, s - 1, s - 1], radius=int(s * 0.22), fill=BRAND)
        pad = s * 0.12
    inner = s - 2 * pad
    c = s / 2
    arm = inner * 0.28
    w = int(inner * 0.14)
    for a in (45, 135):
        dx, dy = math.cos(math.radians(a)) * arm, math.sin(math.radians(a)) * arm
        d.line([(c - dx, c - dy), (c + dx, c + dy)], fill=WHITE, width=w)
        for x, y in ((c - dx, c - dy), (c + dx, c + dy)):
            d.ellipse([x - w / 2, y - w / 2, x + w / 2, y + w / 2], fill=WHITE)
    bar_h = inner * 0.09
    bar_y = c + arm + bar_h * 1.6
    d.rounded_rectangle([pad + inner * 0.08, bar_y, s - pad - inner * 0.08, bar_y + bar_h], radius=int(bar_h / 2), fill=GOLD)
    return img.resize((size, size), Image.LANCZOS)


def main() -> None:
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "icons")
    out.mkdir(parents=True, exist_ok=True)
    draw_icon(192).save(out / "icon-192.png")
    draw_icon(512).save(out / "icon-512.png")
    draw_icon(512, maskable=True).save(out / "icon-maskable-512.png")
    # apple-touch-icon: без прозрачности и без скруглений — iOS скругляет сам
    apple = Image.new("RGBA", (180, 180), BRAND)
    apple.alpha_composite(draw_icon(180, maskable=True))
    apple.convert("RGB").save(out / "apple-touch-icon.png")
    print("icons written to", out.resolve())


if __name__ == "__main__":
    main()
