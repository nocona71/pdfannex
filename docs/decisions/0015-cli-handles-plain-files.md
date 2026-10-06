# 0015 The CLI handles plain files itself
- Context: plain paths are already read by `pdfannex.sty` (self-contained CTAN use), and the CLI already hashes, stores and locks. A separate `pdfannex-resolver-file` program duplicated that and showed nothing about extensibility (decision 0014 provides the template instead).
- Decision:
  1. `pdfannex-resolver-file` is removed. The CLI serves `pdfannex://file/<path>` with a built-in handler: `resolve` returns the project file, `status` compares `lockedSha256` with the current bytes.
  2. The scheme and the lock format are unchanged (`pdfannex://file/<percent-encoded path>`), so existing locks stay valid and the explicit URI still works.
  3. Confinement rules are kept and tested through the CLI: no absolute paths, no `..`, no symbolic links, no options (`invalid-source`, `permission-denied`, `unsupported-source-option`).
  4. All other schemes still go through `pdfannex-resolver-SCHEME` programs (spec/08).
- Consequences: the locked-mode suites still prove store-only builds for files; adapter behavior is proven by the docstore tests. The spec has one built-in scheme and otherwise only external resolvers.
