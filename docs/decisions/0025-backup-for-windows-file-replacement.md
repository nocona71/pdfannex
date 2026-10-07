# 0025 Use a temporary backup for Windows file replacement

- Context: Windows CI confirmed that both absolute replacement paths exist, but `.NET`'s `File.Replace` still rejects the call when its backup-path argument is `$null`.
- Decision: give `File.Replace` a unique backup path beside the destination, then delete the backup after replacement succeeds.
- Consequences: replacement remains atomic while avoiding the failing null-backup call; a failed backup cleanup is reported instead of silently ignored.
