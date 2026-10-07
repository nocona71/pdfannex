# 0022 Cross-platform CLI resolver execution

- Context: the CLI's shell quoting, resolver discovery and script launch assumed POSIX. Windows needs the same Resolver Protocol without platform-specific resolver launchers.
- Decision:
  1. Normalize filesystem paths at the CLI boundary and retain portable `/` separators in stored and generated paths.
  2. Discover resolver scripts on `PATH` or in the TeX scripts tree, then invoke them explicitly through `texlua` using one process wrapper.
  3. Replace existing lock and map files with a platform-aware fallback when `os.rename` cannot replace a destination.
  4. Exercise the CLI's path and resolver process behavior in a Windows CI job with TeX Live.
- Consequences: Resolver Protocol 1 remains OS-neutral; resolver scripts need neither a POSIX shebang nor an executable bit.
