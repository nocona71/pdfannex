# Example resolver: docstore

`pdfannex-resolver-docstore` is a small, dependency-free Resolver Protocol 1
adapter. Copy it as the start of your own adapter (Paperless, SharePoint, an
HTTP server, ...). It needs `texlua` and the `cli/pdfannex-lib.lua` helpers.

It serves `pdfannex://docstore/<id>[?rev=<n>]` from a directory laid out as:

```text
docstore/<id>/<n>.pdf
```

| Aspect | Where to look |
|---|---|
| Source options (`?rev=`) and `unsupported-source-option` | `lookup` |
| Pinning a floating request to a concrete revision | `resolve_one` (`resolved`) |
| Update detection | `status_one` |
| Configuration through the environment (`PDFANNEX_DOCSTORE_DIR`) | `lookup` |
| Protocol plumbing: `describe`, errors, protocol version | bottom of the file |

## Use it

1. Put `pdfannex-resolver-docstore` on `PATH` (the CLI finds `pdfannex-resolver-SCHEME`).
2. In the document, either write the URI or define a command:

   ```latex
   \usepackage{pdfannex}
   \NewAnnexSource{\includedoc}{docstore}   % or \usepackage{pdfannex-docstore}
   ...
   \includedoc[label=contract]{contract-42}{Contract}
   \includeannex{pdfannex://docstore/contract-42?rev=2}{Contract, rev. 2}
   ```

3. Build once, then lock: `pdfannex init`, `pdfannex prepare document.tex`.
   `pdfannex status document.tex` reports `update-available` when a newer
   revision appears; `pdfannex update document.tex` accepts it.

## Check your own adapter

```bash
cd project && python3 ../testfiles/resolver_conformance.py \
  /path/to/pdfannex-resolver-SCHEME SCHEME pdfannex://SCHEME/good pdfannex://SCHEME/missing
```

Adapters are arbitrary code: the CLI runs them only from `prepare` and
`update`, never while compiling. Secrets belong in the environment, never in the
lock, the requests file or the document.
