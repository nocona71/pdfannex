# 0029 Install TDS artifacts in a native user tree

- Context: the temporary TeX Live package-manager tests do not provide a convenient way to install a built TDS artifact persistently for manual host testing, nor a safe uninstall path.
- Decision: ship `install-texmfhome-tds.sh` beside both core and docstore TDS ZIPs in their Actions artifacts. The script defaults to `TEXMFHOME`, supports install and uninstall, refuses to overwrite existing files, records paths it installed, and refreshes the TeX filename database. It does not use `sudo` or register files with `tlmgr`.
- Consequences: users can install either artifact independently and remove exactly the files installed by that artifact. Automated tests cover collision refusal, path traversal, symlink rejection, and preservation of unrelated user files.
