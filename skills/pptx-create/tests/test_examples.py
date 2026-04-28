"""Snapshot tests: render each examples/*.py and hash structural summary.

First run creates the snapshot. Later runs compare and fail on drift.
Refresh with PPTX_SNAPSHOT_UPDATE=1 pytest.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent
sys.path.insert(0, str(_ROOT))

_EXAMPLES = sorted((_ROOT / "examples").glob("*.py"))
_SNAP_DIR = _HERE / "snapshots"


def _hash_summary(report: dict) -> dict:
    """Reduce inspect() report to structure-only summary, then hash."""
    summary = {
        "slide_count": report["slide_count"],
        "slides": [
            {
                "n": s["n"],
                "title": s["title"],
                "shape_kinds": sorted(sh["kind"] for sh in s["shapes"]),
            }
            for s in report["slides"]
        ],
    }
    payload = json.dumps(summary, sort_keys=True).encode("utf-8")
    return {
        "summary": summary,
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def _run_example(path: Path, out_dir: Path) -> Path:
    """Import the example as a module and call its main()/build()/save sequence."""
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    # examples may save to relative paths; chdir into out_dir
    cwd = os.getcwd()
    os.chdir(out_dir)
    try:
        spec.loader.exec_module(mod)  # type: ignore
        if hasattr(mod, "main"):
            mod.main()
        elif hasattr(mod, "build"):
            mod.build()
    finally:
        os.chdir(cwd)
    files = list(out_dir.glob("*.pptx"))
    if not files:
        raise RuntimeError(f"{path.name} did not produce a .pptx")
    return files[0]


@pytest.mark.parametrize("example", _EXAMPLES, ids=[p.stem for p in _EXAMPLES])
def test_example_snapshot(example: Path, tmp_path: Path):
    from helpers.inspect_deck import inspect

    deck = _run_example(example, tmp_path)
    report = inspect(str(deck))
    summary = _hash_summary(report)

    snap = _SNAP_DIR / f"{example.stem}.json"
    if os.environ.get("PPTX_SNAPSHOT_UPDATE") or not snap.is_file():
        _SNAP_DIR.mkdir(parents=True, exist_ok=True)
        snap.write_text(json.dumps(summary, indent=2, sort_keys=True))
        pytest.skip(f"snapshot created at {snap}")

    expected = json.loads(snap.read_text())
    assert summary["sha256"] == expected["sha256"], (
        f"snapshot drift for {example.stem}\n"
        f"  expected: {expected['sha256']}\n"
        f"  actual:   {summary['sha256']}\n"
        f"  refresh: PPTX_SNAPSHOT_UPDATE=1 pytest"
    )
