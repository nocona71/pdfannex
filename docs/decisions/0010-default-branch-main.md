# 0010 Default branch is `main`; workflows trigger on it
- Context: the repository was created with `master`, but CI and release-please (from the paperlessngx-latex template) triggered on `main`, so they never ran on pushes. `main` is the current default for GitHub and Git tooling.
- Decision: rename the default branch to `main`; keep `ci.yml` and `release-please.yml` on `main`. (An interim commit pointed them at `master`; superseded.)
- Consequences: CI runs on pushes and pull requests to `main`.
