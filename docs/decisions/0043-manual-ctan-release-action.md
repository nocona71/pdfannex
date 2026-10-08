# 0043 Make CTAN submission a manual release action

## Context

Publishing a GitHub Release currently triggers CTAN upload automation. The
initial CTAN listing must instead be submitted through CTAN's web form, and
future uploads should be an intentional release operation rather than a side
effect of publishing a GitHub Release.

## Decision

Make the CTAN workflow `workflow_dispatch`-only and remove its invocation from
the Release Please workflow. Manual runs may build and review the release
artifacts without submitting. Require an explicit **Submit to CTAN** selection
before starting the protected `l3build upload` job; keep the existing approval
and receipt-check safeguards for uploads.

## Consequences

GitHub Releases no longer initiate CTAN uploads. The initial package can be
prepared in Actions and submitted through CTAN's web form, while later updates
are manually dispatched and approved. This supersedes decision 0037.
