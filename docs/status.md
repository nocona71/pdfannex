# Status / roadmap
- [x] 1 Restructure (`legacy/`)
- [x] 2 Migration map (`docs/migration-map.md`)
- [~] Phase A spike: first-page hook and aux confirmed; bookmarks, hyperlinks, .loa, pass count open
- [ ] 3 `pdfannex.sty` skeleton + `l3build` tests (pdflatex, lualatex, xelatex)
- [ ] 4 CTAN packaging
- [ ] 5 Phases B/C deferred
- [ ] 6 Copilot `.instructions.md` files

- [x] Infra adoption: devcontainer, CI, release-please, l3build skeleton (`make check` passes; decision 0004)

## Step 3 progress
- `tex/pdfannex.sty` expl3 skeleton: include, labels/refs, bookmarks, `\listofannexes` (via aux) work with pdflatex.
- TODO: layouts beyond fullpage, l3build tests, xetex/luatex checks.
