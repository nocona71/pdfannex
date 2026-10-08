# CTAN releases

## Manual release flow

Publishing a GitHub Release does not trigger CTAN packaging or submission. To
prepare or submit a release, manually run **Actions → Build and submit CTAN
release** on `main`, selecting the published release tag. The workflow checks
the tag against `VERSION`, runs the release checks, builds and attaches the
versioned CTAN archive, and tests that exact archive in a clean container.

The **Submit to CTAN** option is unchecked by default. Leave it unchecked to
build and review the archive and announcement without uploading; this is the
path for the initial submission through CTAN's web form. Check it only for an
update after the package is listed on CTAN. That path uses `l3build upload`
and waits for approval in `ctan-manual-review`.

## Repository setup

Before using **Submit to CTAN**, add the repository Actions secret `CTAN_EMAIL`
with the uploader's CTAN contact email. `l3build` includes this address in the
submission. No CTAN password or API token is required by the upload command.

Submissions pause for approval in the protected `ctan-manual-review`
environment. It currently requires approval from `nocona71`; manage reviewers
under **Settings → Environments**. Without a required reviewer, GitHub does
not pause the submission job for review.

## Initial CTAN listing

The first CTAN submission must use CTAN's [web upload form](https://ctan.org/upload).
The Ubuntu 24.04 runner's packaged `l3build` has a first-upload bug: when the
package is not yet listed, it can report success without uploading. The
upstream fix is not included in Ubuntu's TeX Live package.

For the first submission, run the workflow with **Submit to CTAN** unchecked.
Download the `pdfannex-ctan-archive` and `pdfannex-ctan-announcement` artifacts,
then use the archive, announcement, and metadata shown in the preview when
submitting through CTAN's form. Wait until
[the package page](https://ctan.org/pkg/pdfannex) is published before using
**Submit to CTAN** for updates.

To list eligible releases, leave **Release tag** blank and run the workflow.
The `Resolve release` job summary lists published, non-prerelease tags
matching `pdfannex-vX.Y.Z` whose tagged `VERSION` matches. Run it again with
the exact tag to prepare or submit. Optionally enter a CTAN announcement. If
blank, the workflow uses the selected GitHub Release body. The final
announcement must be nonempty and no more than 8192 bytes.

The workflow produces a read-only **CTAN submission preview**. Review its
metadata, announcement, archive filename, and SHA-256 checksum. For an update,
check **Submit to CTAN**; the submission job waits for approval in
`ctan-manual-review`, then verifies the downloaded archive and announcement
against the preview checksums before running `l3build upload`.

The preview redacts the uploader email and reports only whether `CTAN_EMAIL`
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

For a retry, run the manual workflow for the existing `pdfannex-vX.Y.Z` tag,
check **Submit to CTAN**, and set the **Confirm CTAN has not received this
version** checkbox only after checking the previous result.
