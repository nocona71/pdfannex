# 0001 Spec split by topic
- Context: one 52 KB spec was unwieldy and timed out LanguageTool (server ~3.5 s/KB).
- Decision: topic-cluster files `spec/01..15`, each about 8 KB or less, with `spec/index.md`. The monolithic `spec-0.1.md` was removed.
- Consequences: edit only the relevant topic file; keep files small.
