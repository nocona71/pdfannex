# PDF-Only Core

The canonical artifact consumed by `pdfannex.sty` is a PDF.

The core does not directly consume:

```text
PNG
JPEG
TIFF
SVG
DOCX
ODT
HTML
remote URL
Paperless ID
Zotero ID
cloud object
database row
```

Anything else must first produce a PDF.

Examples:

```text
Paperless document
       ↓
resolver / external tooling
       ↓
PDF
       ↓
pdfannex.sty
```

```text
image
  ↓
converter
  ↓
PDF
  ↓
pdfannex.sty
```

The package MUST NOT become a general conversion framework.

---

# LaTeX Dependencies

Use mature existing infrastructure.

Required or expected core dependencies:

```text
pdfpages
hyperref
bookmark
modern LaTeX kernel
expl3 / l3keys where useful
```

`pdfpages` is the sole low-level PDF inclusion engine.

Do not require:

```text
KOMA-Script
scrlayer-scrpage
fancyhdr
memoir
```

These are compatibility targets, not dependencies.

---

# Public LaTeX API

## Local PDF inclusion

Canonical command:

```latex
\includeannex[<options>]{<pdf-file>}{<title>}
```

Example:

```latex
\includeannex[
  label=contract,
  pages=1-3,
  layout=footer-safe
]{contract.pdf}{
  Contract
}
```

The PDF path is a normal LaTeX argument. TeX-special characters MUST be
escaped using ordinary LaTeX syntax. After TeX expansion, `pdfannex.sty` MUST
preserve the local path literally; it MUST NOT URL-decode percent sequences or
interpret leading hyphens, question marks, or equals signs as options.

Core tests MUST cover paths with spaces, Unicode, nested directories, `%`, `&`,
`#`, `_`, `?`, `=`, leading hyphens, and literal percent sequences across
pdfLaTeX, XeLaTeX, and LuaLaTeX. This minimum set does not guarantee arbitrary
active characters or non-default catcodes.

---

## External source inclusion

When external source support is enabled, the same semantic annex pipeline is used:

```latex
\includeannex[
  source={pdfannex://paperless/4711},
  label=tax-assessment
]{Tax assessment}
```

The exact command parsing may internally distinguish local and source-based forms, but they MUST converge on one annex inclusion implementation.

External source support MUST NOT introduce source-specific public commands into the core package.

---

# Required Annex Options

v0.1 should keep the option surface deliberately small.

Required:

```text
label
pages
source
layout
page-style
frame
bookmark
list
```

Potentially:

```text
scale
margin
footer-space
```

when required by the geometry implementation.

Do not expose low-level `pdfpages` configuration wholesale in v0.1.

A controlled escape hatch may be considered later.

---

# Global Configuration

Provide:

```latex
\pdfannexsetup{
  annex-name=Annex,
  heading=Annexes,
  layout=footer-safe,
  page-style=plain,
  pagination=inherit
}
```

Required global properties:

```text
annex-name
heading
layout
page-style
pagination
```

---

# Annex Identity

Annex number and semantic identity are different concepts.

Example:

```latex
\includeannex[
  label=contract
]{contract.pdf}{
  Contract
}
```

The annex might currently be:

```text
Annex 3
```

and later become:

```text
Annex 4
```

without changing its semantic identity.

The stable document identity is:

```text
contract
```

not:

```text
3
```

---

# Annex Counter

Use a normal LaTeX counter:

```text
annex
```

Default:

```text
Annex 1
Annex 2
Annex 3
```

Users may redefine:

```latex
\renewcommand\theannex{\Roman{annex}}
```

Do not hard-code Arabic numbering.

---
