# Canonical Inclusion Pipeline

All annex inclusion MUST use one canonical internal pipeline.

Conceptually:

```text
resolve local PDF path
      ↓
validate
      ↓
increment annex counter
      ↓
create semantic target
      ↓
establish reference state
      ↓
calculate layout
      ↓
invoke pdfpages
      ↓
detect first inserted document page
      ↓
write .loa metadata
      ↓
create bookmark
```

Private implementation names may use:

```text
\__pdfannex_...
```

No external integration may depend on private implementation commands.

---

# `pdfpages` Integration

`pdfpages` owns physical PDF-page insertion.

Use it for:

- source-page selection;
- page fitting;
- scaling;
- positioning;
- framing;
- per-page commands;
- first-page-only commands.

Do not create a competing rendering path with `\includegraphics`.

---

# First-Page Processing

Use current `pdfpages` first-page facilities such as `pagecommand*` where suitable.

First-page work includes:

```text
semantic hyperlink target
label/reference state
first document page
List-of-Annexes entry
bookmark
```

Per-page work includes:

```text
page style
footer/page number
presentation
```

Avoid a custom first-page state machine unless required by demonstrated `pdfpages` behavior.

---

# Native LaTeX Multi-Pass Model

LaTeX owns document structural state.

Use:

```text
.aux
```

for ordinary references.

Use:

```text
<jobname>.loa
```

for the List of Annexes.

Expected flow:

```text
LaTeX pass 1
    ↓
write .aux / .loa
    ↓
LaTeX pass 2
    ↓
resolved list and references
    ↓
additional pass only if pagination changed
```

Do not implement a second document-indexing engine.

Do not use `makeindex` for the primary List of Annexes.

---

# List of Annexes

Provide:

```latex
\listofannexes
```

Conceptual output:

```text
Annexes

Annex 1: Contract ........................ 4
Annex 2: Medical report .................. 7
Annex 3: Invoice ........................ 12
```

Entries MUST contain:

- annex number;
- title;
- first document page;
- semantic hyperlink.

---

# `.loa` Data

Store semantic data rather than preformatted visual lines.

Conceptually:

```latex
\pdfannexlistentry
  {contract}
  {3}
  {Contract}
  {17}
  {pdfannex.contract}
```

Do not persist:

```text
Annex 3: Contract ............ 17
```

as formatted output.

Formatting occurs when the list is rendered.

---

# List Heading

Do not hard-code:

```latex
\chapter*{Annexes}
```

or:

```latex
\section*{Annexes}
```

Use a class-neutral default and an overridable heading implementation.

---

# References

For:

```latex
\includeannex[
  label=contract
]{contract.pdf}{
  Contract
}
```

provide:

```latex
\annexref{contract}
```

```latex
\annexpageref{contract}
```

```latex
\annexlink{contract}{see the contract}
```

Use normal LaTeX reference infrastructure wherever practical.

---

# Hyperlink Destinations

Do not use logical page anchors such as:

```text
page.17
```

as annex identity.

Logical page numbers may repeat after class- or environment-induced resets.

Create semantic destinations such as:

```text
pdfannex.contract
```

or equivalent unique internal targets.

The displayed page number and hyperlink identity are independent.

---

# Bookmarks

Desired PDF outline:

```text
document
Annexes
    Annex 1: Contract
    Annex 2: Medical report
```

`pdfannex.sty` owns only its own bookmark subtree.

It MUST NOT globally reconfigure `hyperref` or `bookmark`.

---
