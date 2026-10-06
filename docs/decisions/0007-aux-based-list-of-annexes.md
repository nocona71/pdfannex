# 0007 List of annexes built from `.aux`, not `.loa`
- Context: spec/03 allows a `.loa` file; a separate file adds a writer/reader and another stale-state source.
- Decision: first-page hook writes `\pdfannex@loa{number}{title}{page}` to the `.aux`; `\listofannexes` replays them. Labels use `\pdfannex@newlabel` the same way.
- Evidence: `spike/phase-a2.tex`, `testfiles/annex-refs.lvt`; two runs give stable output on pdfLaTeX, LuaLaTeX, XeLaTeX.
- Consequences: no `.loa` file; `\listofannexes` is empty/`??` on the first run.
