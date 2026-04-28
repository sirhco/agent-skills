"""Theme registry for pptx-create skill.

Each theme is a dict with: bg, ink, muted, accent, accent2, font, mode.
Pass into builder functions; helpers in helpers/build_deck.py consume same shape.

Usage:
    from themes import THEMES
    t = THEMES["stripe"]
"""

from pptx.dml.color import RGBColor


def _rgb(hex_str):
    h = hex_str.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


# ---------- corporate themes ----------

CORPORATE_DEFAULT = {
    "name": "corporate-default",
    "mode": "corporate",
    "bg":      _rgb("#FFFFFF"),
    "ink":     _rgb("#1A1A1A"),
    "muted":   _rgb("#5F6B7A"),
    "accent":  _rgb("#0B5FFF"),
    "accent2": _rgb("#E5EEFF"),
    "font":    "Calibri",
}

STRIPE = {  # purple-violet, clean, fintech
    "name": "stripe",
    "mode": "corporate",
    "bg":      _rgb("#FFFFFF"),
    "ink":     _rgb("#0A2540"),
    "muted":   _rgb("#425466"),
    "accent":  _rgb("#635BFF"),
    "accent2": _rgb("#EFEEFF"),
    "font":    "Calibri",
}

LINEAR = {  # near-black bg, sharp, dev-tools
    "name": "linear",
    "mode": "corporate",
    "bg":      _rgb("#0E0E10"),
    "ink":     _rgb("#F4F4F5"),
    "muted":   _rgb("#8E8E93"),
    "accent":  _rgb("#5E6AD2"),
    "accent2": _rgb("#1F1F23"),
    "font":    "Calibri",
}

MCKINSEY = {  # navy-and-white, consulting classic
    "name": "mckinsey",
    "mode": "corporate",
    "bg":      _rgb("#FFFFFF"),
    "ink":     _rgb("#051C2C"),
    "muted":   _rgb("#5A6F80"),
    "accent":  _rgb("#003A70"),
    "accent2": _rgb("#2251FF"),
    "font":    "Calibri",
}

APPLE = {  # mono with red accent
    "name": "apple",
    "mode": "corporate",
    "bg":      _rgb("#FFFFFF"),
    "ink":     _rgb("#1D1D1F"),
    "muted":   _rgb("#86868B"),
    "accent":  _rgb("#FF375F"),
    "accent2": _rgb("#F5F5F7"),
    "font":    "Calibri",
}

MONOCHROME = {  # zero accent — pure black/white/gray
    "name": "monochrome",
    "mode": "corporate",
    "bg":      _rgb("#FFFFFF"),
    "ink":     _rgb("#000000"),
    "muted":   _rgb("#666666"),
    "accent":  _rgb("#000000"),
    "accent2": _rgb("#E5E5E5"),
    "font":    "Calibri",
}

FINANCE = {  # green forest accent, traditional
    "name": "finance",
    "mode": "corporate",
    "bg":      _rgb("#FAFAF7"),
    "ink":     _rgb("#1B2A1B"),
    "muted":   _rgb("#5C6B5C"),
    "accent":  _rgb("#0F5132"),
    "accent2": _rgb("#D4E2D4"),
    "font":    "Calibri",
}

HEALTHCARE = {  # teal + soft warm
    "name": "healthcare",
    "mode": "corporate",
    "bg":      _rgb("#FCFCFA"),
    "ink":     _rgb("#0F2A36"),
    "muted":   _rgb("#5A7282"),
    "accent":  _rgb("#0E8388"),
    "accent2": _rgb("#E3F4F4"),
    "font":    "Calibri",
}


# ---------- pitch themes ----------

PITCH_NOIR = {  # dark + orange punch — default pitch
    "name": "pitch-noir",
    "mode": "pitch",
    "bg":      _rgb("#0A0A0A"),
    "ink":     _rgb("#F5F5F0"),
    "muted":   _rgb("#A0A09A"),
    "accent":  _rgb("#FF4D2E"),
    "accent2": _rgb("#1A1A1A"),
    "font":    "Calibri",
}

PITCH_EDITORIAL = {  # warm cream + burnt accent
    "name": "pitch-editorial",
    "mode": "pitch",
    "bg":      _rgb("#F5F1EA"),
    "ink":     _rgb("#1A1A1A"),
    "muted":   _rgb("#6B5F4F"),
    "accent":  _rgb("#C2410C"),
    "accent2": _rgb("#E8DFCF"),
    "font":    "Calibri",
}

PITCH_ELECTRIC = {  # near-black + lime — bold modern
    "name": "pitch-electric",
    "mode": "pitch",
    "bg":      _rgb("#0F1011"),
    "ink":     _rgb("#FAFAFA"),
    "muted":   _rgb("#888888"),
    "accent":  _rgb("#C7FF3D"),
    "accent2": _rgb("#1A1B1D"),
    "font":    "Calibri",
}

PITCH_VIOLET = {  # midnight purple, futurist
    "name": "pitch-violet",
    "mode": "pitch",
    "bg":      _rgb("#0E0B1F"),
    "ink":     _rgb("#FFFFFF"),
    "muted":   _rgb("#9B96B5"),
    "accent":  _rgb("#A78BFA"),
    "accent2": _rgb("#1A1535"),
    "font":    "Calibri",
}

PITCH_CLAY = {  # earthy terracotta
    "name": "pitch-clay",
    "mode": "pitch",
    "bg":      _rgb("#E8DDD0"),
    "ink":     _rgb("#2B1F17"),
    "muted":   _rgb("#7A6655"),
    "accent":  _rgb("#A0522D"),
    "accent2": _rgb("#D4C4B0"),
    "font":    "Calibri",
}


# ---------- registry ----------

THEMES = {
    "corporate":        CORPORATE_DEFAULT,
    "corporate-default": CORPORATE_DEFAULT,
    "stripe":           STRIPE,
    "linear":           LINEAR,
    "mckinsey":         MCKINSEY,
    "apple":            APPLE,
    "monochrome":       MONOCHROME,
    "finance":          FINANCE,
    "healthcare":       HEALTHCARE,
    "pitch":            PITCH_NOIR,
    "pitch-noir":       PITCH_NOIR,
    "pitch-editorial":  PITCH_EDITORIAL,
    "pitch-electric":   PITCH_ELECTRIC,
    "pitch-violet":     PITCH_VIOLET,
    "pitch-clay":       PITCH_CLAY,
}


_TOML_LOADED = False


def _load_toml_themes():
    """Read themes/*.toml, resolve `extends`, merge into THEMES."""
    global _TOML_LOADED
    if _TOML_LOADED:
        return
    _TOML_LOADED = True

    try:
        import tomllib  # py 3.11+
    except ImportError:
        try:
            import tomli as tomllib  # type: ignore
        except ImportError:
            return  # silently skip if no TOML reader

    from pathlib import Path
    here = Path(__file__).resolve().parent
    for toml in sorted(here.glob("*.toml")):
        try:
            data = tomllib.loads(toml.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"warn: failed to parse {toml.name}: {e}")
            continue
        name = data.get("name") or toml.stem
        base = {}
        ext = data.get("extends")
        if ext and ext in THEMES:
            base = dict(THEMES[ext])
        colors = data.get("colors", {})
        typ = data.get("type", {})
        brand = data.get("brand", {})
        merged = {
            "name": name,
            "mode": data.get("mode", base.get("mode", "corporate")),
            "bg":      _rgb(colors.get("bg",      _hex(base.get("bg",      "#FFFFFF")))),
            "ink":     _rgb(colors.get("ink",     _hex(base.get("ink",     "#1A1A1A")))),
            "muted":   _rgb(colors.get("muted",   _hex(base.get("muted",   "#666666")))),
            "accent":  _rgb(colors.get("accent",  _hex(base.get("accent",  "#0B5FFF")))),
            "accent2": _rgb(colors.get("accent2", _hex(base.get("accent2", "#E5EEFF")))),
            "font":    typ.get("font", base.get("font", "Calibri")),
        }
        if brand.get("logo_path"):
            merged["logo_path"] = brand["logo_path"]
            merged["logo_position"] = brand.get("logo_position", "tr")
        if brand.get("footer_text"):
            merged["footer_text"] = brand["footer_text"]
        if brand.get("background_image"):
            merged["background_image"] = brand["background_image"]
            merged["background_image_position"] = brand.get("background_image_position", "cover")
        if typ.get("font_path"):
            merged["font_path"] = typ["font_path"]
        THEMES[name] = merged


def _hex(rgb):
    if isinstance(rgb, str):
        return rgb
    if hasattr(rgb, "rgb"):
        # RGBColor; format as hex
        try:
            r = int(str(rgb), 16)
            return "#{:06X}".format(r)
        except Exception:
            return "#000000"
    return "#000000"


def _dark_variant(theme):
    """Swap bg/ink for a dark counterpart of a light theme."""
    out = dict(theme)
    out["bg"], out["ink"] = theme["ink"], theme["bg"]
    # darken accent2 for dark bg
    out["accent2"] = _rgb("#1A1A1A")
    out["mode_variant"] = "dark"
    return out


def _light_variant(theme):
    out = dict(theme)
    out["bg"], out["ink"] = theme["ink"], theme["bg"]
    out["accent2"] = _rgb("#F0F0F0")
    out["mode_variant"] = "light"
    return out


def _is_dark_theme(theme):
    """Heuristic: bg luminance < 0.5 -> already dark."""
    bg = theme["bg"]
    try:
        r, g, b = int(str(bg)[0:2], 16), int(str(bg)[2:4], 16), int(str(bg)[4:6], 16)
    except Exception:
        return False
    luma = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
    return luma < 0.5


def get_theme(name, *, mode=None, brand=None):
    """Return theme dict by name. mode='dark'|'light' flips variant. brand= dict overrides accent/logo/footer."""
    _load_toml_themes()
    if name not in THEMES:
        raise KeyError(f"unknown theme: {name!r}. options: {sorted(set(t['name'] for t in THEMES.values()))}")
    theme = dict(THEMES[name])
    if mode == "dark" and not _is_dark_theme(theme):
        theme = _dark_variant(theme)
    elif mode == "light" and _is_dark_theme(theme):
        theme = _light_variant(theme)
    if brand:
        if brand.get("accent"):
            theme["accent"] = _rgb(brand["accent"])
        if brand.get("logo_path"):
            theme["logo_path"] = brand["logo_path"]
            theme["logo_position"] = brand.get("logo_position", "tr")
        if brand.get("footer_text"):
            theme["footer_text"] = brand["footer_text"]
        if brand.get("font"):
            theme["font"] = brand["font"]
    return theme


def list_themes():
    """Return sorted list of unique theme names."""
    _load_toml_themes()
    seen = set()
    out = []
    for k, v in THEMES.items():
        if v["name"] in seen:
            continue
        seen.add(v["name"])
        out.append(v["name"])
    return sorted(out)


def list_themes_detailed():
    """Return list of dicts: {name, mode}."""
    _load_toml_themes()
    seen = set()
    out = []
    for k, v in THEMES.items():
        if v["name"] in seen:
            continue
        seen.add(v["name"])
        out.append({"name": v["name"], "mode": v["mode"]})
    return sorted(out, key=lambda d: (d["mode"], d["name"]))


if __name__ == "__main__":
    import json
    print(json.dumps(list_themes_detailed(), indent=2))
