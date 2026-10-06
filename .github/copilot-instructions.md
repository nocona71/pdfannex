# Copilot instructions — pdfannex

## Project
`pdfannex` is a LaTeX package (`pdfannex.sty`) for including PDFs as annexes, plus an optional CLI and
resolver protocol for external sources. The LaTeX package is implemented (v0.1 in development); the CLI and resolver protocol are still spec-only.

## Source of truth
- The v0.1 spec is split by topic in `spec/` (start at `spec/index.md`). Edit the files in `spec/`.
- Normative terms (MUST/SHOULD/MAY) are meaningful. Use the terminology table in `spec/01-overview.md` consistently.
- Priorities, in order: correctness, minimal user bootstrap, small stable interfaces, reuse of mature LaTeX
  infrastructure, class independence, reproducibility, clear diagnostics, minimal complexity.
- Core package must work with plain LaTeX tooling; external-source features must not increase its bootstrap burden.
- Anything not required for v0.1 is out of scope.

## Editing the spec
- Keep each file in `spec/` under ~8 KB (LanguageTool on the NAS is slow, ~3.5 s/KB). Split by topic at
  top-level `#` headings; update `spec/index.md` when adding/renaming files.
- Cross-check requirement IDs/headings referenced between files when renaming sections.

## Conventions
- Markdown, English (en-US), fenced code blocks tagged with language (`latex`, `json`, `bash`).
- LaTeX code: `legacy/fancy-anlagen.sty` is the legacy predecessor style, useful as reference only.

## Documentation rule
Record every design/process decision as a file in `docs/decisions/` (update its README table) and experiment findings in `docs/`. Capture plans and open items in the repo so work can resume after an interruption.
