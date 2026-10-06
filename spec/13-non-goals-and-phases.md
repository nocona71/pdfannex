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
