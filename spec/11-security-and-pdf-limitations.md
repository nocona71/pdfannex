# Security

`pdfannex` must not store secrets in:

```text
.tex
pdfannex.lock
request state
resolved.tex
artifact filenames
normal logs
```

Resolver-specific authentication belongs behind the resolver boundary.

Potential mechanisms include:

```text
environment variables
credential stores
source-specific config
MCP authentication
vendor SDK configuration
```

Safe process invocation is required.

Avoid shell command construction from untrusted locator strings.

---

# Original PDF Bytes

When the resolver directly retrieves a PDF, preserve the exact returned bytes.

Do not normalize PDFs before hashing unless transformation is explicitly part of resolution.

This provides clear reproducibility semantics.

---

# Transforming Resolvers

A resolver MAY derive a PDF from another representation.

Conceptually:

```text
input artifact
+ transformation
      ↓
output PDF
```

The resulting PDF is then validated, hashed and stored like any other resolver artifact.

Detailed transformation provenance is outside Resolver Protocol 1 unless later demonstrated necessary.

Transformation remains outside `pdfannex.sty`.

---

# PDF Feature Limitations

Visible inclusion through `pdfpages` does not imply preservation of all original PDF behavior.

Do not promise preservation of:

- annotations;
- interactive source links;
- form fields;
- original digital-signature semantics;
- tagged-PDF accessibility structure.

These are inherited limitations and should be documented rather than reimplemented by v0.1.

---

# Digitally Signed PDFs

Including pages from a signed source PDF does not preserve the source document's signature semantics in the combined output.

The artifact store can still preserve exact source PDF bytes.

Embedding the original file as an attachment is a separate possible future feature and out of scope.

---

# Accessibility

Package-owned content such as:

```text
List of Annexes
headings
references
```

should remain ordinary selectable LaTeX text.

Do not promise preservation of tagging from included external PDFs.

---

# Full Build Reproducibility

Initial reproducibility guarantee:

> Given the same lockfile and artifact store, the same annex PDF inputs are used.

This does not imply a bit-identical final document.

Other variables include:

```text
TeX distribution version
engine version
package versions
fonts
timestamps
locale
PDF metadata
```

Full toolchain reproducibility belongs to higher-level build environments and is out of scope.

---

# CTAN Distribution

The CTAN distribution should primarily deliver:

```text
pdfannex.sty
documentation
l3build configuration/tests
```

Where practical it may additionally deliver:

```text
pdfannex.lua
latexmk integration helper
```

The LaTeX package itself MUST remain fully usable when those optional external-source components are never invoked.

Resolver implementations need not be CTAN packages.

---

# Resolver Distribution

Resolvers may be distributed through whatever ecosystem fits them:

```text
CTAN
PyPI / pipx
Cargo
npm
system packages
standalone binaries
GitHub releases
```

The project does not define a resolver package manager in v0.1.

The stable integration point is Resolver Protocol 1.

---
