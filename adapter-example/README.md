# adapter-example: template for pdfannex resolvers

A complete, self-contained example of a pdfannex source adapter (Resolver
Protocol 1). Copy this directory as the start of your own adapter (Paperless,
SharePoint, ...). Nothing here depends on the rest of the pdfannex repository;
runtime use needs `texlua` (TeX Live) and `curl`; Python 3 is needed only for
the mock server and tests.

| File | Purpose |
|---|---|
| `pdfannex-resolver-docstore` | The adapter: a texlua executable speaking Protocol 1 on stdin/stdout |
| `adapter-lib.lua` | Minimal JSON, file and SHA-256 helpers (copy along) |
| `docstore_server.py` | Mock document service (HTTP) with fault injection, for tests and demos |
| `conformance.py` | Generic protocol conformance check for any resolver |
| `test_docstore.py` | Module tests of the adapter alone (`make test`) |
| `test_integration.py` | Plain files and docstore documents in one document, with the real pdfannex package and CLI (`PDFANNEX_HOME`, default `..`; skipped if absent) |
| `test_package.py` | CTAN/TDS archive checks and isolated TDS/CTAN install locked-build tests (`make test-fast`) |
| `e2e_ctan.py` | End-to-end install test for the built core and adapter CTAN archives |
| `build.lua`, `ctan/` | Standalone `l3build` configuration and user-facing package docs |
| `pdfannex-docstore.sty` | Optional companion package; requires pdfannex dated 2026/05/01 or later |
| `.github/actions/test/action.yml` | Composite test action invoked by the monorepo CI and reusable after extracting this directory |
| `.github/workflows/ci.yml` | Workflow template; GitHub activates it only after this directory is a repository root |

The composite action runs `make test` and accepts `pdfannex-home` for the core
checkout used by integration tests. In this repository, root CI invokes it with
the workspace path. After separating this directory, the workflow template
checks out `nocona71/pdfannex` beside the adapter and passes that checkout path.
The caller must install the test tools listed in the workflow template.

Run the focused installed-package test with `make test-fast`; it builds core
and adapter packages in temporary trees and verifies isolated TDS and CTAN
installations, resolver selection and a locked rebuild. CI additionally has a
fresh-container TeX Live package-manager test: it installs only the adapter
from a local repository, confirms `tlmgr` installs the declared core dependency,
then tests both local and docstore PDFs through a locked rebuild.

Build the separate CTAN/TDS package with `make package`. The CTAN archive is
`pdfannex-docstore-ctan.zip`; the TDS archive is
`build/distrib/tds/pdfannex-docstore.tds.zip`. The package contains the
companion `.sty`, resolver, helper library, README, license, PDF manual and a
resolver man page.

## What the example serves

`pdfannex://docstore/<id>[?rev=<n>]` from an HTTP document service:

```text
GET /docs/<id>            -> {"id": "<id>", "latest": <n>}
GET /docs/<id>/<n>.pdf    -> PDF bytes          (Authorization: Bearer <token>)
```

Configuration comes from the environment: `PDFANNEX_DOCSTORE_URL` (required),
`PDFANNEX_DOCSTORE_TOKEN` (optional) and `PDFANNEX_DOCSTORE_TIMEOUT` (seconds,
default 30). The token is handed to curl through a private temporary config
file, so it never appears in the process list. HTTP errors map to protocol
errors: 401 `authentication-required`, 403 `permission-denied`, 404
`resource-not-found`, anything else `temporarily-unavailable`.
If curl is missing, the resolver returns `temporarily-unavailable` with an
install/PATH hint; `describe` itself does not require curl.

Try it: `python3 docstore_server.py ROOT --token SECRET` serves
`ROOT/<id>/<n>.pdf`; then export the two variables above.

| Aspect | Where to look |
|---|---|
| Source options (`?rev=`) and `unsupported-source-option` | `parse_source` |
| Pinning a floating request to a concrete revision | `resolve_one` (`resolved`) |
| Update and tamper detection | `status_one` |
| Refusing non-PDF content | `remote_revision` |
| Configuration, curl call, error mapping | `fetch` |
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
`\NewAnnexSource`. Adapters are arbitrary code, so the CLI runs them from
`prepare`, `update` and `status`, never while compiling. Secrets belong in the
environment, never in the lock, the requests file or the document.

## Build your own adapter

1. Copy this directory and rename the executable to `pdfannex-resolver-SCHEME`.
2. Replace `SCHEME`, `parse_source`, `fetch` and the service calls; keep the
   protocol plumbing.
3. Adapt `test_docstore.py`. The module tests cover what an adapter must get
   right before any integration test: invalid sources and options, a deleted
   document, server outages, bad credentials, redirects, timeouts, tampered content, garbage metadata, batches
   with mixed results and malformed requests. Hash checking against the lock
   is the pdfannex CLI's job, not the adapter's.
4. Check protocol conformance of any resolver:

   ```bash
   cd project && python3 /path/to/conformance.py \
     /path/to/pdfannex-resolver-SCHEME SCHEME pdfannex://SCHEME/good pdfannex://SCHEME/missing
   ```

Resolve artifacts are temporary files (`/tmp/lua_*`) that the CLI moves into its
store. Behaviour worth keeping: downloads must start with `%PDF-`; `status`
reports `update-available` when a newer revision exists or when the locked
revision's bytes changed, and an error when it was deleted.
