# 0002 Use `pagecommand*` for first-page work
- Context: legacy `picturecommand*` fires on every included page.
- Decision: use pdfpages `pagecommand*` for per-annex first-page work (aux/.loa entry, bookmark, target). Evidence: `docs/spike-phase-a.md`.
- Consequences: confirmed on pdfLaTeX, LuaLaTeX, XeLaTeX. Bookmarks, hyperlinks, .loa and pass count still to verify in the real package.
