# 0018 Track only intentional project files

- Context: package and documentation builds create PDFs, ZIP archives, TeX auxiliary files, caches, and logs. These outputs can appear beside source files and are easy to stage accidentally.
- Decision: version control contains only source, tests, documentation, and intentional fixtures. Ignore or clean generated and transient outputs. Before staging, inspect all changed and untracked files, and stage only task-relevant paths rather than adding the whole worktree.
- Consequences: generated outputs needed for a release are reproducibly built by project targets but are not committed unless they are intentionally maintained source assets.
