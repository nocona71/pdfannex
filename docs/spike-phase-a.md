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
