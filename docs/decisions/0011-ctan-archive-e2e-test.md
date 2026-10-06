# 0011 End-to-end test of the CTAN archive
- Context: unit and smoke tests run against the repository tree (`TEXINPUTS=tex:`), so they cannot show that the shipped archive works for a user.
- Decision: `scripts/e2e-ctan <zip>` unpacks the archive, installs `pdfannex.sty` into an empty `TEXMFHOME`, checks the package is invisible before installing, builds the spec/15 example with `latexmk` on pdfLaTeX, XeLaTeX and LuaLaTeX (page count, text, sheet size, convergence) and builds the shipped manual. `make e2e` runs it locally in a fresh `HOME`.
- Isolation: the devcontainer has no Docker, so the "clean container" is the `ctan-e2e.yml` workflow, which runs the script in `ubuntu:24.04` with only the TeX Live packages a user needs. CI runs it on the archive built from the checkout; the release workflow runs it on the published release asset.
- Consequences: a release whose archive is broken fails the release workflow after publishing; fix forward with a patch release.
