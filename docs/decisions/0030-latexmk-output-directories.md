# 0030 Support `latexmk` output directories

- Context: when `latexmk` directs TeX output to a directory such as `build/`, the package writes its request file there, while the lock and resolution map remain in the project directory. The integration previously looked only beside the project source and skipped preparation.
- Decision: before preparing sources, the `latexmk` helper copies the request file from the configured output directory to the project directory, then runs the CLI there.
- Consequences: first-build source resolution works with output-directory configurations without moving project state or changing CLI behavior. Package tests cover both default and configured output directories.
