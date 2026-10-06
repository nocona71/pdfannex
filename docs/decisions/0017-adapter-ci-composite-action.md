# 0017 Keep adapter CI separable

- Context: `adapter-example/` is currently a subdirectory of the pdfannex repository but is intended to become a standalone package/repository. GitHub only activates workflows from the repository-root `.github/workflows`; nested workflow files are ignored.
- Decision:
  1. Keep the adapter test action and future workflow template inside `adapter-example/.github/`.
  2. Implement test execution as a composite action, which the current root workflow can invoke by path. The action runs `make test` and accepts a `pdfannex-home` input for the source checkout used by integration tests.
  3. Have root CI skip the adapter tests inside `scripts/check` and invoke the composite action instead. Plain local `make check` continues to run all tests by default.
  4. Keep a workflow template at `adapter-example/.github/workflows/ci.yml`. It is inactive while nested; after extraction it becomes the standalone repository workflow and invokes the local composite action.
- Consequences: the adapter test command is defined once and exercised by current CI; after extraction, the action and workflow move with the adapter. The future repository workflow still needs to install the documented test tools and check out the pdfannex source for integration tests.
