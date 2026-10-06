# 0013 The file resolver is the first Resolver Protocol 1 adapter
- Context: builds must be reproducible even if a source PDF changes or is tampered with (spec/09). Local files need the same protection as external systems.
- Decision:
  1. Hashing, the project-local store, `pdfannex.lock` and `resolved.tex` stay in the CLI (spec/09). A resolver only acquires a readable PDF.
  2. `pdfannex-resolver-file` is the first and reference resolver. It speaks Protocol 1 over stdin/stdout like any other, handles `pdfannex://file/<project-relative path>`, and is shipped with the CLI.
  3. It only serves paths inside the project root (no absolute paths, no `..`, symlinks resolved before the check), so a foreign `.tex` cannot import arbitrary files into the store.
  4. The CLI promotes plain `\includeannex` paths to `pdfannex://file/…` during `pdfannex lock`; existing documents need no changes.
  5. Resolution happens only in explicit CLI commands, never as a side effect of compiling. A normal build makes zero resolver calls.
  6. A locked artifact whose bytes change is an error, never silently replaced (spec/09). `--update` is explicit.
  7. Third-party resolvers follow spec/08 "Resolver Conventions" (naming, configuration, source options, conformance script).
- Package side: `pdfannex.sty` works unchanged without CLI or lock; a `pdfannex://` source is looked up in `resolved.tex`, and a missing entry errors with a hint to run `pdfannex lock`.
- Consequences: the Resolver Protocol is exercised end to end before any network resolver exists. Remaining implementation (CLI skeleton, store, lock, conformance script) is Phase B/C work and is not started.
