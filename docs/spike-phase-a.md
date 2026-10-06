# Phase A feasibility spike

Script: `spike/t.tex` (annexes of 3 and 1 pages after one body page).

| Question | Result (pdfLaTeX, LuaLaTeX, XeLaTeX identical) |
|---|---|
| `pagecommand*` runs once per annex (first page only)? | Yes: 2 hook calls for 4 included pages |
| First-page number correct in `.aux`? | Yes: annex 1 -> p.2, annex 2 -> p.5 |
| Aux-based multipass works? | Yes, values available on the next run |

Conclusion: the spec's choice of `pagecommand*` (spec/03) is sound and
fixes the legacy per-page `picturecommand*` repetition.

Not yet tested: bookmarks hierarchy, `\hyperlink` targets, `.loa` stability,
pass count. Do these with the real `pdfannex.sty`.

## Correction and completion (real `pdfannex.sty`, `spike/phase-a2.tex`)

The first spike's `pagecommand*` is not a pdfpages key (keyval error, ignored
under nonstopmode). See decision 0006: `pagecommand` + once-per-annex flag.

Results with the real package, 3 runs on pdfLaTeX, LuaLaTeX, XeLaTeX:

| Question | Result |
|---|---|
| Bookmarks | Both annex bookmarks present; titles correct |
| Hyperlinks | `\annexref` and list entries become Link annotations to `pdfannex.N` targets |
| List of annexes | Built from aux (no `.loa`); filled from pass 2 |
| Pass count | 2 runs for stable output (pass 1 shows `??`); aux identical on passes 2 and 3 |
