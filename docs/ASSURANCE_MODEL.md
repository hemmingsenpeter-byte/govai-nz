# Assurance model — foundation

Current evidence: offline tests for deny/review boundaries, successful model identity recording, payload exclusion, provider failure and audit-write failure. They establish narrow engineering invariants, not comprehensive AI safety or factuality.

Put deterministic software tests in `tests/`; behavioural and adversarial scenario definitions/scoring in `evaluations/`. Evaluation results must name commit, fixture/source versions, provider/model, policy version, scoring procedure, expected outcome, observed outcome and limitations. Default CI stays offline; paid/live runs require explicit opt-in.

Before a demonstration release: complete source mappings, adapter contract tests, authorisation tests, provenance checks, adversarial evaluations, pinned dependency/action review, secret/dependency scans and release evidence. Record missing capabilities as gaps. A maintainer review and eventual independent review remain necessary.
