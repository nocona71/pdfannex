# 0031 Smoke-test release TDS artifacts with first-build `latexmk`
- Status: this repository tests the core TDS archive only; adapter TDS installation and docstore behavior are tested by the standalone [pdfannex resolver example repository](https://github.com/nocona71/pdfannex-docstore) (decision 0032).

- Context: package tests built from the checkout do not exercise the exact TDS ZIPs and installer scripts uploaded by a release workflow. Native user-tree installs can also conflict with packages already in a developer's TeX tree.
- Decision: provide an opt-in E2E script that downloads both release TDS artifacts, installs them into a temporary `TEXMFHOME`, starts an isolated docstore mock, and builds the combined showcase with one initial `latexmk` command.
- Consequences: maintainers can verify release artifacts without modifying their regular TeX tree or invoking `tlmgr`; the test requires a valid Actions run ID and native TeX tools, and Actions artifact retention applies.
