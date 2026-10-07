# 0021 Use the host Docker daemon from the devcontainer

- Context: the end-to-end workflow uses disposable Docker containers, but the devcontainer did not provide a Docker CLI or access to a Docker daemon, preventing local execution of the same container-based checks.
- Decision: add the official Docker-outside-of-Docker devcontainer feature. It installs Docker tooling in the devcontainer and connects it to the host daemon; do not run a privileged nested daemon.
- Consequences: running Docker from the devcontainer requires an available host Docker daemon and grants the devcontainer broad control over it, effectively host-level privileges. CI continues to use separate fresh containers and does not depend on developer Docker access.
