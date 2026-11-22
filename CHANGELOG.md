# Changelog

Versionierungsregeln (wie in *Inyana Shel Toras HaChassidus*):
- **MINOR** — Änderungen am deutschen Lesetext
- **PATCH** — Änderungen an Fußnoten, Redaktionshinweisen, Typographie oder Pipeline

## [0.1.4] — 2026-11-22

- Deckblatt: „(MVP)“ entfernt, `בס״ד` oben rechts ergänzt.
- Typst-Satz: Überschriften mit `sticky: true` an den Folgeabsatz gebunden (keine verwaisten Überschriften), Silbentrennung in Überschriften deaktiviert (`hyphenate: false`), Abstands-Hierarchie verfeinert.
- Versionsbasis auf `0.1.4` und Git-Tag `v0.1.4` synchronisiert.

## [0.1.0] — 2026-11-22

- Initiales MVP-Projektsetup (`build`, `scripts/build_pdf.py`, `templates/typst/{book,proof}-a5.typ`, `docs/sprachguide.md`).
- Vollständige hebräische Extraktion aus `pdfs/schwach-hamoadim-Originaltext.pdf` nach `data/hebrew/schewach-hamoadim.json` und `data/hebrew/chanukka.json` (5 Teile, 100 Simanim, 760 Absätze, 1108 Fußnoten).
- Erste vollständige deutsche Übersetzung des Abschnitts **Chanukka** (Einleitung + Kapitel 61–72) im *schlichten*, warmen Stil für die Zielgruppe 16–50 Jahre.
