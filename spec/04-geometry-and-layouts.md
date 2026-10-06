# Page Geometry

The core must distinguish:

```text
source PDF page size
```

from:

```text
output document sheet size
```

Sources may include:

```text
A4
A5
Letter
Legal
landscape
custom sizes
mixed-size pages
```

while the host document uses another paper size.

This is page placement, not source-file conversion.

---

# Default Geometry

Default policy:

```text
sheet-size=document
fit=contain
```

Meaning:

- preserve host document sheet size;
- preserve source aspect ratio;
- shrink as necessary;
- do not crop by default;
- do not upscale by default;
- never stretch non-uniformly.

---

# Annex Content Area

Use one central abstraction:

```text
output sheet
    minus
annex margins
    minus
reserved footer/header areas
    =
annex content area
```

Fit each source page into this area.

---

# v0.1 Layouts

Required named layouts:

```text
fullpage
footer-safe
framed
```

## `fullpage`

Use the maximum appropriate page area.

Typical semantics:

```text
minimal annex margin
no reserved footer
no frame
```

## `footer-safe`

Reserve clean whitespace for host document pagination/footer.

Source content must not be obscured by the host footer.

This is the recommended default for formal documents.

## `framed`

Provide modest surrounding space and a visible frame.

Prefer existing `pdfpages` frame facilities.

---

# Margins

Support:

```text
margin
footer-space
```

in v0.1 where necessary.

Directional margins are deferred.

---

# Orientation

Default:

```text
orientation=preserve
```

Do not silently rotate pages.

Automatic orientation is deferred.

---

# Mixed-Size PDFs

One PDF may contain pages with different dimensions.

Each source page must be fitted independently.

The entire source may still represent one semantic annex.

---

# Page Style

Allow the user to select an already defined LaTeX page style.

Default:

```text
plain
```

Do not require or configure:

```text
fancyhdr
scrlayer-scrpage
```

---

# Pagination

The normal LaTeX:

```text
page
```

counter remains the document page counter.

Desired behavior:

```text
main document          page 1
main document          page 2
List of Annexes        page 3
Annex 1 page 1         page 4
Annex 1 page 2         page 5
Annex 2 page 1         page 6
```

Do not introduce a separate visible annex-page numbering system in v0.1.

---

# Pagination Modes

Provide:

```text
pagination=inherit
pagination=continue
```

## `inherit`

Default.

Use the current logical page-counter state.

## `continue`

Ensure annex page numbering continues from already emitted document pages where a host class/environment has reset logical page numbering.

This MUST be tested with `scrlttr2`.

---
