# Out-of-Scope Architectural Extension: Rich Resource Providers

This section is informative only.

It illustrates why the resolver boundary deliberately separates provider identity from backend technology.

A future application such as an Obsidian plugin may need richer operations:

```text
search
get metadata
list/browse
materialize
thumbnail
relationships
watch
```

These do not belong in Resolver Protocol 1.

Resolver Protocol 1 intentionally answers the narrower question:

> **Given a source locator, materialize the PDF needed by `pdfannex`.**

---

# Out-of-Scope Example: Obsidian External Resources

A future Obsidian integration might use:

```text
                        Obsidian
                           │
                           ▼
              External Resources plugin
                           │
                           ▼
              richer Resource Provider API
                           │
                           ▼
                  provider implementation
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
            MCP          REST/API        CLI
```

The provider implementation may combine those technologies privately, just as a `pdfannex` resolver can.

The richer provider API would support discovery and browsing, which are intentionally outside `pdfannex`.

---

# Out-of-Scope Example: Shared Integration Core

A future external-system integration could expose multiple thin consumer-specific frontends:

```text
                         Paperless-ngx
                              │
                   implementation backends
                              │
                ┌─────────────┼─────────────┐
                │             │             │
               MCP           REST          CLI
                │             │             │
                └─────────────┼─────────────┘
                              │
                   Paperless integration core
                              │
             ┌────────────────┴────────────────┐
             │                                 │
             ▼                                 ▼
    Resource Provider frontend          Resolver frontend
             │                                 │
             ▼                                 ▼
       Obsidian plugin                     pdfannex
```

This is only an implementation pattern.

Neither Resolver Protocol 1 nor a future resource-provider protocol needs to expose the internal backend composition.

---

# Out-of-Scope Example: Generic MCP Reuse

An MCP bridge may allow multiple existing integrations to be reused:

```text
                     pdfannex CLI
                          │
                  Resolver Protocol 1
                          │
                          ▼
                pdfannex-resolver-mcp
                          │
                         MCP
                          │
             ┌────────────┼────────────┐
             ▼            ▼            ▼
         Paperless      Zotero      other MCP
          server         server       server
```

The bridge is still just a resolver from `pdfannex`'s perspective.

Its MCP mapping strategy is private implementation detail.

---

# Out-of-Scope Example: Resource Lookup

A richer consumer may offer:

```text
user types:
"Steuerbescheid 2025"
         │
         ▼
search provider
         │
         ▼
candidate resources
         │
         ▼
user selects resource
         │
         ▼
stable resource identity
```

The principle is:

> **Search discovers identities; human-readable names are not stable identities.**

This may later inform editor integrations for `pdfannex`, but it is explicitly outside the CTAN package v0.1.

---
