# 0013 The file resolver is the first Resolver Protocol 1 adapter
- Status: the standalone `pdfannex-resolver-file` was removed by decision 0015; the CLI handles `pdfannex://file/` itself. The rest still holds.
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
- Consequences: the Resolver Protocol is exercised end to end before any network resolver exists. 
- Implemented (v0.1 slice): `cli/pdfannex` (`prepare`, `update`, `status`, `verify`), `cli/pdfannex-resolver-file`, shared `cli/pdfannex-lib.lua` (JSON, SHA-256 via LuaTeX `sha2`, filesystem, process wrappers), `adapter-example/conformance.py`, `testfiles/test_cli.py`.
- Request state: `pdfannex.sty` writes `<jobname>.pdfannex-requests` (one normalized source per line) and reads `.pdfannex/resolved.tex`. A locked plain path builds from the stored object; an unlocked plain path is used directly; an unlocked `pdfannex://` URI is a LaTeX error.
- Symlinks are refused by the file resolver in v0.1 rather than resolved. `status` passes `lockedSha256` to resolvers that can use it (content-addressed sources).
- Recording requests is opt-in: `pdfannex.sty` writes `<jobname>.pdfannex-requests` only if `pdfannex.lock` exists. `pdfannex init` creates an empty lock. Users without the CLI get no extra files and no write-permission dependency.
- Any file name is allowed. TeX and the CLI exchange sources hex-encoded (UTF-8 bytes) in `<jobname>.pdfannex-requests` and `.pdfannex/resolved.tex`, so no catcode, shell or TeX-special character can break the generated files. In the TeX argument, `%`, `#`, `&` and `_` are written escaped (`\%` etc.). The lock stores the source as written (`source`); plain paths map to `pdfannex://file/<percent-encoded path>`, which the file resolver decodes.
- Locked paths are rescanned before `\includepdf`, because pdfpages on XeTeX miscounts pages for a path made only of catcode-12 letters.
- The test suites also run in locked mode (`PDFANNEX_TEST_LOCKED=1`): sources are locked through the CLI, the original PDFs are deleted, and the build must succeed from the store alone. Windows support is tracked in issue #5.
- Not done: shipping the CLI in the CTAN archive, `latexmk` helper, `pdfannex.lock` handling of Windows shells (the CLI uses POSIX `sh`).
