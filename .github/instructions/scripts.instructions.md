---
applyTo: "scripts/**,Makefile,.devcontainer/**"
---
# Scripts and devcontainer

- Scripts start with `#!/usr/bin/env bash` and `set -euo pipefail`; `make check` runs `bash -n` on them.
- Install TeX dependencies in `.devcontainer/Dockerfile` via apt only (`cm-super` is not packaged for noble; use `lmodern`).
- Run `make check` after changes; record process decisions in `docs/decisions/`.
