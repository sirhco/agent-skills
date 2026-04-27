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


def get_theme(name):
    if name not in THEMES:
        raise KeyError(f"unknown theme: {name!r}. options: {sorted(THEMES)}")
    return THEMES[name]


def list_themes():
    out = {"corporate": [], "pitch": []}
    seen = set()
    for k, v in THEMES.items():
        if v["name"] in seen:
            continue
        seen.add(v["name"])
        out[v["mode"]].append(v["name"])
    return out


if __name__ == "__main__":
    import json
    print(json.dumps(list_themes(), indent=2))
