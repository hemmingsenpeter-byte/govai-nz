# Audit model

Current Python contract: `src/govai_nz/core.py::AuditEvent`; wire schema: `src/govai_nz/contracts.v1.schema.json` (`$defs.auditEvent`). Bundle version `v1` is distinct from the audit event schema version `0.1` and application version `0.0.1`; existing `0.1` event interpretation is retained. The request ID is also the trace ID for the single-call foundation. Events record a UUIDv4, UTC timestamp, phase, decision/reason, policy version, classification, input digest, evidence references and provider/model/output digest when available. Object deserialization rejects unknown fields and unsupported versions.

The schema limits evidence lists to 32, identifiers to 256 characters, provider IDs and reasons to 128 characters, and digests to lowercase SHA-256 hex. The timestamp rule is RFC 3339 UTC (`Z` or `+00:00`, up to six fractional digits). These rules validate wire shape, not whether evidence or a caller-supplied classification is truthful.

Denied/review-required → `stopped`. Allowed → `preflight` → `completed` or `failed`. Audit preflight must succeed before a provider call; terminal audit must succeed before output release. There is no current recovery process for an orphaned preflight.

SQLite's insert-only application API is not immutable or tamper-resistant storage. Metadata-only events do not necessarily satisfy public-record obligations. Retention, access, required payload storage, event signatures/linking and recovery are separate contracts to design in `services/audit/` with records specialists. Do not silently add raw payloads to solve a records gap.
