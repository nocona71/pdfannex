# 0024 Use native Windows paths for atomic replacement

- Context: Windows CI still failed when the CLI replaced an existing lock file. The PowerShell error showed fully qualified paths formatted with forward slashes passed to `.NET`'s `File.Replace`.
- Decision: convert the absolute paths used by the Windows replacement fallback to backslash-separated Windows paths before passing them to PowerShell.
- Consequences: paths used by the Windows-only fallback match the native path format; path normalization elsewhere remains platform-independent.
