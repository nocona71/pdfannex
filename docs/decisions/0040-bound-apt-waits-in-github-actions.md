# 0040 Bound APT waits in GitHub Actions

## Context

Ubuntu 24.04 hosted runners can stall while contacting the configured Azure
Ubuntu mirror. In run 37670202960, the CTAN submission job's `apt-get update`
did not complete before the 15-minute job timeout, even though an earlier
dependency-install job in the same run succeeded.

## Decision

Bound APT network waits in all GitHub Actions workflows that update or install
packages: allow one retry and set HTTP and HTTPS timeouts to 10 seconds.

## Consequences

An unavailable mirror fails over or reports an explicit package-install error
instead of consuming the full job timeout. If all configured mirrors are
unavailable, dependency installation still fails and the workflow does not
continue with missing tools.
