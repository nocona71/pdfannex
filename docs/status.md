# Status / roadmap
- [x] 1 Restructure (`legacy/`)
- [x] 2 Migration map (`docs/migration-map.md`)
- [x] Phase A spike: complete (decision 0006; `pagecommand*` does not exist, use `pagecommand` + flag)
- [ ] 3 `pdfannex.sty` skeleton + `l3build` tests (pdflatex, lualatex, xelatex)
- [ ] 4 CTAN packaging
- [ ] 5 Phases B/C deferred
- [x] 6 Copilot `.instructions.md` files (`.github/instructions/`)

- [x] Infra adoption: devcontainer, CI, release-please, l3build skeleton (`make check` passes; decision 0004)

## Step 3 progress
- `tex/pdfannex.sty` expl3 skeleton: include, labels/refs, bookmarks, `\listofannexes` (via aux) work with pdflatex.
- TODO: layouts beyond fullpage, l3build tests, xetex/luatex checks.

## l3build
- `testfiles/annex-basic.lvt`: 3 annexes, three layouts, counters; passes on pdftex/luatex/xetex (checkruns=2). Fixtures in `testfiles/support/`.
- `testfiles/annex-refs.lvt`: asserts label numbers/pages and list entries; `margin`/`footer-space` keys implemented (uniform scale + upward shift, relative to host paper size).
- Decision 0007 records the aux-based list. Geometry: host sheet size kept, fit-to-sheet (may enlarge small pages, decision 0008), orientation preserved; `testfiles/test_geometry.py`. Open: `pagination=continue` (needs scrlttr2 test), docs polish.
