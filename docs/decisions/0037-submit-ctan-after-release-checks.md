# Submit CTAN releases after tagged release checks

## Context

Release Please creates GitHub Releases using `GITHUB_TOKEN`. GitHub suppresses
new workflow runs for events created with that token, so a `release: published`
trigger alone would not run for the normal Release Please release. Releases
published by other means should still be handled automatically.

## Decision

Use Release Please's `release_created` and `tag_name` outputs to call a reusable
workflow in the same run. That workflow builds and attaches the archive, runs
the clean-container E2E test, then submits the exact tested archive. Also
trigger it for `release: published` events so releases created outside the
Release Please pipeline go through the same checks. The workflow validates the
tag against `VERSION` and uses `l3build upload` only after all checks pass.

Require the repository Actions secret `CTAN_EMAIL`; do not store uploader
contact data in the source tree. Keep manual workflow dispatch available for
retrying a specific published tag.

## Consequences

No separate personal access token is needed for the normal Release Please
pipeline, and CTAN submission is blocked until its release E2E check passes.
Repository setup requires the uploader email secret. CTAN's own review remains
outside the workflow.
