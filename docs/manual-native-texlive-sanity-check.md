# Manual native TeX Live sanity check

Use the core package's TDS artifact from a successful GitHub Actions run to
install pdfannex into your host TeX Live user's tree, then compile a custom
document. This is a persistent, unprivileged user-tree install, unlike
`testfiles/texlive_e2e.py`, which uses an isolated temporary tree.

The artifact is a TDS ZIP, not a TeX Live package-manager container. The
installer beside the ZIP writes into `TEXMFHOME`, records the installed paths,
and runs `mktexlsr`. It refuses to overwrite files already in the user tree.
If you previously extracted a TDS ZIP manually, remove or back up those old
package files first, or test in a clean separate user tree; the installer
cannot safely claim files that it did not install.

To exercise the docstore adapter's own TDS artifact the same way, see
[`pdfannex-docstore`'s manual sanity check](https://github.com/nocona71/pdfannex-docstore/blob/main/docs/manual-native-texlive-sanity-check.md),
which covers the combined core+adapter installation and smoke test.

## Download the TDS artifact

Find a successful Actions run that uploaded `pdfannex-tds-archive`, then enter
its ID:

```bash
read -r -p "Actions run ID: " RUN_ID
ARTIFACT_DIR="$HOME/pdfannex-artifacts/$RUN_ID"
mkdir -p "$ARTIFACT_DIR"
gh run download "$RUN_ID" \
  --repo nocona71/pdfannex \
  --name pdfannex-tds-archive \
  --dir "$ARTIFACT_DIR"
CORE_TDS="$ARTIFACT_DIR/pdfannex.tds.zip"
CORE_INSTALLER="$ARTIFACT_DIR/install-texmfhome-tds.sh"
test -s "$CORE_TDS"
test -s "$CORE_INSTALLER"
```

Actions artifacts expire, so choose a run whose artifacts are still available.

## Install and uninstall

Install the TDS archive without `sudo`:

```bash
bash "$CORE_INSTALLER" install "$CORE_TDS"
kpsewhich pdfannex.sty
kpsewhich -format=texmfscripts pdfannex_latexmkrc
```

The script defaults to the `TEXMFHOME` reported by `kpsewhich`. To use a
different user tree, pass it as the third argument to `install`. To remove the
package later, use the matching script and archive name:

```bash
bash "$CORE_INSTALLER" uninstall "$CORE_TDS"
```

Uninstall removes only paths recorded for that archive; unrelated files and
non-empty directories are left in place.

## Build a custom document

For a local-only document, use the core package and run the selected TeX engine
twice to settle references:

```bash
latexmk -lualatex document.tex
```

Enable the optional project-local latexmk integration as described in the
[latexmk integration guide](./latexmk-integration.md).
