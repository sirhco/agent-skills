"""Embed a TrueType font into a .pptx via direct OOXML manipulation.

python-pptx has no public API for this, so we open the saved .pptx as a zip,
add the font as ppt/fonts/font<N>.fntdata, register it in
[Content_Types].xml, presentation.xml.rels, and presentation.xml.

Limitations:
- TrueType (.ttf) only. OpenType .otf is rejected by PowerPoint when embedded.
- Embedding adds 100KB–1MB+ to the file. Skip for fonts already on the
  recipient's system (Calibri, Arial, etc.).
- Font license must permit embedding. We don't check OS/2 fsType — caller's
  responsibility.

API:
    embed_font(pptx_path, font_path, typeface=None) -> int
        Adds font to deck. Returns 0 on success, 1 on failure.
"""
from __future__ import annotations

import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

# Namespaces used in presentation.xml
NS_P = "http://schemas.openxmlformats.org/presentationml/2006/main"
NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_RELS = "http://schemas.openxmlformats.org/package/2006/relationships"
NS_CT = "http://schemas.openxmlformats.org/package/2006/content-types"

FONT_REL_TYPE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/font"
FONT_CONTENT_TYPE = "application/x-fontdata"


def embed_font(pptx_path: Path, font_path: Path, typeface: str | None = None) -> int:
    pptx_path = Path(pptx_path)
    font_path = Path(font_path)
    if not pptx_path.is_file():
        print(f"error: pptx not found: {pptx_path}", file=sys.stderr)
        return 1
    if not font_path.is_file():
        print(f"error: font not found: {font_path}", file=sys.stderr)
        return 1
    if font_path.suffix.lower() not in (".ttf",):
        print(f"warning: only .ttf is reliably supported by PowerPoint embedding "
              f"(got {font_path.suffix}); proceeding anyway.", file=sys.stderr)

    typeface = typeface or font_path.stem
    try:
        from lxml import etree
    except ImportError:
        print("error: lxml required for font embedding (pip install lxml).",
              file=sys.stderr)
        return 1

    work = Path(tempfile.mkdtemp(prefix="pptx_embed_"))
    try:
        # 1. extract pptx
        with zipfile.ZipFile(pptx_path, "r") as zin:
            zin.extractall(work)

        fonts_dir = work / "ppt" / "fonts"
        fonts_dir.mkdir(exist_ok=True)
        # determine next index
        existing = sorted(fonts_dir.glob("font*.fntdata"))
        next_idx = len(existing) + 1
        font_part_name = f"font{next_idx}.fntdata"
        # plain copy (skip metadata to avoid chflags errors on protected system fonts)
        shutil.copyfile(font_path, fonts_dir / font_part_name)

        # 2. update [Content_Types].xml
        ct_path = work / "[Content_Types].xml"
        ct_tree = etree.parse(str(ct_path))
        ct_root = ct_tree.getroot()
        # add Default for fntdata if missing
        defaults = ct_root.findall(f"{{{NS_CT}}}Default")
        if not any(d.get("Extension") == "fntdata" for d in defaults):
            etree.SubElement(ct_root, f"{{{NS_CT}}}Default", {
                "Extension": "fntdata",
                "ContentType": FONT_CONTENT_TYPE,
            })
        ct_tree.write(str(ct_path), xml_declaration=True, encoding="UTF-8", standalone=True)

        # 3. update ppt/_rels/presentation.xml.rels
        rels_path = work / "ppt" / "_rels" / "presentation.xml.rels"
        rels_tree = etree.parse(str(rels_path))
        rels_root = rels_tree.getroot()
        # next rId
        existing_ids = {r.get("Id") for r in rels_root.findall(f"{{{NS_RELS}}}Relationship")}
        n = 1
        while f"rId{n}" in existing_ids:
            n += 1
        new_rid = f"rId{n}"
        etree.SubElement(rels_root, f"{{{NS_RELS}}}Relationship", {
            "Id": new_rid,
            "Type": FONT_REL_TYPE,
            "Target": f"fonts/{font_part_name}",
        })
        rels_tree.write(str(rels_path), xml_declaration=True, encoding="UTF-8", standalone=True)

        # 4. update ppt/presentation.xml
        pres_path = work / "ppt" / "presentation.xml"
        pres_tree = etree.parse(str(pres_path))
        pres_root = pres_tree.getroot()

        # find or create embeddedFontLst
        emb_lst = pres_root.find(f"{{{NS_P}}}embeddedFontLst")
        if emb_lst is None:
            emb_lst = etree.SubElement(pres_root, f"{{{NS_P}}}embeddedFontLst")
            # reorder: must precede defaultTextStyle and modifyVerifier and extLst
            anchor_tags = ("defaultTextStyle", "modifyVerifier", "extLst")
            anchor = None
            for tag in anchor_tags:
                a = pres_root.find(f"{{{NS_P}}}{tag}")
                if a is not None:
                    anchor = a
                    break
            if anchor is not None:
                # move emb_lst above anchor
                pres_root.remove(emb_lst)
                anchor.addprevious(emb_lst)

        emb_font = etree.SubElement(emb_lst, f"{{{NS_P}}}embeddedFont")
        font_el = etree.SubElement(emb_font, f"{{{NS_P}}}font", {"typeface": typeface})
        regular = etree.SubElement(emb_font, f"{{{NS_P}}}regular", {f"{{{NS_R}}}id": new_rid})

        pres_tree.write(str(pres_path), xml_declaration=True, encoding="UTF-8", standalone=True)

        # 5. repack zip
        out_tmp = pptx_path.with_suffix(".pptx.tmp")
        with zipfile.ZipFile(out_tmp, "w", zipfile.ZIP_DEFLATED) as zout:
            for root, _dirs, files in __import__("os").walk(work):
                root_p = Path(root)
                for f in files:
                    abs_p = root_p / f
                    rel = abs_p.relative_to(work).as_posix()
                    zout.write(abs_p, rel)
        out_tmp.replace(pptx_path)
        print(f"+ embedded {typeface} ({font_path.name}) into {pptx_path}")
        return 0
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(prog="embed_font")
    ap.add_argument("pptx", help="target .pptx (modified in place)")
    ap.add_argument("font", help="path to .ttf font file")
    ap.add_argument("--typeface", help="typeface name (defaults to font filename stem)")
    args = ap.parse_args(argv)
    return embed_font(Path(args.pptx), Path(args.font), args.typeface)


if __name__ == "__main__":
    sys.exit(main())
