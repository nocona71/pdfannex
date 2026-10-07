# Optional `latexmk` integration

The core TDS and CTAN distributions include `pdfannex_latexmkrc`. Enabling it
in a project makes the first `latexmk` build bootstrap source requests, resolve
new sources, and rerun LaTeX without a separate `pdfannex prepare` command.

## Requirements

- Install the core `pdfannex` package and CLI.
- For external sources, install the relevant resolver and its support files.
- Ensure `pdfannex`, resolver scripts, and any resolver dependencies are on
  `PATH`; export resolver configuration such as service URLs and tokens in the
  environment inherited by `latexmk`.
- Run `latexmk` from the document's project directory.

## Enable it for one project

Add the following to the project's `.latexmkrc`:

```perl
my $pdfannex_rc = `kpsewhich -format=texmfscripts pdfannex_latexmkrc`;
$pdfannex_rc =~ s/\r?\n\z//;
die "pdfannex latexmk integration not found\n"
    unless $pdfannex_rc && -f $pdfannex_rc;
require $pdfannex_rc;
```

Then use the normal build command:

```bash
latexmk document.tex
```

The integration creates `pdfannex.lock` on first use, records requests during
the TeX pass, and runs `pdfannex prepare` after that pass. If preparation
changes `.pdfannex/resolved.tex`, `latexmk` reruns TeX. A preparation failure
fails the build. For this discovery pass, unresolved external annexes produce
a warning and are omitted temporarily; the successful final run includes the
resolved annexes. Without this project-local integration, unresolved external
sources remain errors.

Already-locked builds use the project-local artifacts and do not contact
resolvers. Upstream changes are never accepted automatically; use
`pdfannex update document.tex` when you intend to advance a source. The
integration does not modify global `latexmk` configuration.
