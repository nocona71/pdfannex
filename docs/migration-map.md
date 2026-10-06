# Migration map: `fancy-anlagen` -> `pdfannex`

| Legacy | pdfannex (planned, see spec/02) | Notes |
|---|---|---|
| `\Anlage[pages]{file}{title}` | `\includeannex[...]{file}` with title option | Legacy hard-codes `Anlagen/`; new: configurable path |
| `\AnlageAuxEntry` / `\AnlagePageAux` (.aux) | `.loa` entries | Legacy used `picturecommand*` (per page); new uses `pagecommand*` (first page only) |
| `\AnlageLink{n}{text}` | semantic reference to annex label | Legacy links to physical page; `??` if unknown |
| `\Anlagenverzeichnis` | `\listofannexes` | Legacy has hard-coded German strings; new is localized |
| counter `anlage` | annex counter | |
| Bookmarks "Anhang N: title" under "Anhänge" | same, localized | |
