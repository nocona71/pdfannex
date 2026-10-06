# Clean user environment: only the TeX Live packages a user would have.
# The pdfannex package itself is deliberately absent; scripts/e2e-ctan installs it.
FROM ubuntu:24.04
RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      latexmk poppler-utils unzip texlive-fonts-recommended texlive-latex-base \
      texlive-latex-extra texlive-luatex texlive-xetex \
 && rm -rf /var/lib/apt/lists/*
