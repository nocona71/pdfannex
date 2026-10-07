# 0039 Close issue #1 for per-file n-up

## Context

Issue #1 proposed putting multiple PDFs on one output sheet. Decision 0012
scoped v0.1 to `nup` over pages from one PDF and left issue #1 open for future
cross-file grouping. The per-file behavior is now implemented, tested, and
shown in the documentation showcase.

## Decision

Narrow issue #1 to per-file n-up and close it as complete. Combining different
PDF files on one sheet remains out of scope; any future work on that behavior
must be tracked and designed separately.

## Consequences

Closing issue #1 records completion of the supported per-file behavior; it
does not imply that cross-file grouping is implemented or committed to a
release.
