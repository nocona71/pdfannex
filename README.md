# pdfannex

LaTeX package for including PDFs as annexes (via `pdfpages`) with bookmarks,
hyperlinks, an automatic list of annexes and cross references. Works with
pdfLaTeX, LuaLaTeX and XeLaTeX. The package also includes a TeXLua CLI and
Resolver Protocol 1 for locking reproducible annex inputs.

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

For reproducible inputs, run `pdfannex init` once (it creates
`pdfannex.lock`, which opts in to recording source requests), build once, then
run `pdfannex prepare document.tex`. The CLI locks annex PDFs by SHA-256 into
`.pdfannex/` and `pdfannex.lock`; later builds use the locked copies.
`pdfannex status` reports changed external sources, `update` accepts them, and
`verify` checks the local store. Plain files are handled by the CLI itself
(decision 0015). Other sources use resolver programs named
`pdfannex-resolver-SCHEME`; `adapter-example/` is a fork-start, and
`\NewAnnexSource` gives a source its own command (decision 0014). The docstore
example is a separate adapter and requires curl when contacting its service.
Build once without `-halt-on-error` before `prepare` if the document has an
unresolved `pdfannex://` source, because that error can stop the build before
later sources are recorded.

The CLI is a TeXLua script. TeX Live installs scripts in its scripts tree and
normally makes commands available on `PATH`; otherwise invoke the installed
script with `texlua` or add its scripts directory to `PATH`. Adapters must
also be available on `PATH`.

Development: `make check` (smoke tests), `make e2e` (install the CTAN archive into a clean TEXMFHOME and build with it), `make test` (l3build), `make doc`, `make package` (core CTAN archive), `make adapter-package` (docstore adapter archive).
