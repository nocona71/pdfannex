# 0019 Fast isolated package tests and CTAN end-to-end coverage

- Context: the project ships CTAN upload ZIPs and TDS ZIPs, but does not build TeX Live `.tar.xz` archives with `tlpobj` metadata. `tlmgr install --file` therefore cannot install the current package artifacts.
- Decision: provide a focused `make test-fast` target that builds packages in temporary trees, installs the core and adapter TDS/CTAN layouts into isolated TEXMF trees, and verifies resolver use and a locked rebuild. The clean-container end-to-end workflow tests both release CTAN ZIPs, including core CLI behavior and the docstore adapter's locked rebuild.
- Consequences: fast tests exercise the produced layouts without modifying the host TeX installation. A separate `tlmgr` test can be added if the project begins producing TeX Live package archives; CTAN ZIPs must not be passed to `tlmgr`.
