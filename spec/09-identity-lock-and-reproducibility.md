# Source Identity vs Presentation

These must remain independent.

```text
source identity:
pdfannex://paperless/4711

annex identity:
tax-assessment

annex title:
Tax assessment 2025

source page selection:
1-3

layout:
footer-safe
```

Changing:

```text
title
pages
layout
frame
page style
bookmark visibility
```

MUST NOT cause source re-resolution.

---

# Mutable and Immutable Source Identity

A source may be mutable:

```text
requested:
pdfannex://paperless/4711?selector=latest
```

and resolve to:

```text
resolved:
pdfannex://paperless/4711?version=98273
```

The resolver owns the provider-specific semantics of these locators.

The generic CLI treats provider-specific portions as opaque.

---

# Reproducibility Contract

For managed external sources:

> **A normal build uses the locked PDF artifact and never silently advances a mutable source.**

Three identities remain distinct:

```text
requested source
resolved upstream source/revision
artifact SHA-256
```

The SHA-256 identifies the exact PDF bytes used by the build.

---

# Project-Local Artifact Store

Initial storage policy:

> **project-local only**

Layout:

```text
project/
├── document.tex
├── pdfannex.lock
└── .pdfannex/
    └── objects/
        └── sha256/
            └── 8f/
                └── 8f2c...a91.pdf
```

Objects are immutable.

The lock stores hashes, not absolute physical paths.

Do not implement global/hybrid storage in v0.1.

---

# `pdfannex.lock`

The CLI owns:

```text
pdfannex.lock
```

`pdfannex.sty` MUST NOT parse it.

Required conceptual information:

```text
lock schema version
logical source identity
resolver/provider
requested locator
resolved locator if available
artifact SHA-256
media type
```

Keep the schema minimal.

Do not persist backend implementation details such as:

```text
MCP server used
REST endpoint used
number of backend calls
CLI helper used
```

unless later demonstrated useful as optional diagnostics.

Such information is not part of reproducibility identity.

---

# Hash Authority

Artifact SHA-256 is authoritative for reproducibility.

Upstream version IDs provide provenance.

If exact recovery returns different bytes for an already locked hash:

> fail.

Never silently replace a locked artifact.

---

# Exact Recovery

If the local artifact is missing and the lock contains:

```text
requested:
pdfannex://paperless/4711?selector=latest

resolved:
pdfannex://paperless/4711?version=98273
```

recovery MAY call:

```text
resolve(
  pdfannex://paperless/4711?version=98273
)
```

It MUST NOT fall back to:

```text
selector=latest
```

If exact recovery is impossible:

> fail.

No dedicated recovery protocol operation is required.

---

# Resolution Map

`pdfannex.sty` does not parse the lockfile or artifact-store layout.

The CLI generates TeX-native state such as:

```text
.pdfannex/resolved.tex
```

Conceptually:

```latex
\PdfAnnexProvideResolvedArtifact
  {tax-assessment}
  {.pdfannex/objects/sha256/8f/8f2c...a91.pdf}
```

The resolution map is generated state.

`pdfannex.lock` remains authoritative.

---

# Request State

In a project that uses the CLI, `pdfannex.sty` writes build-state information such as:

```text
<jobname>.pdfannex-requests
```

Writing is opt-in: the file is written only if `pdfannex.lock` exists in the working directory. `pdfannex init` creates an empty lock for that purpose. Without a lock, the package writes no extra files.

This format is internal.

It:

- may be regenerated;
- is not a user-editable project format;
- is not Resolver Protocol 1;
- is not consumed directly by resolvers.

---

# External-Source Build Lifecycle

Conceptually:

```text
LaTeX
  ↓
discover source request
  ↓
request state
  ↓
pdfannex prepare
  ↓
resolver.resolve()
  ↓
local PDF
  ↓
generic validation
  ↓
hash + artifact store + lock
  ↓
resolved.tex
  ↓
LaTeX rerun
  ↓
annex included
```

LaTeX's normal multi-pass model remains responsible for document pagination and references.

Source resolution MUST NOT occur once per LaTeX pass.

---

# Canonical Build Command

The desired day-to-day build command is:

```bash
latexmk document.tex
```

for both:

- local PDFs;
- externally prepared sources.

The `pdfannex` CLI is a preparation dependency, not a competing TeX build engine.

There is no required public:

```text
pdfannex build
```

command in v0.1.

---

# `latexmk` Integration

`latexmk` owns:

- TeX invocation;
- dependency convergence;
- `.aux` reruns;
- `.loa` reruns;
- final document convergence.

The project should supply reusable `latexmk` integration for external-source preparation.

A custom dependency can conceptually trigger:

```text
pdfannex prepare
```

when request state changes or required generated state is missing.

---

# `latexmk` Integration Reality

`latexmk` custom dependencies are configured through its RC mechanism.

Therefore the v0.1 requirement is:

> After one-time integration enablement, the normal build command MUST remain `latexmk document.tex`.

The CTAN distribution SHOULD ship a reusable integration file, for example conceptually:

```text
pdfannex_latexmkrc
```

Possible enablement mechanisms include:

- a one-line project `.latexmkrc`;
- a user-level `latexmk` RC include;
- a future upstream/native integration;
- tooling that safely installs or generates the required RC configuration.

The package MUST NOT overwrite a user's global `latexmk` configuration.

Zero-project-configuration integration remains desirable, but MUST NOT be promised until demonstrated reliably across supported environments.

Local PDF usage requires no special `latexmk` configuration.

---

# Unresolved External Sources

An external source may require one discovery/preparation pass before it can be physically included.

A build containing an unresolved required external annex MUST NOT be considered successfully complete.

The implementation may temporarily omit physical pages during the discovery pass so request state can be written, but:

- preparation must occur;
- LaTeX must rerun;
- the converged build must include the annex;
- preparation failure must fail the build.

Direct engine invocation without required external-source preparation should produce a clear diagnostic rather than silently yielding a complete-looking document with missing annexes.

---
