# Contributing

Humans and coding agents follow these same rules. Start with one task in `docs/STARTER_ISSUES.md`; agree scope in an issue before changing public contracts. Keep one focused PR per contract or invariant. Do not open overlapping rewrites of shared files.

## Local checks

Use Python 3.12 or newer. No credentials or external model calls are required.

```bash
python -m compileall -q src tests
python -m unittest discover -s tests -v
PYTHONPATH=src python -m govai_nz.demo
git diff --check
```

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
