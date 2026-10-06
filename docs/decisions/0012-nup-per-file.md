# 0012 Per-file n-up (`nup` key)
- Context: issue #1 asks for several PDFs per sheet. `pdfpages` n-up works within a single file only.
- Decision: v0.1 adds `nup=<cols>x<rows>` to `\includeannex`, passed through to `pdfpages`. Pages of one annex share sheets. Annex entry, bookmark, label and list entry point to the annex's first sheet. `layout`, `margin`, `footer-space`, `frame` and `page-style` apply per sheet; scaling follows decision 0008 per slot.
- Out of scope: combining different files on one sheet (`annexsheet` environment). It needs a new design for numbering and `\annexpageref`, so issue #1 stays open for it.
