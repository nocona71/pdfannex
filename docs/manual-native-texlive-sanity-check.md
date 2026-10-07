# Manual native TeX Live sanity check

Use the core TDS artifacts from a successful GitHub Actions run to install
pdfannex into a TeX Live user's tree and compile a custom document. This is a
persistent, unprivileged user-tree install, unlike the automated test, which
uses an isolated temporary tree.

## Download the TDS artifacts

Find a successful Actions run that uploaded `pdfannex-tds-archive`, then enter
its ID:

```bash
read -r -p "Actions run ID: " RUN_ID
ARTIFACT_DIR="$HOME/pdfannex-artifacts/$RUN_ID"
mkdir -p "$ARTIFACT_DIR/core"
gh run download "$RUN_ID" \
  --repo nocona71/pdfannex \
  --name pdfannex-tds-archive \
  --dir "$ARTIFACT_DIR/core"
CORE_TDS="$ARTIFACT_DIR/core/pdfannex.tds.zip"
CORE_INSTALLER="$ARTIFACT_DIR/core/install-texmfhome-tds.sh"
test -s "$CORE_TDS" && test -s "$CORE_INSTALLER"
```

Actions artifacts expire, so choose a run whose artifacts are still available.

## Automated clean-tree first-build test

To test the TDS ZIP without changing your normal TeX tree, run this from a
pdfannex checkout with `gh` authenticated:

```bash
python3 testfiles/release_tds_latexmk_e2e.py RUN_ID
```

The script downloads the core TDS archive and installer, installs them into a
temporary `TEXMFHOME`, and runs an initial `latexmk` build without manually
invoking `pdfannex init` or `pdfannex prepare`. It checks that the lock and
resolution map are created, the PDF and references are correct, and a
subsequent locked rebuild succeeds after the original PDF is removed.

Requirements are Python 3, `gh`, and native TeX Live tools including
`kpsewhich`, `mktexlsr`, `pdflatex`, LuaLaTeX, `latexmk`, `pdftotext`, and
`texlua`. This tests a clean user-tree installation; it does not install a
second TeX Live distribution or use `tlmgr`.

## Install and uninstall

Install the TDS archive without `sudo`:

```bash
bash "$CORE_INSTALLER" install "$CORE_TDS"
kpsewhich pdfannex.sty
kpsewhich -format=texmfscripts pdfannex
kpsewhich -format=texmfscripts pdfannex_latexmkrc
```

The installer defaults to the `TEXMFHOME` reported by `kpsewhich`. To use a
different user tree, pass it as the third argument to `install`. To uninstall:

```bash
bash "$CORE_INSTALLER" uninstall "$CORE_TDS"
```

Uninstall removes only paths recorded for that archive; unrelated files and
non-empty directories are left in place. If you previously extracted a TDS ZIP
manually, remove or back up those package files first, or test in a clean
separate user tree; the installer cannot safely claim files it did not install.

## Build a custom document

For a local-PDF document, load `pdfannex`, include the source PDF, and run the
selected TeX engine twice to settle references. The optional `latexmk`
integration is documented in the [latexmk integration guide](./latexmk-integration.md).

External source resolver examples, including provider configuration and their
own install/test procedures, are maintained in the
[pdfannex resolver example repository](https://github.com/nocona71/pdfannex-docstore).
