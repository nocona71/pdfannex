# Decision log

One short file per decision: `NNNN-title.md` with Context, Decision, Consequences.
Add a new file whenever a design or process decision is made. Never silently change old ones; supersede them.

| # | Decision | Status |
|---|---|---|
| 0001 | [Spec split by topic into `spec/`](0001-spec-split-by-topic.md) | accepted |
| 0002 | [Use `pagecommand*` for first-page work](0002-pagecommand-first-page.md) | accepted |
| 0003 | [Legacy code lives in `legacy/`; `spec/` is the live source](0003-legacy-and-spec-layout.md) | accepted |
| 0004 | [Dev/CI/release infra from paperlessngx-latex](0004-dev-ci-release-infra.md) | accepted |
| 0005 | [Devcontainer needs texlive-fonts-recommended](0005-devcontainer-fonts-recommended.md) | accepted |
| 0006 | [`pagecommand` plus first-page flag](0006-pagecommand-with-first-page-flag.md) | accepted (supersedes 0002) |
| 0007 | [List of annexes built from `.aux`](0007-aux-based-list-of-annexes.md) | accepted |
| 0008 | [Fit-to-sheet scaling may enlarge small pages](0008-fit-to-sheet-may-enlarge.md) | accepted |
| 0009 | [`pagination=continue` via shipout counter](0009-pagination-continue-shipout-counter.md) | accepted |
| 0010 | [Default branch is `main`](0010-default-branch-main.md) | accepted |
| 0011 | [End-to-end test of the CTAN archive](0011-ctan-archive-e2e-test.md) | accepted |
| 0012 | [Per-file n-up (`nup` key)](0012-nup-per-file.md) | accepted |
| 0013 | [File resolver is the first Resolver Protocol 1 adapter](0013-file-resolver-first-adapter.md) | partly superseded by 0015 |
| 0014 | [Example docstore resolver and `\NewAnnexSource`](0014-example-docstore-resolver.md) | partly superseded by 0016 and 0032 |
| 0015 | [CLI handles plain files itself](0015-cli-handles-plain-files.md) | accepted |
| 0016 | [Package adapters for CTAN distribution](0016-package-adapters-for-ctan.md) | accepted |
| 0017 | [Keep adapter CI separable](0017-adapter-ci-composite-action.md) | adapter extracted; superseded by 0032 |
| 0018 | [Track only intentional project files](0018-track-only-intentional-files.md) | accepted |
| 0019 | [Fast isolated package tests and CTAN end-to-end coverage](0019-package-test-levels.md) | superseded by 0020 and 0032 |
| 0020 | [TeX Live package-manager end-to-end tests](0020-texlive-package-manager-e2e.md) | partly superseded by 0032 |
| 0021 | [Use the host Docker daemon from the devcontainer](0021-devcontainer-docker-access.md) | accepted |
| 0022 | [Cross-platform CLI resolver execution](0022-cross-platform-cli-resolvers.md) | accepted |
| 0023 | [Quote Windows child-process arguments](0023-windows-child-process-arguments.md) | accepted |
| 0024 | [Use native Windows paths for atomic replacement](0024-native-windows-paths-for-file-replacement.md) | accepted |
| 0025 | [Use a temporary backup for Windows file replacement](0025-backup-for-windows-file-replacement.md) | accepted |
| 0026 | [Report the package version from the CLI](0026-cli-uses-package-version.md) | accepted |
| 0027 | [Document manual native TeX Live installation check](0027-manual-native-texlive-sanity-check.md) | accepted |
| 0028 | [Opt-in `latexmk` source bootstrap](0028-opt-in-latexmk-bootstrap.md) | accepted |
| 0029 | [Install TDS artifacts in a native user tree](0029-texmfhome-tds-installer.md) | partly superseded by 0032 |
| 0030 | [Support `latexmk` output directories](0030-latexmk-output-directories.md) | accepted |
| 0031 | [Smoke-test release TDS artifacts with first-build `latexmk`](0031-release-tds-latexmk-smoke-test.md) | adapter half moved to pdfannex-docstore; partly superseded by 0032 |
| 0032 | [Keep core packaging and QA in the core repository](0032-core-repository-owns-core-package-only.md) | accepted |
| 0033 | [Use plain-text annex references in PDF bookmarks](0033-plain-text-references-in-bookmarks.md) | accepted |
| 0034 | [Preserve local PDF paths literally](0034-preserve-local-pdf-paths-literally.md) | accepted |
| 0035 | [Track reproducible showcase PDF fixtures](0035-track-showcase-pdf-fixtures.md) | accepted |
| 0036 | [Use larger manual PDF previews](0036-larger-manual-pdf-previews.md) | accepted |
| 0037 | [Submit CTAN releases after tagged release checks](0037-submit-ctan-after-release-checks.md) | accepted |
| 0038 | [Review manual CTAN submissions before upload](0038-review-manual-ctan-submissions.md) | accepted |
| 0039 | [Close issue #1 for per-file n-up](0039-close-issue-1-per-file-nup.md) | accepted |
| 0040 | [Bound APT waits in GitHub Actions](0040-bound-apt-waits-in-github-actions.md) | accepted |
| 0041 | [Prefer HTTPS Ubuntu archive on hosted runners](0041-prefer-https-ubuntu-archive.md) | accepted |
