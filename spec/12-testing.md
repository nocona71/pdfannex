# Testing Infrastructure

Use `l3build` for the LaTeX package.

CLI and resolver protocol tests may use separate tooling if appropriate.

---

# Required PDF Fixtures

Provide small deterministic fixtures:

```text
a4-one-page.pdf
a5-one-page.pdf
letter-one-page.pdf
legal-one-page.pdf
landscape.pdf
multipage.pdf
mixed-pagesize.pdf
edge-content.pdf
```

---

# Required Geometry Tests

Test:

```text
A4 → A4
A5 → A4
Letter → A4
Legal → A4
landscape source
mixed-size source
```

Verify:

- aspect ratio preserved;
- no unintended crop;
- no non-uniform stretching;
- footer reservation;
- frame placement;
- document pagination.

---

# Required Multi-Pass Tests

Verify:

- `.loa` written correctly;
- List of Annexes resolves;
- page changes propagate;
- annex reordering changes annex numbers;
- labels remain stable;
- hyperlink targets remain unique;
- `latexmk` converges normally.

---

# `scrlttr2` Regression

Test annex insertion after:

```latex
\begin{letter}{...}
...
\end{letter}
```

Verify:

- no annex-induced duplicate destination warning;
- `pagination=continue`;
- correct first annex page;
- correct List-of-Annexes page;
- footer-safe layout.

---

# External-Source Tests

When companion tooling is included, test:

```text
unresolved request discovery
resolver selection
missing resolver
describe success
protocol incompatibility
resolve success
resource-not-found
authentication failure
batch resolution
deduplication
partial batch failure
invalid resolver output
artifact missing
non-PDF artifact
locked rebuild → zero resolver calls
exact recovery
hash mismatch
transactional rollback
resolution-map regeneration
```

No test should depend on how a resolver internally obtains its result.

---
