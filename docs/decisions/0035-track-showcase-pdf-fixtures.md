# Track reproducible showcase PDF fixtures

## Context

The manual's visual showcase includes previews of the pages produced by a
standalone `pdfannex` example. The source PDF and resulting PDF are normally
build products and should not be tracked, but the manual needs stable input
assets and an inspectable example output.

## Decision

Track the example TeX sources and their PDFs in `doc/examples/` as intentional
documentation fixtures. The `showcase.pdf` is generated from
`showcase.tex` and `sample-attachments.pdf`; its page previews in the manual
come directly from that checked-in output. Auxiliary files such as `.aux` and
`.log` remain ignored.

Regenerate the input fixture with `pdflatex sample-attachments.tex`, then
regenerate the showcase with two pdfLaTeX runs on `showcase.tex` so references
and list entries resolve. When building from the repository checkout, set
`TEXINPUTS=../../tex:` on the showcase commands to use the working-tree
package.

## Consequences

The full example output can be reviewed without compiling it, and manual
previews show the exact checked-in result. Changes to either source require
regenerating and reviewing its corresponding PDF. These named PDFs are an
intentional exception to the repository rule against generated artifacts;
unrelated build output remains untracked.
