# `pdfannex` CLI

The optional CLI owns only external artifact preparation and reproducibility.

Responsibilities:

```text
consume request state
deduplicate requests
group requests
select resolvers
invoke Resolver Protocol 1
validate protocol results
validate returned PDFs
SHA-256
artifact store
lockfile
resolution map
update
status
verify
```

It MUST NOT implement:

```text
annex numbering
page layout
LaTeX references
List of Annexes
bookmarks
TeX rerun convergence
provider-specific source semantics
backend-specific integration logic
```

---

# CLI Implementation

Preferred initial implementation:

```text
texlua
```

Rationale:

- available with normal TeX distributions;
- avoids mandatory Python/Node/Rust runtime for the generic CLI;
- sufficient for filesystem, hashing and orchestration requirements.

Use project-owned wrappers for:

```text
hashing
filesystem
process execution
structured serialization
```

Implementation language is not part of any public protocol.

---

# CLI Commands

Human-facing external-source commands may include:

```bash
pdfannex update document.tex
pdfannex status document.tex
pdfannex verify document.tex
```

Build integration may use:

```bash
pdfannex prepare document.tex
```

`prepare` is primarily a machine/build-system command.

---

# Normal Build Fast Path

When:

```text
request unchanged
lock entry valid
artifact present
resolution map current
```

a normal build should perform:

```text
resolver discovery   0
describe calls       0
resolve calls        0
status calls         0
downloads            0
network requests     0
```

This is a core external-source performance requirement.

---

# Explicit Updates

Only explicit user intent may advance mutable external sources.

Example:

```bash
pdfannex update document.tex
```

Update flow:

```text
read requested locators
      ↓
invoke relevant resolvers
      ↓
materialize new PDFs
      ↓
generic validation
      ↓
hash/store
      ↓
construct full replacement lock
      ↓
atomic replace
      ↓
regenerate resolution map
```

Old immutable artifacts remain preserved.

---

# Transactional Updates

Lockfile updates MUST be transactional.

Required pattern:

```text
resolve all required updates
materialize all
validate all
hash all
store immutable objects
construct complete new lock
write temporary lock
flush / close
atomic rename
regenerate generated state
```

Failure before final replacement leaves the old lock intact.

---

# Status

Optional:

```bash
pdfannex status document.tex
```

This may ask resolvers whether mutable requested sources have changed.

Generic states:

```text
up-to-date
update-available
unknown
error
```

A resolver not supporting status yields `unknown` or a clear unsupported status.

No lock modification occurs.

---

# Verify

```bash
pdfannex verify document.tex
```

operates locally by default.

Check:

- lock schema;
- required artifact existence;
- SHA-256;
- plausible PDF format;
- generated resolution consistency where practical.

Verification must not require upstream access.

---
