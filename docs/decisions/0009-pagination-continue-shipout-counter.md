# 0009 `pagination=continue` via a shipout counter
- Context: `scrlttr2` resets the page counter per letter, so annex pages after the second letter were recorded too low (spec/04 requires a `scrlttr2` test).
- Decision: count shipped pages with the `shipout/before` hook; `continue` does `\clearpage` and sets the page counter to shipped pages + 1 before the annex.
- Evidence: `testfiles/test_pagination.py` (inherit -> 2, continue -> 3).
- Consequences: needs the LaTeX hook management of 2020 or newer; `inherit` is unchanged.
