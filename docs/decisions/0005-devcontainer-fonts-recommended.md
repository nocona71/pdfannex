# 0005: Install texlive-fonts-recommended in the devcontainer

Status: accepted

`make check` failed in the devcontainer: `pdflatex` could not find `pzdr.tfm`
(ZapfDingbats metrics, needed by `pifont`/`latex-extra`), and `mktextfm` fell
back to Metafont and failed. Adding `texlive-fonts-recommended` to
`.devcontainer/Dockerfile` provides the PSNFSS metrics. Rebuild the container.
