# External Sources — Optional Companion Layer

Everything below this section concerns optional external-source support.

It MUST NOT affect the local-PDF bootstrap experience.

The key architectural rule is:

> **`pdfannex.sty` does not know how external systems work.**

---

# `pdfannex Source Locator`

An external source may be expressed as:

```text
pdfannex://<provider>/<resource>?<provider-specific-query>
```

Examples:

```text
pdfannex://paperless/4711
pdfannex://paperless/4711?selector=latest
pdfannex://zotero/ABCD1234
pdfannex://nextcloud/Documents/report.pdf
```

The namespace is owned by the `pdfannex` project.

Do not reuse third-party application schemes such as:

```text
zotero:
obsidian:
vscode:
```

which may already have host-OS application semantics.

---

# Provider Identity vs Backend Technology

The locator identifies the **semantic provider**, not the integration technology.

Good:

```text
pdfannex://paperless/4711
```

Bad:

```text
pdfannex://paperless-mcp/4711
pdfannex://paperless-rest/4711
```

The same source locator should remain valid whether the implementation internally uses:

```text
MCP
REST
GraphQL
vendor SDK
CLI
local database
or several of these together
```

Backend selection is an implementation detail.

It MUST NOT leak into document source identity.

---

# Resolver Boundary

The `pdfannex` project owns one small external integration contract:

> **Resolver Protocol 1**

Conceptually:

```text
pdfannex.sty
      │
      ▼
request state
      │
      ▼
pdfannex CLI
      │
      ▼
Resolver Protocol 1
      │
      ▼
resolver implementation
      │
      ▼
local PDF
```

The resolver boundary isolates the TeX/document layer from changing external integration technologies.

---

# Resolver Calls Map Directly to Implementation Capabilities

Resolver Protocol 1 models only operations visible to `pdfannex`.

Conceptually:

```text
describe
    ↓
resolver.describe()

resolve
    ↓
resolver.resolve()

status
    ↓
resolver.status()
```

The protocol does not model the resolver's internal workflow.

A resolver may internally make:

```text
one backend call
many backend calls
MCP calls
REST calls
CLI calls
SDK calls
database queries
any combination
```

without this becoming visible in Resolver Protocol 1.

This is an explicit abstraction rule:

> **Protocol operations describe required outcomes, not backend execution plans.**

---

# Backend-Agnostic Resolver Implementation

A resolver MAY use any implementation technology.

```text
                     Resolver Protocol 1
                              │
                              ▼
                           resolver
                              │
             ┌────────────────┼────────────────┐
             │                │                │
             ▼                ▼                ▼
            MCP            REST/API           CLI
```

The branches above are private implementation details.

The resolver may use one, several, or none of them.

No additional protocol semantics are introduced merely because multiple backend technologies are used.

---

# Resolver Result Contract

A successful `resolve` result asserts:

> **The returned local artifact is the resolver's materialization of the returned resolved source.**

Conceptually:

```json
{
  "id": "tax-assessment",
  "resolved": "pdfannex://paperless/4711?version=98273",
  "artifact": {
    "path": "/tmp/document.pdf"
  }
}
```

The `pdfannex` CLI does not ask:

- whether MCP was used;
- whether REST was used;
- how many backend calls occurred;
- whether results from several systems were combined;
- which SDK implemented the source access.

Those are resolver implementation concerns.

---

# Generic Result Validation

The `pdfannex` CLI validates only properties that are generic to Resolver Protocol 1 and PDF artifact handling.

Examples:

```text
valid protocol response
matching request/result ID
syntactically acceptable resolved locator
artifact path exists
artifact is readable
artifact is plausibly a PDF
SHA-256 can be calculated
locked SHA-256 matches during exact recovery
```

The CLI MUST NOT contain provider-specific validation logic such as:

```text
Paperless version semantics
Zotero item semantics
Nextcloud revision semantics
```

Provider correctness belongs to the resolver implementation.

---
