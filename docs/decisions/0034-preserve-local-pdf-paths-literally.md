# 0034 Preserve local PDF paths literally

- Context: the core package consumes local filenames as LaTeX arguments, while percent sequences and option-looking strings can also occur in filenames. URI decoding or CLI-style interpretation would change valid local paths and add unnecessary bootstrap behavior.
- Decision:
  1. Apply normal LaTeX escaping to TeX-special characters in `\includeannex` file arguments.
  2. After TeX expansion, pass the resulting local path literally to `pdfpages`; do not URL-decode it or interpret punctuation as options.
  3. Guarantee a tested minimum of spaces, Unicode, nested directories, `%`, `&`, `#`, `_`, `?`, `=`, leading hyphens, and literal percent sequences across pdfLaTeX, XeLaTeX, and LuaLaTeX.
- Consequences: local inclusion remains independent of the CLI and resolver layer. Other TeX-active characters and non-default catcodes are not promised by this decision; CLI and adapter path handling are tested separately.
