# Localization

The canonical API remains English.

Default visible strings:

```text
Annex
Annexes
```

Allow:

```latex
\pdfannexsetup{
  annex-name=Anlage,
  heading=Anlagen
}
```

Do not require Babel or Polyglossia.

---

# No Global Side Effects

Loading:

```latex
\usepackage{pdfannex}
```

MUST NOT globally alter:

- fonts;
- margins;
- document paper size;
- language;
- paragraph layout;
- ordinary page style;
- headers;
- footers;
- page numbering before annex handling.

All annex-specific behavior must be scoped.

---

# Missing Local PDFs

A missing local PDF is a hard package error.

Example:

```text
Package pdfannex Error:
Annex PDF 'contract.pdf' was not found.
```

Never silently omit a required local annex.

---

# Shell-Escape Policy

`pdfannex.sty` MUST NOT require:

```text
-shell-escape
```

It MUST NOT directly invoke:

```text
curl
wget
Python
Node
Rust
Go
resolver executable
converter
network client
```

External preparation happens outside the TeX process.

---

# Document-Class Independence

Compatibility is architectural, not whitelist-based.

Representative regression classes:

```text
article
report
book
letter

scrartcl
scrreprt
scrbook
scrlttr2

memoir

amsart
amsbook

extarticle
extreport
extbook

IEEEtran
```

This is a test matrix, not a list of classes the package explicitly recognizes.

Avoid logic such as:

```text
if class == scrlttr2
```

unless a demonstrated incompatibility leaves no class-neutral solution.

---

# Non-Targets

For v0.1:

```text
beamer
standalone
```

are not primary targets.

They should be documented as unsupported or of limited semantic relevance rather than distorting the package architecture.

---

# Engine Support

Target:

```text
pdfLaTeX
LuaLaTeX
XeLaTeX
```

subject to current `pdfpages` capabilities.

---
