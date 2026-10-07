# 0033 Use plain-text annex references in PDF bookmarks

- Context: `\annexref` creates an in-document hyperlink, while PDF bookmarks and other PDF strings cannot contain that hyperlink command. Using either reference command in a heading otherwise makes `hyperref` discard it with a warning.
- Decision:
  1. Keep `\annexref` clickable in document text and use its plain-text form, `Annex N`, in PDF strings.
  2. Use the page number from `\annexpageref` in PDF strings.
  3. Support these references in headings, captions, footnotes, and other moving contexts without adding special markup at each use site.
- Consequences: Moving contexts produce clean bookmarks and auxiliary entries. Regression tests cover their reference values and PDF-string output across the supported engines.
