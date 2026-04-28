"""Icon resolver.

resolve_icon(name) returns Path to a PNG, or None if unavailable.

Lookup order:
1. helpers/icons/<name>.png  (drop your own here)
2. helpers/icons/<name>.svg  (rendered to PNG via cairosvg if installed; cached)
3. unicode glyph fallback rendered with Pillow if a known mapping exists
4. None
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

_HERE = Path(__file__).resolve().parent
_ICON_DIR = _HERE / "icons"
_CACHE_DIR = _ICON_DIR / "_cache"

# unicode fallback glyphs for common bullet icons
GLYPHS = {
    "check":    "✓",
    "x":        "✗",
    "star":     "★",
    "dot":      "●",
    "arrow":    "→",
    "warn":     "⚠",
    "info":     "ⓘ",
    "rocket":   "🚀",
    "shield":   "🛡",
    "zap":      "⚡",
    "heart":    "♥",
    "lock":     "🔒",
    "user":     "👤",
    "trend-up": "↗",
    "trend-down": "↘",
    "calendar": "📅",
    "money":    "💰",
}


def resolve_icon(name: str) -> Optional[Path]:
    if not name:
        return None
    name = name.strip().lower()

    # 1. direct PNG
    p = _ICON_DIR / f"{name}.png"
    if p.is_file():
        return p

    # 2. SVG rendered to PNG (cached)
    svg = _ICON_DIR / f"{name}.svg"
    if svg.is_file():
        cached = _CACHE_DIR / f"{name}.png"
        if cached.is_file():
            return cached
        try:
            import cairosvg  # type: ignore
            _CACHE_DIR.mkdir(parents=True, exist_ok=True)
            cairosvg.svg2png(url=str(svg), write_to=str(cached), output_width=128, output_height=128)
            return cached
        except ImportError:
            pass

    # 3. unicode glyph fallback
    glyph = GLYPHS.get(name)
    if glyph:
        cached = _CACHE_DIR / f"_glyph_{name}.png"
        if cached.is_file():
            return cached
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            return None
        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        # try common system font
        font = None
        for fp in ("/System/Library/Fonts/Apple Symbols.ttf",
                   "/System/Library/Fonts/Helvetica.ttc",
                   "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                   "C:/Windows/Fonts/seguisym.ttf"):
            try:
                font = ImageFont.truetype(fp, 96)
                break
            except OSError:
                continue
        if font is None:
            font = ImageFont.load_default()
        try:
            bbox = draw.textbbox((0, 0), glyph, font=font)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
        except AttributeError:
            w, h = font.getsize(glyph)
        draw.text(((128 - w) / 2, (128 - h) / 2), glyph, fill=(0, 0, 0, 255), font=font)
        img.save(cached)
        return cached

    return None


def list_icons() -> list[str]:
    """Names available via PNG/SVG file or unicode mapping."""
    names = set()
    if _ICON_DIR.is_dir():
        for p in _ICON_DIR.glob("*.png"):
            names.add(p.stem)
        for p in _ICON_DIR.glob("*.svg"):
            names.add(p.stem)
    names.update(GLYPHS.keys())
    return sorted(names)
