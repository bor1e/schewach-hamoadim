// =============================================================================
// Schewach Hamoadim — Deutsche Ausgabe (DIN A5)
// =============================================================================

#let accent = rgb("#7A3E1D")
#let ink = rgb("#1A1A1A")
#let muted = rgb("#666666")
#let hebrew-font = ("SBL Hebrew", "Noto Serif Hebrew", "Arial")

#set text(font: ("Georgia", "Times New Roman"), size: 10.5pt, lang: "de", fill: ink)
#set par(justify: true, leading: 0.72em, spacing: 0.9em)

#set page(
  paper: "a5",
  margin: (inside: 1.8cm, outside: 1.4cm, top: 1.8cm, bottom: 1.8cm),
  header: context {
    if counter(page).get().first() > 2 {
      set text(size: 8pt, fill: muted, style: "italic")
      if calc.odd(counter(page).get().first()) {
        align(right)[Schewach Hamoadim — Chanukka]
      } else {
        align(left)[Die jüdischen Feiertage — Halacha und Brauch]
      }
      v(-0.4em)
      line(length: 100%, stroke: 0.3pt + gray.lighten(50%))
    }
  },
  footer: context {
    if counter(page).get().first() > 1 {
      align(center, text(size: 8.5pt, fill: muted, counter(page).display()))
    }
  }
)

#show heading.where(level: 1): it => block(sticky: true, above: 1.4em, below: 1.0em)[
  #set par(justify: false)
  #set text(hyphenate: false)
  #text(size: 15pt, weight: "bold", fill: accent, it.body)
]

#show heading.where(level: 2): it => block(sticky: true, above: 1.35em, below: 0.65em)[
  #set par(justify: false)
  #set text(hyphenate: false)
  #text(size: 11.5pt, weight: "bold", fill: accent, it.body)
]

#show heading.where(level: 3): it => block(sticky: true, above: 0.9em, below: 0.45em)[
  #set par(justify: false)
  #set text(hyphenate: false)
  #text(size: 10.5pt, weight: "bold", it.body)
]

#let heb(content) = {
  show "\"": "״"
  show "'": "׳"
  text(font: hebrew-font, lang: "he", dir: rtl, size: 10.5pt, content)
}

#let redaktion(content) = {
  // Im Buchdruck standardmäßig ausgeblendet; in proof-a5.typ sichtbar.
}

#let infobox(content) = {
  block(
    width: 100%,
    fill: rgb("#FAF7F2"),
    stroke: (left: 2pt + accent),
    inset: (x: 10pt, y: 8pt),
    spacing: 1em,
    text(size: 9.5pt, content)
  )
}

#set footnote.entry(indent: 0pt)
#show footnote.entry: it => {
  set text(size: 8.5pt, fill: ink.lighten(10%))
  it
}

// --- Deckblatt ---
#page(header: none, footer: none)[
  #place(top + right, text(font: hebrew-font, lang: "he", dir: rtl, size: 9pt, fill: muted)[בס״ד])
  #align(center + horizon)[
    #text(size: 20pt, weight: "bold", fill: accent)[Schewach Hamoadim]
    #v(0.4em)
    #text(size: 12pt, style: "italic")[Die jüdischen Feiertage — Halacha und Brauch]
    #v(1.2em)
    #line(length: 40%, stroke: 0.6pt + accent)
    #v(1.2em)
    #text(size: 13pt, weight: "bold")[Chanukka]
    #v(0.4em)
    #text(size: 9.5pt, fill: muted)[Deutsche Übersetzung (MVP)]
    #v(2em)
    #let ver = "{{VERSION}}"
    #if ver != "" {
      text(size: 8pt, fill: muted)[Version #ver · #datetime.today().display("[day].[month].[year]")]
    }
  ]
]

{{CONTENT}}
