# Initial threat model

Assets: request contents, provider credentials (future), evidence integrity, review authority, and audit availability/integrity. Boundaries: caller → core, core → provider, core → audit store, future retriever → core, future reviewer → release.

| Threat | Current treatment | Gap |
| --- | --- | --- |
| Non-public input sent to provider | Block non-public or personally labelled request before execution | Labels are caller supplied; no detection or authoritative identity |
| Review bypass | Stop before execution | Authenticated reviewer and resume are absent |
| Unlogged execution | Require successful preflight insert | Crash recovery and reconciled terminal events are absent |
| Payload exposure in logs | Digests/metadata only; generic failure reason | Digests may disclose guessable content; metadata can still be sensitive |
| Altered audit history | Unique event IDs, insert-only application interface | DB owner can modify records; no tamper-resistant storage |
| Injection in evidence/model output | No live sources or live models | Requires adversarial tests and authority separation before live slice |
| Malicious contribution/dependency | Small PRs, owner review, dependency-free runtime, pinned checkout action | Repository protections, scanners, SBOM and broader assurance are planned |
| Malformed or extended contract payload | Versioned strict wire schemas and Python validation reject unsupported labels, fields, formats and oversized values | JSON Schema checks shape only; it does not authenticate callers, verify evidence, or authoritatively classify information |

The mock adapter is a test double, not a security boundary. Never infer production readiness from passing offline tests.
