# Definition of Done — Core Package

The following must work without external tooling:

```latex
\documentclass[a4paper]{article}

\usepackage{pdfannex}

\pdfannexsetup{
  heading=Annexes,
  layout=footer-safe,
  page-style=plain
}

\begin{document}

Main document.

See \annexref{contract}.

\listofannexes

\includeannex[
  label=contract
]{letter-sized-contract.pdf}{
  Contract
}

\includeannex[
  label=report,
  pages=1-3,
  frame=true
]{legal-sized-report.pdf}{
  Report
}

\end{document}
```

with:

```bash
latexmk document.tex
```

Expected:

- correct annex numbering;
- correct document pagination;
- proportional page fitting;
- no footer/source overlap;
- correct first-page tracking;
- aux-based List of Annexes (decision 0007);
- working references;
- unique hyperlink targets;
- clean bookmarks;
- no source-specific logic;
- no network access;
- no shell execution;
- no class-specific dependency.

---

# Definition of Done — Optional External Source Flow

Given:

```latex
\includeannex[
  label=tax-assessment,
  source={pdfannex://mock/4711?selector=latest}
]{Tax assessment}
```

the external-source layer should be capable of:

```text
discover request
      ↓
invoke preparation
      ↓
resolver.resolve()
      ↓
local PDF + resolved locator
      ↓
generic protocol/artifact validation
      ↓
SHA-256
      ↓
artifact store
      ↓
lock
      ↓
resolved.tex
      ↓
LaTeX rerun
      ↓
annex included
```

A subsequent unchanged build must perform zero source-resolution operations.

Failure to resolve the required source must fail the build.

---

# Release Gate

## Core CTAN package

Required for v0.1:

- local PDF workflow works;
- `pdfpages` integration works;
- layouts work;
- list of annexes works;
- references work;
- bookmarks work;
- pagination works;
- representative class tests pass;
- representative engine tests pass;
- no CLI required for local use.

## External-source companion layer

May mature alongside the package, but MUST NOT block the usefulness or releaseability of the core package.

Before its interfaces are treated as stable:

- mock resolver passes;
- generic resolver-result validation works;
- transactional locking works;
- locked rebuild performs zero resolver calls;
- MCP bridge spike has been evaluated;
- at least one real source system has validated the abstraction.

---

# Final Design Principles

> **The CTAN package comes first.**

> **A local PDF annex requires only `\usepackage{pdfannex}` and normal LaTeX tooling.**

> **An annex is a semantic role assigned to a PDF, not a source type.**

> **`pdfpages` owns physical PDF inclusion.**

> **LaTeX owns page numbers, references, lists and document convergence.**

> **`pdfannex.sty` knows document semantics, not source systems.**

> **External source identity does not encode backend technology.**

> **Resolver Protocol 1 is the only external integration contract owned by `pdfannex`.**

> **Resolver Protocol calls describe required outcomes, not backend workflows.**

> **`describe`, `resolve`, and optionally `status` map directly to resolver implementation capabilities.**

> **A resolver may use MCP, REST, SDKs, CLIs, databases, or any combination internally.**

> **Backend composition is private resolver implementation detail.**

> **A successful `resolve` result asserts that the returned artifact represents the returned resolved source.**

> **The `pdfannex` CLI validates protocol and artifact properties generically, not provider semantics.**

> **MCP should be reused when useful, but must not become a core dependency.**

> **Human search discovers resources; human-readable names are not stable identities.**

> **Human search, browsing and virtual mounts belong to richer future provider layers, not Resolver Protocol 1.**

> **`pdfannex.sty` never parses the lockfile.**

> **A locked build performs zero source-resolution operations.**

> **An ordinary build never silently advances a mutable source.**

> **Presentation changes never trigger source resolution.**
