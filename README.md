# Schewach Hamoadim — Deutsche Ausgabe

Deutsche Übersetzung von *Schewach Hamoadim, Band 1* (*Die jüdischen Feiertage – Halacha und Brauch*), beginnend mit dem Abschnitt **Chanukka** (Kapitel 61–72).

## Projektstruktur

- [VERSION](file:///Users/elyahuborodin/Documents/projects/schewach-hamoadim-de/VERSION) — Versionsbasis (`0.1.0`)
- [build](file:///Users/elyahuborodin/Documents/projects/schewach-hamoadim-de/build) — Build-Skript für Typst-PDFs (Standard: `a5` Leseausgabe; optional `proof` mit Redaktionshinweisen)
- [docs/sprachguide.md](file:///Users/elyahuborodin/Documents/projects/schewach-hamoadim-de/docs/sprachguide.md) — Verbindliche Stil-, Transkriptions- und Terminologieregeln
- [data/hebrew/](file:///Users/elyahuborodin/Documents/projects/schewach-hamoadim-de/data/hebrew) — Extrahierter hebräischer Originaltext als maschinenlesbares JSON (`schewach-hamoadim.json`, `chanukka.json`)
- [input/chanukka/](file:///Users/elyahuborodin/Documents/projects/schewach-hamoadim-de/input/chanukka) — Deutsche Übersetzung im Markdown-DSL-Format (inkl. `:::redaktion`-Hinweisen)
- [pdfs/](file:///Users/elyahuborodin/Documents/projects/schewach-hamoadim-de/pdfs) — Ausgangs-PDFs (Exposé, Redaktionelle Hilfe, hebräischer Originaltext)
- [scripts/extract_hebrew.py](file:///Users/elyahuborodin/Documents/projects/schewach-hamoadim-de/scripts/extract_hebrew.py) — Extrahiert den gesamten hebräischen Originaltext inkl. Fußnoten aus `pdfs/schwach-hamoadim-Originaltext.pdf`
- [scripts/build_pdf.py](file:///Users/elyahuborodin/Documents/projects/schewach-hamoadim-de/scripts/build_pdf.py) — Konvertiert Markdown-DSL nach Typst
- [templates/typst/](file:///Users/elyahuborodin/Documents/projects/schewach-hamoadim-de/templates/typst) — DIN-A5-Layouts (`proof-a5.typ`, `book-a5.typ`)

## Voraussetzungen

- `python3` (mit `pyyaml`, für die Extraktion zusätzlich `pymupdf` und `pdftotext`)
- `typst` (getestet mit `0.14.2`)

## Verwendung

```bash
# Leseausgabe (DIN A5, Standard, ohne Redaktionshinweise) -> dist/pdf-a5/book.pdf & archive/
./build

# Optional: Korrekturfahne (DIN A5, inkl. :::redaktion-Hinweise) -> dist/proof-a5/book.pdf
./build proof

# Hebräischen Originaltext erneut aus dem PDF extrahieren
python3 scripts/extract_hebrew.py
```
