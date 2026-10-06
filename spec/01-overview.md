# `pdfannex` v0.1 — Implementation Specification

## Status

This document defines the v0.1 implementation contract for the **`pdfannex` project**, with primary emphasis on the **`pdfannex` CTAN package** and its runtime implementation **`pdfannex.sty`**.

The package must be useful independently of all external-source infrastructure.

The core v0.1 user story is:

```latex
\usepackage{pdfannex}

...

\includeannex[
  label=contract
]{contract.pdf}{
  Contract
}
```

built using ordinary LaTeX tooling.

External source resolution, immutable artifact management, resolver adapters, MCP integration and related tooling are architecturally supported but must not increase the bootstrap burden of this basic use case.

The guiding principle is:

> **An annex is a semantic role assigned to a page-oriented PDF artifact, not a type of source.**

---

## Normative Language

The terms **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** describe implementation requirements.

Anything not explicitly required for v0.1 is out of scope unless necessary to implement a required feature correctly.

The implementation should favor, in order:

1. correctness;
2. minimal user bootstrap;
3. small stable interfaces;
4. reuse of mature LaTeX infrastructure;
5. class independence;
6. reproducibility;
7. clear diagnostics;
8. minimal implementation complexity.

---

# Project Components

Use these terms consistently.

| Term | Meaning |
|---|---|
| **`pdfannex` project** | Entire ecosystem described here |
| **`pdfannex` CTAN distribution** | CTAN-distributed bundle |
| **`pdfannex` CTAN package** | LaTeX package loaded by `\usepackage{pdfannex}` |
| **`pdfannex.sty`** | Runtime LaTeX implementation |
| **`pdfannex` CLI** | Optional generic preparation/reproducibility tool |
| **`pdfannex Source Locator`** | Stable source reference such as `pdfannex://paperless/4711` |
| **Resolver Protocol 1** | Small process protocol between the CLI and resolver implementations |
| **resolver** | Implementation of Resolver Protocol 1 |
| **provider** | Semantic external source system such as `paperless`, `zotero`, or `nextcloud` |
| **backend** | Technology used internally by a resolver, e.g. MCP, REST, SDK, CLI, database |
| **`pdfannex.lock`** | Reproducibility lockfile |
| **artifact store** | Immutable project-local PDF store |
| **resolution map** | Generated TeX mapping from source identities to local PDF artifacts |
| **request state** | Generated build state describing unresolved external sources |

Avoid ambiguous bare uses of `pdfannex`.

Prefer:

> The **`pdfannex` CLI** writes `pdfannex.lock`.

and:

> **`pdfannex.sty`** includes pages through `pdfpages`.

---

# Core Architectural Boundary

The design separates two questions.

### Source question

> Where does this PDF come from?

Examples:

- local filesystem;
- Paperless-ngx;
- Zotero;
- Nextcloud;
- REST API;
- MCP server;
- external CLI;
- database;
- conversion pipeline.

This is outside `pdfannex.sty`.

### Document question

> How does this PDF participate in the final LaTeX document?

Examples:

- annex number;
- title;
- label;
- page selection;
- scaling;
- output geometry;
- page style;
- document pagination;
- List of Annexes;
- references;
- hyperlinks;
- bookmarks.

This belongs inside `pdfannex.sty`.

The concise rule is:

> **Resolvers produce PDFs. `pdfannex.sty` turns PDFs into annexes.**

---

# Capability Layers

The project should remain useful in progressively richer configurations.

```text
LEVEL 0

TeX distribution
      +
pdfannex CTAN package
      ↓
local PDF annexes
```

```text
LEVEL 1

LEVEL 0
  +
pdfannex CLI
      ↓
locked/local artifact management
```

```text
LEVEL 2

LEVEL 1
  +
resolver
      ↓
external source integration
```

```text
LEVEL 3 — OUT OF SCOPE

richer resource providers
search / browse / metadata / virtual mounts
      ↓
other consumers such as Obsidian
```

Higher levels MUST NOT be prerequisites for lower levels.

---

# v0.1 Primary Scope

The primary v0.1 deliverable is **`pdfannex.sty`**.

It MUST provide:

- annex numbering;
- titles;
- labels;
- PDF inclusion;
- source-page selection;
- geometry and scaling;
- page styles;
- pagination;
- first-page tracking;
- unique hyperlink targets;
- references;
- List of Annexes;
- PDF bookmarks;
- class-neutral operation;
- clear error handling.

The package MUST work for local PDFs without:

- the `pdfannex` CLI;
- `pdfannex.lock`;
- `.pdfannex/`;
- resolver adapters;
- MCP;
- network access;
- shell escape;
- Python;
- Node;
- Rust;
- Go;
- a source-specific `.sty`.

This independence is a release requirement.

---
