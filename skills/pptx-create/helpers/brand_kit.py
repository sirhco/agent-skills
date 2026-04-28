"""Brand kit loader.

A brand.toml in the working directory (or path passed explicitly) overrides
theme accent / logo / footer / font for every deck built in that dir.

Schema:
    accent = "#635BFF"
    logo_path = "/abs/path/logo.png"
    logo_position = "tr"          # tl|tr|bl|br
    footer_text = "Acme Confidential"
    font = "Calibri"
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional


def _toml_loader():
    try:
        import tomllib  # py3.11+
        return tomllib
    except ImportError:
        try:
            import tomli as tomllib  # type: ignore
            return tomllib
        except ImportError:
            return None


def load_brand_kit(path: Optional[str] = None) -> dict:
    """Load brand.toml. If path is None, try ./brand.toml. Returns {} if absent."""
    tomllib = _toml_loader()
    if tomllib is None:
        return {}
    p = Path(path) if path else Path.cwd() / "brand.toml"
    if not p.is_file():
        return {}
    try:
        data = tomllib.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"warn: brand.toml parse failed: {e}")
        return {}
    return {k: v for k, v in data.items() if v is not None}
