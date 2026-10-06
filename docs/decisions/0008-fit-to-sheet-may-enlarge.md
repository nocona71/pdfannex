# 0008 Fit-to-sheet scaling may enlarge small pages
- Context: spec/04 asked for no upscaling. `pdfpages` always scales a source page to fit the host sheet (`\AM@globalscale`), so small pages are enlarged. `noautoscale` disables all scaling (large pages overflow). Clamping the scale needs `pdfpages` internals.
- Decision: v0.1 uses plain `pdfpages` fit-to-sheet scaling and keeps the host sheet size (no `fitpaper`, which changed the sheet size to the source's, contradicting `sheet-size=document`). No-upscale is deferred. Users are warned in the manual and README.
- Evidence: `testfiles/test_geometry.py` (A5 enlarged, A3 shrunk, landscape not rotated, host size kept, margin/footer-space distances).
- Consequences: spec/04 amended.
