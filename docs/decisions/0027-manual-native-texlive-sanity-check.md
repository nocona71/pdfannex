# 0027 Document manual native TeX Live installation check

- Context: the automated TeX Live E2E test installs the TDS package in a temporary user tree and removes it afterward; users may also want to try the release artifact in their own TeX Live installation and custom documents.
- Decision: document a manual install of the core TDS artifact into `TEXMFHOME`, followed by a custom-document compile.
- Consequences: this provides a persistent, unprivileged host sanity check distinct from CI and `tlmgr` package-manager installation.
