# 0010 Workflows trigger on `master`
- Context: the repository's default branch is `master`; CI and release-please were copied from a template that used `main`, so they never ran on pushes.
- Decision: point `ci.yml` and `release-please.yml` at `master`. The alternative (renaming the branch) was rejected as a larger change.
- Consequences: CI runs on pushes and pull requests to `master`.
