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
| 0013 | [File resolver is the first Resolver Protocol 1 adapter](0013-file-resolver-first-adapter.md) | accepted |
