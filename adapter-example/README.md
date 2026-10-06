# adapter-example: template for pdfannex resolvers

A complete, dependency-free example of a pdfannex source adapter (Resolver
Protocol 1). Copy this directory as the start of your own adapter (Paperless,
SharePoint, an HTTP server, ...). Nothing here depends on the rest of the
pdfannex repository; it needs only `texlua` (TeX Live) and Python 3 for the tests.

| File | Purpose |
|---|---|
| `pdfannex-resolver-docstore` | The adapter: a texlua executable speaking Protocol 1 on stdin/stdout |
| `adapter-lib.lua` | Minimal JSON and SHA-256 helpers (copy along) |
| `conformance.py` | Generic protocol conformance check for any resolver |
| `test_docstore.py` | Module tests of the adapter alone (`make test`) |
| `pdfannex-docstore.sty` | Optional: a nicer command name for the scheme |

## What the example serves

`pdfannex://docstore/<id>[?rev=<n>]` from a directory laid out as:

```text
$PDFANNEX_DOCSTORE_DIR/<id>/<n>.pdf      (default directory: ./docstore)
```

| Aspect | Where to look |
|---|---|
| Source options (`?rev=`) and `unsupported-source-option` | `lookup` |
| Pinning a floating request to a concrete revision | `resolve_one` (`resolved`) |
| Update and tamper detection | `status_one` |
| Refusing symlinks and non-PDF content | `check_revision` |
| Configuration through the environment | `lookup` |
| Protocol plumbing: `describe`, errors, protocol version | bottom of the file |

## Use it with pdfannex

1. Put `pdfannex-resolver-docstore` and `adapter-lib.lua` in one directory on
   `PATH` (the CLI finds `pdfannex-resolver-SCHEME`).
2. In the document, write the URI or define a command:

   ```latex
   \usepackage{pdfannex}
   \NewAnnexSource{\includedoc}{docstore}   % or \usepackage{pdfannex-docstore}
   ...
   \includedoc[label=contract]{contract-42}{Contract}
   \includeannex{pdfannex://docstore/contract-42?rev=2}{Contract, rev. 2}
   ```

3. Build once (without `-halt-on-error`), then `pdfannex init` and
   `pdfannex prepare document.tex`. `pdfannex status document.tex` reports
   `update-available` when a newer revision appears; `pdfannex update
   document.tex` accepts it.

The package needs no knowledge of the adapter: any scheme name works with
`\NewAnnexSource`. Adapters are arbitrary code, so the CLI runs them only from
`prepare` and `update`, never while compiling. Secrets belong in the environment,
never in the lock, the requests file or the document.

## Build your own adapter

1. Copy this directory and rename the executable to `pdfannex-resolver-SCHEME`.
2. Replace `SCHEME` and the body of `lookup`; keep the protocol plumbing.
3. Adapt `test_docstore.py`. The module tests cover what an adapter must get
   right before any integration test: invalid sources and options, a deleted
   or emptied store, tampered content, symlinks, unreadable files, batches
   with mixed results and malformed requests. Hash checking against the lock
   is the pdfannex CLI's job, not the adapter's.
4. Check protocol conformance of any resolver:

   ```bash
   cd project && python3 /path/to/conformance.py \
     /path/to/pdfannex-resolver-SCHEME SCHEME pdfannex://SCHEME/good pdfannex://SCHEME/missing
   ```

Behaviour worth keeping: revisions must be regular files that start with
`%PDF-`; `status` reports `update-available` when a newer revision exists or
when the locked revision's bytes changed, and an error when it was deleted.
