# 0026 Report the package version from the CLI

- Context: the bundled CLI reported a hard-coded `0.1.0` after the core package had advanced to later releases, and release automation did not update the separate literal.
- Decision: have `pdfannex --version` read the version from `pdfannex.sty`, the package's release-managed version source.
- Consequences: CLI output follows the installed or checked-out package without duplicate version constants; package E2E tests verify the version from the archive.
