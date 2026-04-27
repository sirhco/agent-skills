"""Reference scaffold for pptx-create skill.

Usage as library:
    from helpers.build_deck import (
        Deck, title_slide, bullets_slide, big_stat_slide,
        chart_slide, image_slide, two_col_slide, table_slide,
        section_slide, quote_slide, cta_slide,
    )
    from themes.themes import get_theme
    d = Deck(theme=get_theme("stripe"))
    d.title("My deck", "Subtitle")
    d.bullets("Agenda", ["A", "B"])
    d.save("out.pptx")

Usage as script:
    python3 build_deck.py corporate   # build sample corporate deck
    python3 build_deck.py pitch       # build sample pitch deck
"""

import os
import sys
from pathlib import Path

# allow running as script or importing from neighbor dir
_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE

from themes.themes import get_theme, CORPORATE_DEFAULT, PITCH_NOIR


# ---------- primitives ----------

def add_text(slide, text, x, y, w, h, *, size=18, bold=False,
             color=None, align=PP_ALIGN.LEFT, font="Calibri",
             anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = text
    r.font.name = font
    r.font.size = Pt(size)
    r.font.bold = bold
    if color is not None:
        r.font.color.rgb = color
    return tb


def add_bg(slide, prs, color):
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0,
                                prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = color
    bg.line.fill.background()
    return bg


def add_rect(slide, x, y, w, h, color, line_color=None):
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    sh.fill.solid()
    sh.fill.fore_color.rgb = color
    if line_color is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line_color
    return sh


def add_notes(slide, text):
    if text:
        slide.notes_slide.notes_text_frame.text = text


def add_footer(slide, prs, theme, page_num=None, total=None, brand=""):
    """Bottom strip: brand left, page count right."""
    if brand:
        add_text(slide, brand, Inches(0.6), Inches(7.05), Inches(6), Inches(0.3),
                 size=10, color=theme["muted"], font=theme["font"])
    if page_num is not None:
        txt = f"{page_num}" if total is None else f"{page_num} / {total}"
        add_text(slide, txt, Inches(11.5), Inches(7.05), Inches(1.3), Inches(0.3),
                 size=10, color=theme["muted"], font=theme["font"],
                 align=PP_ALIGN.RIGHT)


# ---------- Deck class ----------

class Deck:
    def __init__(self, theme=None, brand=""):
        self.prs = Presentation()
        self.prs.slide_width = Inches(13.333)
        self.prs.slide_height = Inches(7.5)
        self.theme = theme or CORPORATE_DEFAULT
        self.brand = brand
        self._slide_index = 0

    def _new(self, with_footer=True):
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        add_bg(slide, self.prs, self.theme["bg"])
        self._slide_index += 1
        if with_footer and self._slide_index > 1:
            add_footer(slide, self.prs, self.theme,
                       page_num=self._slide_index, brand=self.brand)
        return slide

    # ---------- slide types ----------

    def title(self, title, subtitle="", notes=""):
        slide = self._new(with_footer=False)
        t = self.theme
        is_pitch = t["mode"] == "pitch"

        if is_pitch:
            add_text(slide, title, Inches(0.6), Inches(2.6), Inches(12), Inches(2.5),
                     size=84, bold=True, color=t["ink"], font=t["font"])
            if subtitle:
                add_text(slide, subtitle, Inches(0.6), Inches(5.5), Inches(12),
                         Inches(0.6), size=20, color=t["muted"], font=t["font"])
            # accent slash
            add_rect(slide, Inches(0.6), Inches(2.4), Inches(0.6), Inches(0.08),
                     t["accent"])
        else:
            add_rect(slide, Inches(0.6), Inches(2.0), Inches(0.6), Inches(0.08),
                     t["accent"])
            add_text(slide, title, Inches(0.6), Inches(2.4), Inches(12), Inches(1.5),
                     size=44, bold=True, color=t["ink"], font=t["font"])
            if subtitle:
                add_text(slide, subtitle, Inches(0.6), Inches(4.0), Inches(12),
                         Inches(0.6), size=20, color=t["muted"], font=t["font"])
        add_notes(slide, notes)
        return slide

    def section(self, label, number=None, notes=""):
        slide = self._new(with_footer=False)
        t = self.theme
        # full-bleed accent panel left third
        add_rect(slide, 0, 0, Inches(4.5), self.prs.slide_height, t["accent"])
        add_text(slide, label, Inches(5.0), Inches(3.0), Inches(8), Inches(2),
                 size=48, bold=True, color=t["ink"], font=t["font"])
        if number is not None:
            num = f"0{number}" if number < 10 else str(number)
            add_text(slide, num, Inches(0.6), Inches(0.6), Inches(2), Inches(0.6),
                     size=14, color=t["bg"], font=t["font"])
        add_notes(slide, notes)
        return slide

    def bullets(self, title, bullets, notes=""):
        slide = self._new()
        t = self.theme
        self._title_bar(slide, title)

        tb = slide.shapes.add_textbox(Inches(0.6), Inches(1.8), Inches(12),
                                      Inches(5))
        tf = tb.text_frame
        tf.word_wrap = True
        for i, b in enumerate(bullets):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = PP_ALIGN.LEFT
            p.space_after = Pt(14)
            r = p.add_run()
            r.text = f"•  {b}"
            r.font.name = t["font"]
            r.font.size = Pt(20)
            r.font.color.rgb = t["ink"]
        add_notes(slide, notes)
        return slide

    def two_col(self, title, left_title, left_items, right_title, right_items,
                notes=""):
        slide = self._new()
        t = self.theme
        self._title_bar(slide, title)

        for col, (h, items) in enumerate([(left_title, left_items),
                                          (right_title, right_items)]):
            x = Inches(0.6 + col * 6.2)
            add_text(slide, h, x, Inches(1.9), Inches(5.8), Inches(0.6),
                     size=16, bold=True, color=t["accent"], font=t["font"])
            tb = slide.shapes.add_textbox(x, Inches(2.6), Inches(5.8), Inches(4.5))
            tf = tb.text_frame
            tf.word_wrap = True
            for i, b in enumerate(items):
                p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
                p.space_after = Pt(10)
                r = p.add_run()
                r.text = f"•  {b}"
                r.font.name = t["font"]
                r.font.size = Pt(18)
                r.font.color.rgb = t["ink"]
        add_notes(slide, notes)
        return slide

    def big_stat(self, stat, caption, notes=""):
        slide = self._new(with_footer=False)
        t = self.theme
        add_text(slide, stat, Inches(0.6), Inches(1.5), Inches(12), Inches(3.5),
                 size=200, bold=True, color=t["accent"], font=t["font"])
        add_text(slide, caption, Inches(0.6), Inches(5.6), Inches(12), Inches(1),
                 size=22, color=t["ink"], font=t["font"])
        add_notes(slide, notes)
        return slide

    def quote(self, quote, attribution="", notes=""):
        slide = self._new()
        t = self.theme
        add_text(slide, f"“{quote}”", Inches(1.5), Inches(2.0),
                 Inches(10.3), Inches(3.5), size=32, bold=False,
                 color=t["ink"], font=t["font"])
        if attribution:
            add_text(slide, f"— {attribution}", Inches(1.5), Inches(5.5),
                     Inches(10.3), Inches(0.6),
                     size=16, color=t["muted"], font=t["font"])
        add_notes(slide, notes)
        return slide

    def chart(self, title, categories, series, *,
              chart_type=XL_CHART_TYPE.COLUMN_CLUSTERED, notes=""):
        """series: dict[name -> tuple of values]."""
        slide = self._new()
        self._title_bar(slide, title)
        data = CategoryChartData()
        data.categories = categories
        for name, values in series.items():
            data.add_series(name, values)
        slide.shapes.add_chart(
            chart_type,
            Inches(0.6), Inches(1.8), Inches(12), Inches(5), data
        )
        add_notes(slide, notes)
        return slide

    def table(self, title, headers, rows, notes=""):
        slide = self._new()
        t = self.theme
        self._title_bar(slide, title)
        n_rows = len(rows) + 1
        n_cols = len(headers)
        tbl = slide.shapes.add_table(
            n_rows, n_cols, Inches(0.6), Inches(1.9), Inches(12), Inches(5)
        ).table
        for c, h in enumerate(headers):
            cell = tbl.cell(0, c)
            cell.text = ""
            tf = cell.text_frame
            p = tf.paragraphs[0]
            r = p.add_run()
            r.text = h
            r.font.name = t["font"]
            r.font.size = Pt(14)
            r.font.bold = True
            r.font.color.rgb = t["bg"]
            cell.fill.solid()
            cell.fill.fore_color.rgb = t["accent"]
        for ri, row in enumerate(rows, start=1):
            for ci, val in enumerate(row):
                cell = tbl.cell(ri, ci)
                cell.text = ""
                tf = cell.text_frame
                p = tf.paragraphs[0]
                r = p.add_run()
                r.text = str(val)
                r.font.name = t["font"]
                r.font.size = Pt(13)
                r.font.color.rgb = t["ink"]
        add_notes(slide, notes)
        return slide

    def image(self, title, image_path, caption="", notes=""):
        slide = self._new()
        t = self.theme
        self._title_bar(slide, title)
        if image_path and os.path.exists(image_path):
            slide.shapes.add_picture(
                image_path, Inches(0.6), Inches(1.9), width=Inches(12)
            )
        else:
            add_text(slide, f"[image not found: {image_path}]",
                     Inches(0.6), Inches(3.5), Inches(12), Inches(0.6),
                     size=14, color=t["muted"], font=t["font"])
        if caption:
            add_text(slide, caption, Inches(0.6), Inches(6.6), Inches(12),
                     Inches(0.4), size=12, color=t["muted"], font=t["font"])
        add_notes(slide, notes)
        return slide

    def cta(self, headline, sub="", contact="", notes=""):
        slide = self._new(with_footer=False)
        t = self.theme
        add_rect(slide, 0, 0, self.prs.slide_width, self.prs.slide_height,
                 t["accent"])
        add_text(slide, headline, Inches(0.6), Inches(2.6), Inches(12),
                 Inches(2), size=64, bold=True, color=t["bg"],
                 font=t["font"])
        if sub:
            add_text(slide, sub, Inches(0.6), Inches(4.8), Inches(12),
                     Inches(0.8), size=24, color=t["bg"], font=t["font"])
        if contact:
            add_text(slide, contact, Inches(0.6), Inches(6.4), Inches(12),
                     Inches(0.6), size=16, color=t["bg"], font=t["font"])
        add_notes(slide, notes)
        return slide

    # ---------- internal ----------

    def _title_bar(self, slide, title):
        t = self.theme
        add_text(slide, title, Inches(0.6), Inches(0.6), Inches(12), Inches(0.9),
                 size=30, bold=True, color=t["ink"], font=t["font"])
        add_rect(slide, Inches(0.6), Inches(1.45), Inches(0.6), Inches(0.06),
                 t["accent"])

    # ---------- output ----------

    def save(self, path):
        self.prs.save(path)
        return path


# ---------- sample builds (run as script) ----------

def _sample_corporate(out="deck_corporate.pptx"):
    d = Deck(theme=get_theme("stripe"), brand="Acme Corp · 2026")
    d.title("Q3 Business Review",
            "Operations + Product · 2026-04-27",
            notes="Open with topline. 90s.")
    d.bullets("Agenda",
              ["Topline metrics", "Product highlights", "Risks", "Q4 plan"])
    d.section("Topline", number=1)
    d.chart("Revenue by quarter",
            ["Q1", "Q2", "Q3", "Q4 (proj)"],
            {"Revenue ($M)": (12.4, 15.1, 18.7, 22.0)},
            notes="Q3 beat plan by 8%.")
    d.table("Customer mix",
            ["Segment", "ARR ($M)", "Growth"],
            [["Enterprise", "11.2", "+34%"],
             ["Mid-market", "5.8", "+22%"],
             ["SMB", "1.7", "+11%"]])
    d.two_col("Risks vs Mitigations",
              "Risks", ["Hiring lag in EMEA", "One large customer at renewal",
                        "Infra cost trending up 12%"],
              "Mitigations", ["Open EMEA contractor pool", "Exec sponsor on account",
                              "Reserved capacity contracts"])
    d.quote("We don't ship to schedule. We ship when it's right.",
            attribution="CEO, all-hands 2026-Q1")
    d.cta("Q4 plan: ship billing v2",
          sub="Close 3 enterprise deals · Hire VP Eng · Reduce infra 8%")
    return d.save(out)


def _sample_pitch(out="deck_pitch.pptx"):
    d = Deck(theme=get_theme("pitch-noir"), brand="Ferro")
    d.title("Ferro", "AI dev tools that ship themselves.")
    d.big_stat("73%",
               "of engineering time is spent reading code, not writing it.")
    d.bullets("What we built",
              ["Autonomous PR review",
               "Zero-config setup",
               "Works with any stack"])
    d.big_stat("$1.2M", "ARR · 4 months · 38 customers")
    d.chart("Growth", ["M1", "M2", "M3", "M4"],
            {"ARR ($K)": (180, 420, 780, 1200)})
    d.cta("Raising $8M", sub="Seed · close 2026-06", contact="chris@ferro.ai")
    return d.save(out)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "corporate"
    path = _sample_pitch() if mode == "pitch" else _sample_corporate()
    prs = Presentation(path)
    print(f"saved: {path}")
    print(f"slides: {len(prs.slides)}")
    print(f"size:   {os.path.getsize(path)} bytes")
