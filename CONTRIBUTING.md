# Contributing

Humans and coding agents follow these same rules. Start with the linked live issues in `docs/STARTER_ISSUES.md`; propose one small scope in the relevant issue before changing public contracts. Gate 1 is open for schema/threat-model proposals; formal approval is pending. You may prepare a focused draft PR and tests while review is pending, but do not merge contract changes without explicit maintainer review. Keep one focused PR per contract or invariant. Do not open overlapping rewrites of shared files.

Use `REPOSITORY_MAP.md` before choosing a path. Read the destination directory's README. Scaffold directories reserve ownership boundaries, not independent microservices. Move existing demo code during a reviewed implementation task; do not duplicate it across `src/` and `services/` or add dependencies for empty placeholders.

## Local checks

Use Python 3.12 or newer; CI explicitly selects Python 3.12. Tests use `PYTHONPATH=src` until packaging is agreed, rather than modifying imports inside the suite. No credentials or external model calls are required.

```bash
python3 -m compileall -q src tests
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m govai_nz.demo
git diff --check
```

The obsolete one-time `publish.sh` bootstrap has been removed. The repository already exists; submit changes on a branch through a pull request.

Before review, explain the resulting behaviour, test evidence, and remaining limitations. Add regression tests for changed enforcement, serialization, or adapter behaviour. Tests must assert observable invariants, especially that denied/review-required requests never reach providers. Do not test live services in default CI.

## Rules

- Use synthetic or public fixtures only. No credentials, personal records, classified information, or proprietary source code.
- Keep vendor-specific SDKs in adapters. No application-specific policy models in core.
- No raw prompts, responses, secrets, or provider exception messages in audit/logs by default.
- Treat retrieved text and model output as untrusted data, never as authorisation.
- Document implemented, partial, and planned controls accurately. Do not claim endorsement, accreditation, compliance, complete redaction, or complete injection prevention.
- Contract changes require updated architecture notes and tests; migrations must preserve old audit schema interpretation.
- AI assistance is welcome. The contributor must inspect the diff, run checks, verify sources, and take responsibility for the submission. Never auto-merge an agent's work.
- Contributions must be original or compatibly licensed. Identify third-party code and preserve required notices.

Maintainers review security-sensitive changes. A second independent reviewer should be added when available. CI success is necessary, not proof of security. Until repository rules are configured, review requirements are a documented process rather than an enforced GitHub gate.
