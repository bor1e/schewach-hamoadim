// =============================================================================
// Schewach Hamoadim — Korrekturfahne (DIN A5, inkl. :::redaktion-Hinweise)
// =============================================================================

#let accent = rgb("#7A3E1D")
#let redaktion-color = rgb("#B45309")
#let ink = rgb("#1A1A1A")
#let muted = rgb("#666666")
#let hebrew-font = ("SBL Hebrew", "Noto Serif Hebrew", "Arial")

#set text(font: ("Georgia", "Times New Roman"), size: 10.5pt, lang: "de", fill: ink)
#set par(justify: true, leading: 0.8em, spacing: 1.0em)

#set page(
  paper: "a5",
  margin: (left: 1.4cm, right: 1.6cm, top: 1.8cm, bottom: 1.8cm),
  header: context {
    if counter(page).get().first() > 1 {
      set text(size: 7.5pt, fill: muted)
      [Korrekturfahne · Schewach Hamoadim (Chanukka) #h(1fr) #("{{VERSION}}")]
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
  block(
    width: 100%,
    fill: rgb("#FFFBEB"),
    stroke: (left: 2.5pt + redaktion-color),
    inset: (x: 9pt, y: 7pt),
    spacing: 0.8em,
    text(size: 8.8pt, fill: rgb("#78350F"))[*Redaktionshinweis:* #content]
  )
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

#page(header: none, footer: none)[
  #place(top + right, text(font: hebrew-font, lang: "he", dir: rtl, size: 9pt, fill: muted)[בס״ד])
  #align(center + horizon)[
    #text(size: 18pt, weight: "bold", fill: accent)[Schewach Hamoadim — Korrekturfahne]
    #v(0.5em)
    #text(size: 12pt)[Chanukka (mit redaktionellen Hinweisen)]
    #v(1em)
    #let ver = "{{VERSION}}"
    #text(size: 8.5pt, fill: muted)[
      #if ver != "" { "Version " + ver + " · " }
      #datetime.today().display("[day].[month].[year]")
    ]
  ]
]

{{CONTENT}}
