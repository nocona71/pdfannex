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

# PDF-Only Core

The canonical artifact consumed by `pdfannex.sty` is a PDF.

The core does not directly consume:

```text
PNG
JPEG
TIFF
SVG
DOCX
ODT
HTML
remote URL
Paperless ID
Zotero ID
cloud object
database row
```

Anything else must first produce a PDF.

Examples:

```text
Paperless document
       ↓
resolver / external tooling
       ↓
PDF
       ↓
pdfannex.sty
```

```text
image
  ↓
converter
  ↓
PDF
  ↓
pdfannex.sty
```

The package MUST NOT become a general conversion framework.

---

# LaTeX Dependencies

Use mature existing infrastructure.

Required or expected core dependencies:

```text
pdfpages
hyperref
bookmark
modern LaTeX kernel
expl3 / l3keys where useful
```

`pdfpages` is the sole low-level PDF inclusion engine.

Do not require:

```text
KOMA-Script
scrlayer-scrpage
fancyhdr
memoir
```

These are compatibility targets, not dependencies.

---

# Public LaTeX API

## Local PDF inclusion

Canonical command:

```latex
\includeannex[<options>]{<pdf-file>}{<title>}
```

Example:

```latex
\includeannex[
  label=contract,
  pages=1-3,
  layout=footer-safe
]{contract.pdf}{
  Contract
}
```

---

## External source inclusion

When external source support is enabled, the same semantic annex pipeline is used:

```latex
\includeannex[
  source={pdfannex://paperless/4711},
  label=tax-assessment
]{Tax assessment}
```

The exact command parsing may internally distinguish local and source-based forms, but they MUST converge on one annex inclusion implementation.

External source support MUST NOT introduce source-specific public commands into the core package.

---

# Required Annex Options

v0.1 should keep the option surface deliberately small.

Required:

```text
label
pages
source
layout
page-style
frame
bookmark
list
```

Potentially:

```text
scale
margin
footer-space
```

when required by the geometry implementation.

Do not expose low-level `pdfpages` configuration wholesale in v0.1.

A controlled escape hatch may be considered later.

---

# Global Configuration

Provide:

```latex
\pdfannexsetup{
  annex-name=Annex,
  heading=Annexes,
  layout=footer-safe,
  page-style=plain,
  pagination=inherit
}
```

Required global properties:

```text
annex-name
heading
layout
page-style
pagination
```

---

# Annex Identity

Annex number and semantic identity are different concepts.

Example:

```latex
\includeannex[
  label=contract
]{contract.pdf}{
  Contract
}
```

The annex might currently be:

```text
Annex 3
```

and later become:

```text
Annex 4
```

without changing its semantic identity.

The stable document identity is:

```text
contract
```

not:

```text
3
```

---

# Annex Counter

Use a normal LaTeX counter:

```text
annex
```

Default:

```text
Annex 1
Annex 2
Annex 3
```

Users may redefine:

```latex
\renewcommand\theannex{\Roman{annex}}
```

Do not hard-code Arabic numbering.

---

# Canonical Inclusion Pipeline

All annex inclusion MUST use one canonical internal pipeline.

Conceptually:

```text
resolve local PDF path
      ↓
validate
      ↓
increment annex counter
      ↓
create semantic target
      ↓
establish reference state
      ↓
calculate layout
      ↓
invoke pdfpages
      ↓
detect first inserted document page
      ↓
write .loa metadata
      ↓
create bookmark
```

Private implementation names may use:

```text
\__pdfannex_...
```

No external integration may depend on private implementation commands.

---

# `pdfpages` Integration

`pdfpages` owns physical PDF-page insertion.

Use it for:

- source-page selection;
- page fitting;
- scaling;
- positioning;
- framing;
- per-page commands;
- first-page-only commands.

Do not create a competing rendering path with `\includegraphics`.

---

# First-Page Processing

Use current `pdfpages` first-page facilities such as `pagecommand*` where suitable.

First-page work includes:

```text
semantic hyperlink target
label/reference state
first document page
List-of-Annexes entry
bookmark
```

Per-page work includes:

```text
page style
footer/page number
presentation
```

Avoid a custom first-page state machine unless required by demonstrated `pdfpages` behavior.

---

# Native LaTeX Multi-Pass Model

LaTeX owns document structural state.

Use:

```text
.aux
```

for ordinary references.

Use:

```text
<jobname>.loa
```

for the List of Annexes.

Expected flow:

```text
LaTeX pass 1
    ↓
write .aux / .loa
    ↓
LaTeX pass 2
    ↓
resolved list and references
    ↓
additional pass only if pagination changed
```

Do not implement a second document-indexing engine.

Do not use `makeindex` for the primary List of Annexes.

---

# List of Annexes

Provide:

```latex
\listofannexes
```

Conceptual output:

```text
Annexes

Annex 1: Contract ........................ 4
Annex 2: Medical report .................. 7
Annex 3: Invoice ........................ 12
```

Entries MUST contain:

- annex number;
- title;
- first document page;
- semantic hyperlink.

---

# `.loa` Data

Store semantic data rather than preformatted visual lines.

Conceptually:

```latex
\pdfannexlistentry
  {contract}
  {3}
  {Contract}
  {17}
  {pdfannex.contract}
```

Do not persist:

```text
Annex 3: Contract ............ 17
```

as formatted output.

Formatting occurs when the list is rendered.

---

# List Heading

Do not hard-code:

```latex
\chapter*{Annexes}
```

or:

```latex
\section*{Annexes}
```

Use a class-neutral default and an overridable heading implementation.

---

# References

For:

```latex
\includeannex[
  label=contract
]{contract.pdf}{
  Contract
}
```

provide:

```latex
\annexref{contract}
```

```latex
\annexpageref{contract}
```

```latex
\annexlink{contract}{see the contract}
```

Use normal LaTeX reference infrastructure wherever practical.

---

# Hyperlink Destinations

Do not use logical page anchors such as:

```text
page.17
```

as annex identity.

Logical page numbers may repeat after class- or environment-induced resets.

Create semantic destinations such as:

```text
pdfannex.contract
```

or equivalent unique internal targets.

The displayed page number and hyperlink identity are independent.

---

# Bookmarks

Desired PDF outline:

```text
document
Annexes
    Annex 1: Contract
    Annex 2: Medical report
```

`pdfannex.sty` owns only its own bookmark subtree.

It MUST NOT globally reconfigure `hyperref` or `bookmark`.

---

# Page Geometry

The core must distinguish:

```text
source PDF page size
```

from:

```text
output document sheet size
```

Sources may include:

```text
A4
A5
Letter
Legal
landscape
custom sizes
mixed-size pages
```

while the host document uses another paper size.

This is page placement, not source-file conversion.

---

# Default Geometry

Default policy:

```text
sheet-size=document
fit=contain
```

Meaning:

- preserve host document sheet size;
- preserve source aspect ratio;
- shrink as necessary;
- do not crop by default;
- do not upscale by default;
- never stretch non-uniformly.

---

# Annex Content Area

Use one central abstraction:

```text
output sheet
    minus
annex margins
    minus
reserved footer/header areas
    =
annex content area
```

Fit each source page into this area.

---

# v0.1 Layouts

Required named layouts:

```text
fullpage
footer-safe
framed
```

## `fullpage`

Use the maximum appropriate page area.

Typical semantics:

```text
minimal annex margin
no reserved footer
no frame
```

## `footer-safe`

Reserve clean whitespace for host document pagination/footer.

Source content must not be obscured by the host footer.

This is the recommended default for formal documents.

## `framed`

Provide modest surrounding space and a visible frame.

Prefer existing `pdfpages` frame facilities.

---

# Margins

Support:

```text
margin
footer-space
```

in v0.1 where necessary.

Directional margins are deferred.

---

# Orientation

Default:

```text
orientation=preserve
```

Do not silently rotate pages.

Automatic orientation is deferred.

---

# Mixed-Size PDFs

One PDF may contain pages with different dimensions.

Each source page must be fitted independently.

The entire source may still represent one semantic annex.

---

# Page Style

Allow the user to select an already defined LaTeX page style.

Default:

```text
plain
```

Do not require or configure:

```text
fancyhdr
scrlayer-scrpage
```

---

# Pagination

The normal LaTeX:

```text
page
```

counter remains the document page counter.

Desired behavior:

```text
main document          page 1
main document          page 2
List of Annexes        page 3
Annex 1 page 1         page 4
Annex 1 page 2         page 5
Annex 2 page 1         page 6
```

Do not introduce a separate visible annex-page numbering system in v0.1.

---

# Pagination Modes

Provide:

```text
pagination=inherit
pagination=continue
```

## `inherit`

Default.

Use the current logical page-counter state.

## `continue`

Ensure annex page numbering continues from already emitted document pages where a host class/environment has reset logical page numbering.

This MUST be tested with `scrlttr2`.

---

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

When an external source has no prepared artifact, `pdfannex.sty` may write build-state information such as:

```text
<jobname>.pdfannex-requests
```

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

# Testing Infrastructure

Use `l3build` for the LaTeX package.

CLI and resolver protocol tests may use separate tooling if appropriate.

---

# Required PDF Fixtures

Provide small deterministic fixtures:

```text
a4-one-page.pdf
a5-one-page.pdf
letter-one-page.pdf
legal-one-page.pdf
landscape.pdf
multipage.pdf
mixed-pagesize.pdf
edge-content.pdf
```

---

# Required Geometry Tests

Test:

```text
A4 → A4
A5 → A4
Letter → A4
Legal → A4
landscape source
mixed-size source
```

Verify:

- aspect ratio preserved;
- no unintended crop;
- no non-uniform stretching;
- footer reservation;
- frame placement;
- document pagination.

---

# Required Multi-Pass Tests

Verify:

- `.loa` written correctly;
- List of Annexes resolves;
- page changes propagate;
- annex reordering changes annex numbers;
- labels remain stable;
- hyperlink targets remain unique;
- `latexmk` converges normally.

---

# `scrlttr2` Regression

Test annex insertion after:

```latex
\begin{letter}{...}
...
\end{letter}
```

Verify:

- no annex-induced duplicate destination warning;
- `pagination=continue`;
- correct first annex page;
- correct List-of-Annexes page;
- footer-safe layout.

---

# External-Source Tests

When companion tooling is included, test:

```text
unresolved request discovery
resolver selection
missing resolver
describe success
protocol incompatibility
resolve success
resource-not-found
authentication failure
batch resolution
deduplication
partial batch failure
invalid resolver output
artifact missing
non-PDF artifact
locked rebuild → zero resolver calls
exact recovery
hash mismatch
transactional rollback
resolution-map regeneration
```

No test should depend on how a resolver internally obtains its result.

---

# v0.1 Explicit Non-Goals

The following are not part of the core v0.1 CTAN package:

```text
human resource search
resource browser
virtual filesystem
Obsidian integration
resource-provider standard
MCP client inside pdfannex.sty
source-specific .sty adapters
adapter registry
automatic adapter installation
REST resolver daemon
generic backend composition model
backend reconciliation protocol
global artifact store
hybrid artifact store
garbage collection
vendor command
hierarchical annex groups
automatic orientation
rich provenance manifest
generic document conversion framework
embedded originals
annotation preservation
form preservation
tagged-PDF preservation
full final-PDF bit reproducibility
GUI
editor plugin
```

---

# Implementation Phases

## Phase A — `pdfannex.sty`

This is the primary v0.1 milestone.

Implement:

```text
package skeleton
configuration keys
annex counter
\includeannex
pdfpages integration
first-page hook
semantic anchors
references
.loa
\listofannexes
bookmarks
fullpage
footer-safe
framed
pagination
class tests
engine tests
```

This phase MUST be independently useful and releasable.

---

## Phase B — generic external-source tooling

Implement only after the core package architecture is stable:

```text
texlua CLI
request state
project-local artifact store
SHA-256
lock schema
resolution map
latexmk helper
Resolver Protocol 1
prepare
update
status
verify
transactionality
```

---

## Phase C — resolver validation

Validate Resolver Protocol 1 with:

- a mock/reference resolver;
- at least one real external system;
- the MCP bridge spike.

Paperless-ngx is a useful proving case because it exercises:

```text
mutable latest
historical revisions
authentication
PDF download
update checks
```

The internal implementation of the Paperless resolver may use MCP, REST, CLI, or any mixture.

That choice is intentionally irrelevant to Resolver Protocol 1.

---

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
- `.loa`-based List of Annexes;
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
- `.loa` works;
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

> **Do not make the v0.1 CTAN package pay for future ecosystem possibilities.**