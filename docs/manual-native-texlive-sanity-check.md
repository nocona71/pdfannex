# Manual native TeX Live sanity check

Use the TDS artifacts from a successful GitHub Actions run to install the core
package and optional docstore adapter into your host TeX Live user's tree, then
compile a custom document. This is a persistent, unprivileged user-tree install,
unlike `testfiles/texlive_e2e.py`, which uses an isolated temporary tree.

The artifacts are TDS ZIPs, not TeX Live package-manager containers. The
installer beside each ZIP writes into `TEXMFHOME`, records the installed paths,
and runs `mktexlsr`. It refuses to overwrite files already in the user tree.
If you previously extracted a TDS ZIP manually, remove or back up those old
package files first, or test in a clean separate user tree; the installer
cannot safely claim files that it did not install.

## Download the TDS artifacts

Find a successful Actions run that uploaded `pdfannex-tds-archive` and
`docstore-adapter-tds-archive`, then enter its ID:

```bash
read -r -p "Actions run ID: " RUN_ID
ARTIFACT_DIR="$HOME/pdfannex-artifacts/$RUN_ID"
mkdir -p "$ARTIFACT_DIR/core" "$ARTIFACT_DIR/docstore"
gh run download "$RUN_ID" \
  --repo nocona71/pdfannex \
  --name pdfannex-tds-archive \
  --dir "$ARTIFACT_DIR/core"
gh run download "$RUN_ID" \
  --repo nocona71/pdfannex \
  --name docstore-adapter-tds-archive \
  --dir "$ARTIFACT_DIR/docstore"
CORE_TDS="$ARTIFACT_DIR/core/pdfannex.tds.zip"
DOCSTORE_TDS="$ARTIFACT_DIR/docstore/pdfannex-docstore.tds.zip"
CORE_INSTALLER="$ARTIFACT_DIR/core/install-texmfhome-tds.sh"
DOCSTORE_INSTALLER="$ARTIFACT_DIR/docstore/install-texmfhome-tds.sh"
test -s "$CORE_TDS" && test -s "$DOCSTORE_TDS"
test -s "$CORE_INSTALLER" && test -s "$DOCSTORE_INSTALLER"
```

Actions artifacts expire, so choose a run whose artifacts are still available.

## Automated clean-tree first-build test

To test the released core and docstore TDS ZIPs without touching your normal
TeX tree, use a successful Actions run containing both artifacts and run this
from the repository checkout:

```bash
python3 testfiles/release_tds_latexmk_e2e.py RUN_ID
```

The script downloads both TDS artifacts and their installers with `gh`, then
creates a temporary `HOME` and `TEXMFHOME`. It confirms pdfannex is not
visible before installation, installs both archives with their companion
scripts, and checks that TeX resolves both packages from the temporary tree.
It also creates a fresh combined showcase project, generates local PDF
fixtures, and starts an in-process docstore mock serving `memo`.

The test uses a project-local `.latexmkrc` with `build/` as the output
directory. It runs only the initial `latexmk -lualatex` build—no manual
`pdfannex init` or `pdfannex prepare`—then checks that the lock and resolution
map were created, latexmk reran after resolution, the PDF contains both local
and docstore annexes with converged references, and `pdfannex verify` passes.
The temporary tree and mock server are removed when the script exits.

Requirements are `gh` authenticated for the repository, Python 3, and a native
TeX Live installation providing `kpsewhich`, `mktexlsr`, `pdflatex`, LuaLaTeX,
latexmk, `pdftotext`, `curl`, and `texlua`. This tests TDS installation into a
clean user tree; it does not install a second TeX Live distribution or use
`tlmgr`.

## Install and uninstall

Install both TDS archives without `sudo`:

```bash
bash "$CORE_INSTALLER" install "$CORE_TDS"
bash "$DOCSTORE_INSTALLER" install "$DOCSTORE_TDS"
kpsewhich pdfannex.sty
kpsewhich pdfannex-docstore.sty
kpsewhich -format=texmfscripts pdfannex_latexmkrc
```

The script defaults to the `TEXMFHOME` reported by `kpsewhich`. To use a
different user tree, pass it as the third argument to `install`. To remove the
packages later, use the matching script and archive name:

```bash
bash "$DOCSTORE_INSTALLER" uninstall "$DOCSTORE_TDS"
bash "$CORE_INSTALLER" uninstall "$CORE_TDS"
```

Uninstall removes only paths recorded for that archive; unrelated files and
non-empty directories are left in place. Uninstall the adapter before the core
package when removing both.

## Build a custom document

For a local-only document, use the core package and run the selected TeX engine
twice to settle references.

For a docstore document, keep the mock server running and export the same
service configuration in the shell that runs `latexmk`:

```bash
export PDFANNEX_DOCSTORE_URL=http://127.0.0.1:8080
export PDFANNEX_DOCSTORE_TOKEN=test-token
```

Enable the optional project-local latexmk integration as described in the
[latexmk integration guide](./latexmk-integration.md). Then run the normal
single command:

```bash
latexmk -lualatex showcase.tex
```

The first run initializes the lock, resolves the local and docstore PDFs after
the discovery pass, and reruns LuaLaTeX until references converge. A subsequent
locked build uses the stored artifacts without contacting the server. The
adapter example's [README](../adapter-example/README.md) documents the mock
server layout and resolver setup.
