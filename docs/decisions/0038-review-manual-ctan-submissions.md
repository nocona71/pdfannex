# 0038 Review manual CTAN submissions before upload

## Context

GitHub Actions manual dispatch inputs cannot be populated from live release
data. The manual CTAN workflow also needs an operator to inspect the final
announcement, metadata, and exact archive before an irreversible upload.
CTAN does not expose a reliable upload-status lookup; an accepted upload may
temporarily be absent from both its unprocessed uploads page and package page
while maintainers process it.

## Decision

Run manual dispatches only from `main`. A blank release-tag input lists
published releases whose tags are valid and whose tagged `VERSION` matches;
the operator then dispatches again with an eligible tag. An optional
announcement overrides the GitHub Release body.

Build and E2E-test the archive before creating a read-only payload preview.
Use workflow artifacts for the tested archive and announcement, show the
archive checksum, and verify both payload checksums after approval. Gate only
manual submissions with the protected `ctan-manual-review` environment; the
automatic Release Please path remains unpaused.

Before a manual retry, require the operator to check the previous CTAN response
and, if ambiguous, CTAN's unprocessed uploads and package pages. If neither
shows the upload while CTAN may be processing it, wait or contact CTAN rather
than immediately resubmitting.

## Consequences

The repository must configure `ctan-manual-review` with at least one required
reviewer. Listing eligible tags and submitting require separate dispatches.
GitHub Actions retains the submission response in the run log, while CTAN's
processing remains an external operation without a reliable status endpoint.
