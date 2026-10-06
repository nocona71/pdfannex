# pdfannex

LaTeX package for including PDFs as annexes (via `pdfpages`) with bookmarks,
hyperlinks, an automatic list of annexes and cross references. Works with
pdfLaTeX, LuaLaTeX and XeLaTeX. An optional CLI and resolver protocol are
specified; an experimental CLI is included in the repository.

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
Reproducible inputs (experimental, not yet in the CTAN archive): run `texlua cli/pdfannex init` once (it creates `pdfannex.lock`, which makes the package record its sources; without it no extra files are written), build once, then `texlua cli/pdfannex prepare document.tex` locks every annex PDF by SHA-256 into `.pdfannex/` and `pdfannex.lock`; later builds use the locked copies. `status` reports changed sources, `update` accepts them, `verify` checks the store. Plain files are handled by the CLI itself (decision 0015). Other sources use resolver programs `pdfannex-resolver-SCHEME`; `examples/` has a documented fork-start (`pdfannex-resolver-docstore`) and `\NewAnnexSource` gives a source its own command (decision 0014). Note: build once without `-halt-on-error` before `prepare`, because an unresolved `pdfannex://` source is an error and stops the build before later sources are recorded.

Development: `make check` (smoke tests), `make e2e` (install the CTAN archive into a clean TEXMFHOME and build with it), `make test` (l3build), `make doc`, `make package`.
