# 0006 First-page work via `pagecommand` plus a global flag
- Context: decision 0002 assumed `pagecommand*`. Installed pdfpages (TeX Live 2023) defines only `pagecommand`, `picturecommand` and `picturecommand*` (`keyval Error: pagecommand* undefined`). `picturecommand*` runs in the shipout picture, so it is unsuitable for aux writes and bookmarks.
- Decision: `pagecommand` calls `\__pdfannex_page_hook:`, which sets the page style every page and runs first-page work once per annex, guarded by `\g__pdfannex_first_bool` (set in `\includeannex`).
- Evidence: `spike/phase-a2.tex`, `docs/spike-phase-a.md`.
- Consequences: works on pdfLaTeX, LuaLaTeX, XeLaTeX.
