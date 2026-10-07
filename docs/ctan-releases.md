# CTAN releases

## Release flow

Publishing a GitHub Release starts the CTAN submission workflow, using the
release tag as the authoritative version. For Release Please releases, the
same workflow is called from the Release Please run because GitHub suppresses
new workflow runs for releases created with `GITHUB_TOKEN`. The archive job
checks the tag against `VERSION`, runs the release checks, builds and attaches
the versioned CTAN archive, and the clean-container E2E job tests that exact
archive. CTAN submission runs only after those checks pass.

Releases published outside the Release Please pipeline also start CTAN
submission directly. The workflow supports manual dispatch to retry an
existing release tag.

## Repository setup

Before the first automated submission, add the repository Actions secret
`CTAN_EMAIL` with the uploader's CTAN contact email. `l3build` includes this
address in the submission. No CTAN password or API token is required by the
upload command.

CTAN submissions are reviewed by CTAN maintainers; a successful workflow means
the package was submitted, not necessarily that it is already published in the
archive.

When manually retrying a submission, check whether CTAN already received it
before dispatching again. Select the existing `pdfannex-vX.Y.Z` release tag in
the **Build and submit CTAN release** workflow.
