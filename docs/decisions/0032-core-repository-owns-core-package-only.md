# 0032 Keep core packaging and QA in the core repository

- Context: the docstore resolver example has been extracted to `nocona71/pdfannex-docstore`, with its own CI, CTAN/TDS packaging, and release workflow. Keeping its implementation and artifacts in core workflows creates duplicate ownership and couples independent releases.
- Decision:
  1. The `pdfannex` repository owns and releases the core LaTeX package, CLI, and generic Resolver Protocol 1 contract.
  2. Core CI, CTAN/TDS artifacts, release uploads, and package-manager E2E tests cover only core components.
  3. Resolver examples and provider-specific tests, dependencies, and packages are maintained and released in their own repositories. The core project links to those repositories but does not vendor or build them.
  4. Keep historical decision records, but mark test/release decisions partly superseded where their adapter-specific steps moved to the standalone repository.
- Consequences: core and adapter releases can proceed independently. Protocol compatibility remains governed by the core specification; the standalone resolver repository tests against the core checkout.
