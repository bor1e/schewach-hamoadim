#!/usr/bin/env python3
"""
Convert Schewach Hamoadim Markdown DSL files into Typst markup.
Lean MVP pipeline supporting:
  - YAML frontmatter
  - #, ##, ### headings
  - **bold**, *italic*, `hebrew` inline spans
  - {{fn:N}} inline footnote markers + :::footnote N blocks
  - :::redaktion editorial hint blocks (suppressed with --no-redaktion)
  - Ordered & unordered lists
"""

import argparse
import re
from pathlib import Path
import yaml


def escape_typst(text: str) -> str:
    """Escape Typst special characters in plain text."""
    text = text.replace("\\", "\\\\")
    for ch in ["#", "$", "@", "<", ">"]:
        text = text.replace(ch, "\\" + ch)
    return text


def format_inline(text: str, footnotes: dict[str, str], include_footnotes: bool = True) -> str:
    """Format inline Markdown (**bold**, *italic*, `hebrew`, {{fn:N}}) to Typst."""
    tokens: list[str] = []
    pos = 0
    pattern = re.compile(r"(\{\{fn:(\d+)\}\}|`([^`]+)`|\*\*([^*]+)\*\*|\*([^*]+)\*)")

    for m in pattern.finditer(text):
        if m.start() > pos:
            tokens.append(escape_typst(text[pos:m.start()]))

        if m.group(2) is not None:
            fn_num = m.group(2)
            if include_footnotes and fn_num in footnotes:
                fn_body = format_inline(footnotes[fn_num], footnotes, include_footnotes=False)
                tokens.append(f"#footnote[{fn_body}]")
        elif m.group(3) is not None:
            heb = escape_typst(m.group(3))
            tokens.append(f"#heb[{heb}]")
        elif m.group(4) is not None:
            bold = escape_typst(m.group(4))
            tokens.append(f"*{bold}*")
        elif m.group(5) is not None:
            ital = escape_typst(m.group(5))
            tokens.append(f"_{ital}_")

        pos = m.end()

    if pos < len(text):
        tokens.append(escape_typst(text[pos:]))

    return "".join(tokens)


def parse_markdown_file(path: Path) -> tuple[dict, list[tuple[str, str]], dict[str, str]]:
    """Parse frontmatter, body blocks, and :::footnote blocks from a Markdown file."""
    raw = path.read_text(encoding="utf-8")
    meta = {}
    body = raw

    if raw.startswith("---\n"):
        parts = raw.split("---\n", 2)
        if len(parts) == 3:
            meta = yaml.safe_load(parts[1]) or {}
            body = parts[2]

    lines = body.splitlines()
    blocks: list[tuple[str, str]] = []
    footnotes: dict[str, str] = {}

    i = 0
    para_buf: list[str] = []

    def flush_para():
        nonlocal para_buf
        if para_buf:
            blocks.append(("para", " ".join(para_buf).strip()))
            para_buf = []

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Custom ::: block
        if stripped.startswith(":::"):
            flush_para()
            header = stripped[3:].strip()
            inner: list[str] = []
            i += 1
            while i < len(lines) and lines[i].strip() != ":::":
                inner.append(lines[i])
                i += 1
            i += 1  # consume closing :::
            content = "\n".join(inner).strip()

            m_fn = re.match(r"^footnote\s+(\d+)$", header)
            if m_fn:
                footnotes[m_fn.group(1)] = re.sub(r"\s+", " ", content)
            elif header == "redaktion":
                blocks.append(("redaktion", content))
            elif header in ("note", "infobox"):
                blocks.append(("infobox", content))
            continue

        if not stripped:
            flush_para()
            i += 1
            continue

        if stripped.startswith("### "):
            flush_para()
            blocks.append(("h3", stripped[4:].strip()))
            i += 1
            continue
        if stripped.startswith("## "):
            flush_para()
            blocks.append(("h2", stripped[3:].strip()))
            i += 1
            continue
        if stripped.startswith("# "):
            flush_para()
            blocks.append(("h1", stripped[2:].strip()))
            i += 1
            continue

        # Ordered list item
        if re.match(r"^\d+\.\s+", stripped):
            flush_para()
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i].strip()):
                items.append(re.sub(r"^\d+\.\s+", "", lines[i].strip()))
                i += 1
            blocks.append(("olist", "\n".join(items)))
            continue

        # Unordered list item
        if stripped.startswith("- "):
            flush_para()
            items = []
            while i < len(lines) and lines[i].strip().startswith("- "):
                items.append(lines[i].strip()[2:].strip())
                i += 1
            blocks.append(("ulist", "\n".join(items)))
            continue

        para_buf.append(stripped)
        i += 1

    flush_para()
    return meta, blocks, footnotes


def render_blocks_to_typst(
    blocks: list[tuple[str, str]],
    footnotes: dict[str, str],
    include_redaktion: bool,
    include_footnotes: bool,
) -> str:
    out: list[str] = []
    for kind, content in blocks:
        if kind == "h1":
            out.append(f"= {format_inline(content, footnotes, include_footnotes)}\n")
        elif kind == "h2":
            out.append(f"== {format_inline(content, footnotes, include_footnotes)}\n")
        elif kind == "h3":
            out.append(f"=== {format_inline(content, footnotes, include_footnotes)}\n")
        elif kind == "para":
            out.append(f"{format_inline(content, footnotes, include_footnotes)}\n")
        elif kind == "olist":
            for item in content.splitlines():
                out.append(f"+ {format_inline(item, footnotes, include_footnotes)}")
            out.append("")
        elif kind == "ulist":
            for item in content.splitlines():
                out.append(f"- {format_inline(item, footnotes, include_footnotes)}")
            out.append("")
        elif kind == "redaktion":
            if include_redaktion:
                body = format_inline(re.sub(r"\s+", " ", content), footnotes, include_footnotes=False)
                out.append(f"#redaktion[{body}]\n")
        elif kind == "infobox":
            body = format_inline(re.sub(r"\s+", " ", content), footnotes, include_footnotes=False)
            out.append(f"#infobox[{body}]\n")
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description="Build Typst source from Schewach Hamoadim Markdown files.")
    parser.add_argument("files", nargs="+", help="Input Markdown files")
    parser.add_argument("-o", "--output", required=True, help="Output directory")
    parser.add_argument("--template", required=True, help="Typst template path")
    parser.add_argument("--version", default="", help="Version string")
    parser.add_argument("--no-redaktion", action="store_true", help="Hide :::redaktion blocks")
    parser.add_argument("--no-footnotes", action="store_true", help="Omit footnotes")
    args = parser.parse_args()

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    include_redaktion = not args.no_redaktion
    include_footnotes = not args.no_footnotes

    rendered_parts: list[str] = []
    for idx, f in enumerate(args.files):
        p = Path(f)
        meta, blocks, footnotes = parse_markdown_file(p)
        if idx > 0 and meta.get("pagebreak", True):
            rendered_parts.append("#pagebreak(weak: true)\n")
        rendered_parts.append(render_blocks_to_typst(blocks, footnotes, include_redaktion, include_footnotes))

    content_str = "\n".join(rendered_parts)

    tpl = Path(args.template).read_text(encoding="utf-8")
    tpl = tpl.replace("{{VERSION}}", args.version).replace("{{CONTENT}}", content_str)
    book_typ = out_dir / "book.typ"
    book_typ.write_text(tpl, encoding="utf-8")

    print(f"Generated {book_typ} ({len(args.files)} files)")


if __name__ == "__main__":
    main()
