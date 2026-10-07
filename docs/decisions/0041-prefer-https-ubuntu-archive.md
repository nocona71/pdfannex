# 0041 Prefer HTTPS Ubuntu archive on hosted runners

## Context

Decision 0040 bounded APT retries and per-request timeouts, but run 37675415799
still spent the full 10-minute `prepare-review` job timeout in `apt-get update`.
Its logs showed the hosted runner continuing to use
`http://azure.archive.ubuntu.com/ubuntu`, while requests to
`https://archive.ubuntu.com/ubuntu` were completing.

## Decision

Before package updates, replace the Azure Ubuntu archive URL in the runner's
APT mirror list with `https://archive.ubuntu.com/ubuntu`. Retain bounded
retries and HTTP/HTTPS timeouts as additional safeguards.

## Consequences

Package-installing workflows avoid the observed stalled mirror while still
failing explicitly if the Ubuntu archive itself is unavailable.
