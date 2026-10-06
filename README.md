# pdfannex

LaTeX package for including PDFs as annexes (via `pdfpages`) with bookmarks,
hyperlinks, an automatic list of annexes and cross references. Works with
pdfLaTeX, LuaLaTeX and XeLaTeX. An optional CLI and resolver protocol are
specified but not yet implemented.

```latex
\usepackage{pdfannex}
\listofannexes
\includeannex[label=cv,layout=footer-safe]{cv.pdf}{Curriculum vitae}
See \annexref{cv} on page \annexpageref{cv}.
```

Run LaTeX twice to resolve references.

**Warning:** annex pages are scaled to fit the host sheet (aspect ratio and orientation preserved). Source pages smaller than the sheet, such as A5 in an A4 document, are enlarged; larger pages are shrunk.
 See `doc/pdfannex-doc.tex` for options.

Status: v0.1 in development. Specification: [spec/index.md](spec/index.md).
Development: `make check` (smoke tests), `make test` (l3build), `make doc`, `make package`.
