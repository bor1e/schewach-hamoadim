#!/usr/bin/env python3
"""
Extract all Hebrew text and footnotes from pdfs/schwach-hamoadim-Originaltext.pdf
into structured, parseable JSON files in data/hebrew/.

Combines:
  - pdftotext (Poppler) for clean Unicode BiDi text & footnote order
  - PyMuPDF (pymupdf) for reliable detection of part title pages (>=23pt)
    and Siman headings (18pt David-Bold standalone lines).
"""

import json
import re
import subprocess
from pathlib import Path
import pymupdf

ROOT = Path(__file__).resolve().parent.parent
PDF_PATH = ROOT / "pdfs" / "schwach-hamoadim-Originaltext.pdf"
OUT_DIR = ROOT / "data" / "hebrew"

GEMATRIA = {
    "א": 1, "ב": 2, "ג": 3, "ד": 4, "ה": 5, "ו": 6, "ז": 7, "ח": 8, "ט": 9,
    "י": 10, "כ": 20, "ך": 20, "ל": 30, "מ": 40, "ם": 40, "נ": 50, "ן": 50,
    "ס": 60, "ע": 70, "פ": 80, "ף": 80, "צ": 90, "ץ": 90,
    "ק": 100, "ר": 200, "ש": 300, "ת": 400,
}


BIDI_RE = re.compile(r"[\u200e\u200f\u202a-\u202e\u2066-\u2069\ufeff]")


def clean_line(s: str) -> str:
    return re.sub(r"\s+", " ", BIDI_RE.sub("", s)).strip()


def hebrew_to_int(s: str) -> int | None:
    s = re.sub(r'["״׳\']', "", s.strip())
    if not s or not all(c in GEMATRIA for c in s):
        return None
    return sum(GEMATRIA[c] for c in s)


def get_pdf_layout_hints(pdf_path: Path) -> tuple[set[int], dict[int, list[int]], dict[int, float]]:
    """Use PyMuPDF to find part title pages, Siman headings, and footnote y-boundaries per page."""
    doc = pymupdf.open(str(pdf_path))
    title_pages: set[int] = set()
    siman_headings: dict[int, list[int]] = {}
    fn_first_lines: dict[int, str] = {}

    for idx in range(len(doc)):
        pno = idx + 1
        d = doc[idx].get_text("dict")
        has_24pt = False
        has_kitzur = False
        min_fn_y = 9999.0
        first_fn_txt = ""
        for b in d["blocks"]:
            for l in b.get("lines", []):
                spans = l.get("spans", [])
                if not spans:
                    continue
                txt = "".join(s["text"] for s in spans).strip()
                if not txt:
                    continue
                max_sz = max(s["size"] for s in spans)
                y0 = l["bbox"][1]
                all_bold = all(("Bold" in s["font"] or (s["flags"] & 16)) for s in spans if s["text"].strip())
                if max_sz >= 23.0:
                    has_24pt = True
                if "קיצור" in txt and max_sz >= 17.0:
                    has_kitzur = True
                if max_sz >= 17.5 and all_bold and re.match(r"^[א-ת]{1,3}\.\s+\S+", clean_line(txt)):
                    m_s = re.match(r"^([א-ת]{1,3})\.", clean_line(txt))
                    if m_s and hebrew_to_int(m_s.group(1)):
                        siman_headings.setdefault(pno, []).append(hebrew_to_int(m_s.group(1)))
                # Footnote region: 9pt text (or 12pt "סימן X" in lower half)
                if y0 > 150 and (max_sz <= 10.5 or (max_sz <= 12.2 and clean_line(txt).startswith("סימן "))):
                    if y0 < min_fn_y:
                        min_fn_y = y0
                        first_fn_txt = clean_line(txt)
        if has_24pt and has_kitzur:
            title_pages.add(pno)
        if first_fn_txt:
            fn_first_lines[pno] = first_fn_txt

    return title_pages, siman_headings, fn_first_lines


def strip_running_header(lines: list[str]) -> list[str]:
    """Remove top running header ('שבח המועדים' and Hebrew page number)."""
    cleaned = []
    for i, line in enumerate(lines):
        s = clean_line(line)
        if not s:
            cleaned.append("")
            continue
        if i < 5:
            if s == "שבח המועדים":
                continue
            if len(s) <= 5 and all(c in GEMATRIA or c in '״"' for c in s) and s != "קיצור":
                continue
        # Also catch trailing reversed page numbers on title pages
        if len(s) <= 3 and all(c in GEMATRIA for c in s):
            continue
        cleaned.append(s)
    return cleaned


def split_body_and_footnotes(lines: list[str], fn_hint: str = "") -> tuple[list[str], list[str]]:
    """Split a page's lines into body lines and footnote lines."""
    fn_start = None
    if fn_hint:
        # Match by first 12 non-space chars of the first footnote line
        hint_key = re.sub(r"[\s\u0591-\u05c7]+", "", fn_hint)[:12]
        if len(hint_key) >= 4:
            for i, line in enumerate(lines):
                line_key = re.sub(r"[\s\u0591-\u05c7]+", "", line)
                if hint_key in line_key:
                    fn_start = i
                    break
    if fn_start is None:
        for i, line in enumerate(lines):
            if re.match(r"^סימן\s+[א-ת]{1,3}\s*$", line):
                fn_start = i
                break
    if fn_start is None:
        for i, line in enumerate(lines):
            if re.match(r"^(?:\)\d+|\d+\))\s*\S", line):
                fn_start = i
                break
    if fn_start is not None:
        return lines[:fn_start], lines[fn_start:]
    return lines, []


def attach_inline_fn_markers(text: str) -> str:
    """Convert trailing footnote digits (e.g. 'הַּנֵס.1' or 'טָהֹור,1') to {{fn:1}}."""
    # Match punctuation followed by 1-2 digits at word boundary or end
    return re.sub(r"([.,:;?!״\"\)])(\d{1,2})(?=\s|$)", r"\1{{fn:\2}}", text)


def parse_book(pdf_path: Path) -> dict:
    title_pages, siman_headings, fn_first_lines = get_pdf_layout_hints(pdf_path)
    raw_text = subprocess.check_output(["pdftotext", str(pdf_path), "-"]).decode("utf-8")
    raw_pages = raw_text.split("\x0c")

    parts = []
    current_part = None
    current_siman = None
    fn_siman = None
    current_seif = None
    current_para: list[str] = []
    current_fn_num: str | None = None
    current_fn_buf: list[str] = []

    def flush_para():
        nonlocal current_para
        if not current_para:
            return
        text = attach_inline_fn_markers(" ".join(current_para).strip())
        if current_seif is not None:
            current_seif["paragraphs"].append(text)
        elif current_siman is not None:
            current_siman["intro_paragraphs"].append(text)
        elif current_part is not None:
            current_part["intro_blocks"].append(text)
        current_para = []

    def flush_fn():
        nonlocal current_fn_num, current_fn_buf
        target = fn_siman or current_siman
        if current_fn_num is not None and target is not None:
            fn_text = " ".join(current_fn_buf).strip()
            if current_fn_num in target["footnotes"]:
                target["footnotes"][current_fn_num] += " " + fn_text
            else:
                target["footnotes"][current_fn_num] = fn_text
        current_fn_num = None
        current_fn_buf = []

    def ensure_part(title="קיצור הלכות ימים נוראים", page=1):
        nonlocal current_part
        if current_part is None:
            current_part = {
                "title": title,
                "start_page": page,
                "intro_blocks": [],
                "simanim": [],
            }
            parts.append(current_part)

    for idx, page_raw in enumerate(raw_pages):
        pno = idx + 1
        if pno >= 240:
            continue
        lines = strip_running_header(page_raw.splitlines())
        non_empty = [l for l in lines if l]
        if not non_empty:
            continue

        if pno in title_pages:
            flush_para()
            flush_fn()
            title_text = re.sub(r"\s+", " ", " ".join(non_empty)).strip()
            current_part = {
                "title": title_text,
                "start_page": pno,
                "intro_blocks": [],
                "simanim": [],
            }
            parts.append(current_part)
            current_siman = None
            current_seif = None
            continue

        ensure_part(page=pno)
        body_lines, fn_lines = split_body_and_footnotes(lines, fn_first_lines.get(pno, ""))
        page_siman_hdrs = set(siman_headings.get(pno, []))

        for line in body_lines:
            if not line:
                flush_para()
                continue

            norm_line = re.sub(r"\s+", " ", line).strip()

            # Check if this line is a Siman heading
            m_siman = re.match(r"^([א-ת]{1,3})[\u0591-\u05c7]*\s*\.\s*(.+)$", norm_line)
            siman_num = hebrew_to_int(m_siman.group(1)) if m_siman else None
            if siman_num is not None and siman_num in page_siman_hdrs:
                flush_para()
                heb_num = m_siman.group(1)
                if fn_siman is None:
                    fn_siman = current_siman
                current_siman = {
                    "number": siman_num,
                    "hebrew_number": heb_num,
                    "title": m_siman.group(2).strip(),
                    "start_page": pno,
                    "intro_paragraphs": [],
                    "sections": [],
                    "footnotes": {},
                }
                current_part["simanim"].append(current_siman)
                current_seif = None
                continue

            # Check if this line starts a Se'if (e.g. "א. הַמֶּלֶךְ בַּשָּׂדֶה — ...")
            m_seif = re.match(r"^([א-ת]{1,2})[\u0591-\u05c7]*\s*\.\s*(.+)$", norm_line)
            if m_seif and current_siman is not None and hebrew_to_int(m_seif.group(1)) is not None:
                # Avoid false positives like abbreviations; Se'if always starts at beginning of line
                # and usually has a short letter (1-2 chars) followed by ". " and a word >= 2 chars
                letter = m_seif.group(1)
                rest = m_seif.group(2).strip()
                if len(rest) >= 3:
                    flush_para()
                    if "—" in rest:
                        head, tail = rest.split("—", 1)
                        seif_title = head.strip()
                        first_text = tail.strip()
                    else:
                        seif_title = ""
                        first_text = rest
                    current_seif = {
                        "letter": letter,
                        "title": seif_title,
                        "page": pno,
                        "paragraphs": [],
                    }
                    current_siman["sections"].append(current_seif)
                    if first_text:
                        current_para.append(first_text)
                    continue

            current_para.append(norm_line)

        if current_para and current_para[-1].rstrip().endswith((".", ":", "!", "?", "״", '"')) and not current_para[-1].rstrip().endswith("וכו'"):
            flush_para()

        for fl in fn_lines:
            fl = fl.strip()
            if not fl:
                continue
            m_fn_siman = re.match(r"^סימן\s+([א-ת]{1,3})\s*$", fl)
            if m_fn_siman:
                flush_fn()
                snum = hebrew_to_int(m_fn_siman.group(1))
                for s in current_part["simanim"]:
                    if s["number"] == snum:
                        fn_siman = s
                        break
                continue
            if fn_siman is None:
                fn_siman = current_siman
            m_fn = re.match(r"^(?:\)(\d+)|(\d+)\))\s*(.*)$", fl)
            if m_fn:
                flush_fn()
                current_fn_num = m_fn.group(1) or m_fn.group(2)
                if m_fn.group(3).strip():
                    current_fn_buf.append(m_fn.group(3).strip())
            else:
                if current_fn_num is not None:
                    current_fn_buf.append(fl)

    flush_para()
    flush_fn()

    return {
        "source_pdf": pdf_path.name,
        "total_pages": len(raw_pages) - 1,
        "parts": parts,
    }


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    book = parse_book(PDF_PATH)

    full_path = OUT_DIR / "schewach-hamoadim.json"
    full_path.write_text(json.dumps(book, ensure_ascii=False, indent=2), encoding="utf-8")

    chanukka_parts = [p for p in book["parts"] if "חנוכה" in p["title"]]
    chanukka_path = OUT_DIR / "chanukka.json"
    chanukka_data = {
        "source_pdf": book["source_pdf"],
        "part": chanukka_parts[0] if chanukka_parts else None,
    }
    chanukka_path.write_text(json.dumps(chanukka_data, ensure_ascii=False, indent=2), encoding="utf-8")

    total_simanim = sum(len(p["simanim"]) for p in book["parts"])
    total_sections = sum(len(s["sections"]) for p in book["parts"] for s in p["simanim"])
    total_fns = sum(len(s["footnotes"]) for p in book["parts"] for s in p["simanim"])
    print(f"Extracted {len(book['parts'])} parts, {total_simanim} simanim, {total_sections} sections, {total_fns} footnotes.")
    for p in book["parts"]:
        print(f"  Part (p.{p['start_page']}): {p['title']} -> {len(p['simanim'])} simanim")
    if chanukka_parts:
        cp = chanukka_parts[0]
        print(f"Chanukka JSON written to {chanukka_path} ({len(cp['simanim'])} simanim, {len(cp['intro_blocks'])} intro blocks)")


if __name__ == "__main__":
    main()
