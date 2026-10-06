# Backend Composition Is Private

A resolver may, for example, implement:

```text
resolve()
    ├── MCP metadata request
    └── REST PDF download
```

or:

```text
resolve()
    ├── REST lookup
    ├── vendor SDK
    └── local CLI conversion
```

Resolver Protocol 1 sees only:

```text
resolve(request)
      ↓
result or error
```

No generic "backend reconciliation" stage is defined in v0.1.

If an implementation needs consistency checks between its own backend calls, those checks are ordinary resolver implementation logic.

They are not a separate `pdfannex` architectural concept.

---

# MCP Position

MCP is a **preferred reusable backend building block**, not a dependency of `pdfannex.sty` and not the protocol owned by the `pdfannex` project.

A resolver SHOULD consider using an existing suitable MCP server when this avoids reimplementing source-specific integration logic.

A resolver MAY instead or additionally use:

- a direct REST/GraphQL API;
- a vendor SDK;
- an existing CLI;
- a local service;
- a database;
- another protocol.

Existing MCP support does not need to be complete.

For example, a resolver may privately implement:

```text
MCP        → metadata/search
REST       → PDF retrieval
```

without changing Resolver Protocol 1.

---

# Why MCP Is Behind the Resolver Boundary

Existing MCP servers may expose equivalent source systems through different MCP resources or tools.

For example, PDF retrieval could be exposed as:

```text
resources/read
download_document
document_download
get_file
```

All may be legitimate MCP designs.

A deterministic LaTeX build must not infer source semantics from arbitrary tool names.

Resolver Protocol 1 therefore remains the stable semantic boundary.

---

# Generic MCP Bridge

A possible implementation is:

```text
pdfannex-resolver-mcp
```

Conceptually:

```text
pdfannex CLI
      │
Resolver Protocol 1
      │
      ▼
pdfannex-resolver-mcp
      │
      ▼
MCP SDK
      │
      ▼
existing MCP server
```

The bridge may use declarative or provider-specific mapping internally where needed.

That mapping is outside Resolver Protocol 1.

---

# MCP Architecture Spike

Before freezing the final Resolver Protocol 1 wire schema, perform a small MCP integration spike.

Test at least:

- one tool-oriented MCP server;
- one resource-oriented MCP server where available;
- source lookup;
- deterministic source identity;
- PDF acquisition;
- large PDF handling;
- compatibility with existing MCP implementations.

Success criterion:

> A PDF can be reproducibly resolved through an existing MCP integration without source-specific HTTP logic inside the `pdfannex` core.

The spike may affect resolver implementation choices but MUST NOT expand the responsibilities of `pdfannex.sty`.

---

# Resolver Discovery

Default v0.1 convention:

For:

```text
pdfannex://paperless/...
```

look for:

```text
pdfannex-resolver-paperless
```

on `PATH`.

For:

```text
pdfannex://zotero/...
```

look for:

```text
pdfannex-resolver-zotero
```

This convention says nothing about the resolver's internal backend.

A resolver may itself use MCP or delegate to a generic MCP bridge.

A more elaborate resolver registry or routing system is deferred until demonstrated necessary.

---
