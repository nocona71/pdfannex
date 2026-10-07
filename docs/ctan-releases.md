# CTAN releases

## Automatic release flow

Publishing a GitHub Release starts the CTAN submission workflow, using the
release tag as the authoritative version. For Release Please releases, the
same workflow is called from the Release Please run because GitHub suppresses
new workflow runs for releases created with `GITHUB_TOKEN`. The archive job
checks the tag against `VERSION`, runs the release checks, builds and attaches
the versioned CTAN archive, and the clean-container E2E job tests that exact
archive. CTAN submission runs only after those checks pass.

Releases published outside the Release Please pipeline also start CTAN
submission directly.

## Repository setup

Before the first automated submission, add the repository Actions secret
`CTAN_EMAIL` with the uploader's CTAN contact email. `l3build` includes this
address in the submission. No CTAN password or API token is required by the
upload command.

Manual submissions pause for approval in the protected `ctan-manual-review`
environment. It currently requires approval from `nocona71`; manage reviewers
under **Settings → Environments**. Without a required reviewer, GitHub does
not pause the submission job for review. Automatic Release Please submissions
use a separate, unprotected environment and are not paused.

## Initial CTAN listing

The first CTAN submission must use CTAN's [web upload form](https://ctan.org/upload).
The Ubuntu 24.04 runner's packaged `l3build` has a first-upload bug: when the
package is not yet listed, it can report success without uploading. The
upstream fix is not included in Ubuntu's TeX Live package.

Run the manual workflow to build, test, and review the release. Download the
`pdfannex-ctan-archive` and `pdfannex-ctan-announcement` artifacts from that
run, then use the archive, announcement, and metadata shown in the preview
when submitting through CTAN's form. Wait until
[the package page](https://ctan.org/pkg/pdfannex) is published before using
the workflow for automated updates. The submission job checks that page and
fails explicitly while the package is not listed.

## Manual release flow

1. In **Actions → Build and submit CTAN release**, select the `main` branch.
   Manual runs from another branch are rejected.
2. To list eligible releases, leave **Release tag** blank and run the workflow.
   The `Resolve release` job summary lists published, non-prerelease tags
   matching `pdfannex-vX.Y.Z` whose tagged `VERSION` matches. Run it again with
   the exact tag to submit.
3. Optionally enter a CTAN announcement. If blank, the workflow uses the
   selected GitHub Release body. The final announcement must be nonempty and
   no more than 8192 bytes.
4. The workflow builds the archive, runs the clean-container E2E test, then
   produces a read-only **CTAN submission preview**. Review its metadata,
   announcement, archive filename, and SHA-256 checksum.
5. The submission job waits for approval in `ctan-manual-review`. Approving
   allows the workflow to download the same tested archive and announcement;
   it verifies both checksums before running `l3build upload`.

The preview redacts the uploader email. It reports only whether `CTAN_EMAIL`
is configured. The archive and announcement are passed as workflow artifacts
so the reviewed content is the content submitted.

## Checking a submission before retrying

The `l3build upload` step prints CTAN's response in the GitHub Actions log.
If the response confirms the upload succeeded, do not resubmit that version.
For an ambiguous result, inspect [CTAN's Unprocessed Uploads](https://ctan.org/incoming)
and the [pdfannex package page](https://ctan.org/pkg/pdfannex) for the target
version.

An upload being processed by CTAN maintainers may temporarily appear in neither
place. If the previous run is ambiguous and the version is not visible yet,
wait or contact CTAN before retrying; do not immediately submit a duplicate.
The manual workflow requires an explicit confirmation that this check was
performed.

CTAN submissions are reviewed by CTAN maintainers; a successful workflow means
the package was submitted, not necessarily that it is already published in the
archive.

The manual workflow dispatch can also be used to retry an existing
`pdfannex-vX.Y.Z` release tag after the receipt check above. Set the
**Confirm CTAN has not received this version** checkbox only after checking
the previous result.
