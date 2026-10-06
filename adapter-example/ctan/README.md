# pdfannex-docstore

An optional docstore adapter for the `pdfannex` LaTeX package. It provides
`\includedoc[options]{id}{title}` for including documents from an HTTP
docstore.

## Requirements

- `pdfannex` dated 2026/05/01 or later (version 0.2.0 or later).
- `texlua`, provided by TeX Live, to run the resolver.
- `curl` on `PATH` when resolving or checking docstore sources.

The adapter does not access the network during LaTeX compilation. Run
`pdfannex prepare`, `update` or `status` to contact the service. If curl is
missing, the resolver reports that it must be installed and available on
`PATH`. Locked builds use the stored PDF objects and do not require curl or the
resolver.

## Installation and use

Install `pdfannex` and `pdfannex-docstore`. Make sure the TeX distribution makes
the `pdfannex-resolver-docstore` script available on `PATH`; otherwise add its
scripts directory. Install curl separately if it is not already available.

```latex
\usepackage{pdfannex-docstore}
...
\includedoc[label=contract]{contract-42}{Contract}
```

Set `PDFANNEX_DOCSTORE_URL` to the service base URL and, if needed,
`PDFANNEX_DOCSTORE_TOKEN` to a bearer token. The resolver implements
`pdfannex://docstore/<id>[?rev=<n>]`. Without `rev`, it pins the latest
revision during `prepare`.

For the protocol details and test server, see the
[adapter-example repository](https://github.com/nocona71/pdfannex/tree/main/adapter-example).

## License

This package is distributed under the LaTeX Project Public License 1.3c or
later. See `LICENSE`.
