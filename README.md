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

The v0.1 specification remains the baseline contract: [spec/index.md](spec/index.md).
See [GitHub releases](https://github.com/nocona71/pdfannex/releases) for the current version.

For reproducible inputs, run `pdfannex init` once (it creates
`pdfannex.lock`, which opts in to recording source requests), build once, then
run `pdfannex prepare document.tex`. The CLI locks annex PDFs by SHA-256 into
`.pdfannex/` and `pdfannex.lock`; later builds use the locked copies.
`pdfannex status` reports changed external sources, `update` accepts them, and
`verify` checks the local store. Plain files are handled by the CLI itself
(decision 0015). Other sources use texlua-compatible resolver scripts named
`pdfannex-resolver-SCHEME`; the CLI invokes them with `texlua`, so no
platform-specific shebang or executable bit is required. `\NewAnnexSource`
gives a source its own command (decision 0014). For resolver development, see
the separate [pdfannex resolver example and template](https://github.com/nocona71/pdfannex-docstore),
which demonstrates the protocol with a mock HTTP document service.
Build once without `-halt-on-error` before `prepare` if the document has an
unresolved `pdfannex://` source, because that error can stop the build before
later sources are recorded.

For a one-command `latexmk` workflow, enable the optional project-local
integration described in the [latexmk integration guide](https://github.com/nocona71/pdfannex/blob/main/docs/latexmk-integration.md).
It bootstraps the lock, prepares new requests after the discovery pass, and
lets `latexmk document.tex` rerun TeX. Without that opt-in, direct engine runs
and ordinary `latexmk` retain the explicit CLI workflow above.

The CLI is a TeXLua script. TeX Live installs scripts in its scripts tree and
normally makes commands available on `PATH`; otherwise invoke the installed
script with `texlua` or add its scripts directory to `PATH`. Resolver scripts
are discovered on `PATH` or in the TeX scripts tree.

Development: `make test-fast` runs the focused core packaging and TDS-installer tests; `make check` runs the core smoke and integration tests; `make e2e` installs the core CTAN archive into a clean TEXMFHOME and tests a locked build; `make test` runs l3build; `make doc` builds the manual; and `make package` creates the core CTAN archive. CI also installs the core TDS package through TeX Live's package manager in a clean container. The resolver example has its own tests and package workflow in the [separate repository](https://github.com/nocona71/pdfannex-docstore).

For a persistent install of the core package artifact into a host TeX Live user's tree, see the [manual native TeX Live sanity check](./docs/manual-native-texlive-sanity-check.md).

The devcontainer includes Docker-outside-of-Docker for running Docker-based
checks locally; it requires a Docker daemon on the host and grants the
devcontainer access to that daemon.
