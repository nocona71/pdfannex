# 0004 — Dev, CI and release infrastructure from paperlessngx-latex

Status: accepted

- Adopted the sibling project's devcontainer (single `dev` service), `make check`, l3build, GitHub Actions CI, release-please and CTAN release workflow.
- Licence: LPPL 1.3c.
- Release tags use the prefix `v` (release-please `include-v-in-tag`); package name `pdfannex`.
- Versions are kept in `VERSION`, `tex/pdfannex.sty` and `doc/pdfannex-doc.tex` via `x-release-please-version` markers; `test_packaging.py` checks they agree.
