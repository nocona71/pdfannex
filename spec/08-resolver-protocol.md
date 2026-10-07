# Resolver Protocol 1

Resolver Protocol 1 should remain deliberately small.

Transport:

```text
local process
JSON on stdin
JSON on stdout
diagnostics on stderr
```

Required operations:

```text
describe
resolve
```

Optional operation:

```text
status
```

No v0.1:

```text
REST resolver daemon
persistent plugin server
generic repository browser
search protocol
virtual filesystem
backend execution graph
backend reconciliation protocol
```

---

# `describe`

Every resolver MUST support:

```text
describe
```

Purpose:

- implementation identity;
- Resolver Protocol compatibility;
- optional operation discovery.

Conceptual request:

```json
{
  "operation": "describe"
}
```

Conceptual response:

```json
{
  "resolver": {
    "name": "paperless",
    "version": "1.4.2"
  },
  "protocolVersions": [1],
  "capabilities": [
    "resolve",
    "status"
  ]
}
```

`resolve` is mandatory.

`status` is optional.

Batch resolution is mandatory in Protocol 1 and does not need a separate capability flag.

---

# Protocol Compatibility

The CLI MUST verify compatibility before invoking a resolver operationally for the first time in a process invocation.

If no common Resolver Protocol version exists:

- do not call `resolve`;
- emit a clear diagnostic;
- fail non-zero.

Protocol version and resolver implementation version are independent.

---

# `resolve`

Conceptual request:

```json
{
  "protocolVersion": 1,
  "operation": "resolve",
  "requests": [
    {
      "id": "tax-assessment",
      "source": "pdfannex://paperless/4711?selector=latest"
    }
  ]
}
```

Conceptual success:

```json
{
  "protocolVersion": 1,
  "results": [
    {
      "id": "tax-assessment",
      "resolved": "pdfannex://paperless/4711?version=98273",
      "artifact": {
        "path": "/tmp/document.pdf"
      }
    }
  ]
}
```

The resolver returns a readable local PDF.

The resolver does not own:

- artifact SHA-256 as the `pdfannex` lock authority;
- artifact-store import;
- lockfile persistence;
- annex rendering.

Those belong to the `pdfannex` CLI and `pdfannex.sty`.

---

# Batch Resolution

Resolver Protocol 1 MUST accept multiple requests.

Equivalent requests should be deduplicated before resolver invocation.

Example:

```text
Annex A → Paperless 4711, pages 1–2
Annex B → Paperless 4711, pages 8–10
```

means:

```text
2 semantic annexes
1 source request
1 acquired PDF artifact
```

Page selection is a presentation concern and MUST NOT alter source identity.

---

# Structured Resolver Errors

The protocol distinguishes:

```text
resolver-level errors
request-level errors
```

Request-level examples:

```text
resource-not-found
authentication-required
permission-denied
invalid-source
unsupported-source-option
temporarily-unavailable
```

Resolver-level examples:

```text
unsupported-protocol
invalid-request
malformed-request
resolver-internal-error
```

A missing required resource MUST ultimately fail the document build.

It MUST NOT silently remove an annex.

---

# Partial Batch Failure

Resolvers SHOULD return all per-request results they can obtain.

Example:

```text
A → success
B → resource-not-found
C → success
```

The CLI may preserve successfully acquired immutable artifacts.

However, transactional lock updates MUST NOT commit an incomplete new project state when required requests failed.

---

# Standard Streams

Resolver Protocol 1 reserves:

```text
stdin   → machine request
stdout  → protocol response only
stderr  → human/debug diagnostics
```

Human logging MUST NOT contaminate stdout.

---

# Resolver Exit Status

Recommended semantics:

```text
0
    valid protocol response was produced

non-zero
    resolver-level failure prevented normal protocol completion
```

Per-request resource failures should normally appear in structured response data.

---

# Human Resource Lookup

Human-readable search is intentionally **not part of Resolver Protocol 1**.

For example:

```text
"Steuerbescheid 2025"
```

is not stable resource identity.

Search should return candidates carrying stable identifiers.

Conceptually:

```text
search("Steuerbescheid 2025")
    ↓
candidate resources
    ↓
user selects
    ↓
stable source locator
```

The resulting document should store something such as:

```text
pdfannex://paperless/4711
```

not the human title.

Human lookup, autocomplete and resource browsing are important future integration scenarios but are out of scope for the CTAN package v0.1.

---

# Resolver Conventions

Resolver scripts and discovery:

- A resolver is a texlua-compatible script named `pdfannex-resolver-SCHEME`, discoverable on `PATH` or in the TeX scripts tree (see `spec/07`).
- The CLI invokes resolver scripts explicitly with `texlua`; a platform-specific shebang or executable bit is not required.
- `describe` MUST list the URI schemes it handles, so a mismatch is detected before `resolve`.
- Resolvers are installed and versioned independently of `pdfannex.sty` and the CLI.
- The `file` scheme is not a resolver: the CLI handles it itself (see File Handling). [`pdfannex-docstore`](https://github.com/nocona71/pdfannex-docstore)'s `pdfannex-resolver-docstore` is the reference template for new resolvers.

Source options:

- Options are URI query parameters, for example `?selector=latest`.
- An unknown option MUST yield `unsupported-source-option`.

Configuration and secrets:

- A resolver reads configuration from environment variables named `PDFANNEX_SCHEME_*` (scheme upper-cased) and MAY use its own config file.
- Secrets MUST NOT appear in `pdfannex.lock`, `resolved.tex`, requests or responses.

Trust:

- Resolvers are arbitrary code. The CLI MUST invoke them only from explicit commands (`prepare`, `update`), never while compiling.

Conformance:

- A conformance script SHOULD run any resolver through `describe`, a successful `resolve`, a missing resource and a malformed request. The example resolver MUST pass it.

---

# File Handling

`pdfannex://file/PATH` refers to a path relative to the project root. Plain `\includeannex` paths mean this URI. The CLI handles the scheme itself, with the semantics below; no resolver program is involved.

- Absolute paths yield `invalid-source`; `..` segments yield `permission-denied`.
- v0.1 refuses symbolic links in any path component (`permission-denied`), instead of resolving them.
- The resolved identity equals the requested locator, since plain files have no revision.
- Plain files take no source options; any option yields `unsupported-source-option`.
- Content-addressed resolvers have no upstream revision. A `status` request MAY therefore carry `lockedSha256`, and the CLI compares it with the current file bytes (`up-to-date` or `update-available`). Without it the state is `unknown`.

---
