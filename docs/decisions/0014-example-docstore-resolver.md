# 0014 Example docstore resolver and `\NewAnnexSource`
- Context: the goal is simple extensibility and the same command pattern for different PDF sources. A file adapter does not show that: plain paths are already read by the package (self-contained CTAN use), and the CLI already hashes and locks. A numeric-only adapter was too thin to be a template.
- Decision:
  1. `\NewAnnexSource{\cmd}{scheme}` in `pdfannex.sty` defines `\cmd[opts]{ref}{title}` as `\includeannex[opts]{pdfannex://scheme/ref}{title}`. The scheme is any name; the package never validates or knows adapters. Adapter discovery stays in the CLI (`pdfannex-resolver-SCHEME` on `PATH`).
  2. `examples/pdfannex-resolver-docstore` is the showcase and fork-start. It serves `pdfannex://docstore/<id>[?rev=n]` from a local directory. It shows source options, pinning a floating request to a revision (`resolved`), `status` update detection, error codes and environment configuration. An optional `examples/pdfannex-docstore.sty` shows an adapter-specific command name.
  3. Adapters are not shipped in the CTAN archive; the example lives in `examples/` and is covered by `testfiles/test_cli.py`.
- Open (not done yet): routing plain paths through `pdfannex-resolver-file` duplicates what the CLI does. Plan: the CLI locks plain paths itself, and the file resolver becomes a test fixture or is removed. A document-wide `scheme=` shorthand key is deferred.
- Consequences: a new adapter needs no change to the package; mixed-source documents use one lock and one map.
