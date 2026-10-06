---
applyTo: "tex/**,doc/**,testfiles/**"
---
# LaTeX package code

- `tex/pdfannex.sty` is expl3; keep internals `\__pdfannex_...` and public commands `\NewDocumentCommand`.
- Must work on pdfLaTeX, LuaLaTeX and XeLaTeX with no class dependency.
- pdfpages has no `pagecommand*`; first-page work goes through `pagecommand` plus the once-per-annex flag (decision 0006).
- Annex state (labels, list entries) lives in `.aux` (decision 0007); references need two runs.
- Update `doc/pdfannex-doc.tex` when options or commands change. Keep the version marker `# x-release-please-version` lines intact.
- Tests: `make check` (smoke tests, fails on any package error) and `make test` (l3build). Put assertions after `\START` in `.lvt` files; errors before it are not compared.
- Regenerate a `.tlg` only with `l3build save <name>` and review the diff.
