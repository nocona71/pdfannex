# 0042 Use the CTAN form for initial package submission

## Context

The Ubuntu 24.04 runner's packaged `l3build` does not correctly handle a
first-time upload when the package is absent from CTAN. Run 37683896923
reported success, but its log shows `form-string` fields being executed as
shell commands. Upstream tracked this as
[latex3/l3build#468](https://github.com/latex3/l3build/issues/468) and fixed it
in [latex3/l3build#469](https://github.com/latex3/l3build/pull/469), after the
version packaged by Ubuntu.

## Decision

Submit the initial package through CTAN's web upload form. Use `l3build upload`
only after the package page is publicly listed. The submission workflow checks
for that listing and fails explicitly before invoking `l3build` if it is
absent.

## Consequences

The workflow still builds, tests, and previews the exact archive for the
initial submission; the operator uploads its artifacts through CTAN's form.
Subsequent updates use the automated submission path after CTAN publishes the
package page.
