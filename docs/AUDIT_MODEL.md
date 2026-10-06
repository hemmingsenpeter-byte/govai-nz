# Audit model

Current schema: `src/govai_nz/core.py::AuditEvent`. Schema version `0.1` is distinct from application version `0.0.1`. The request ID is also the trace ID for the single-call foundation. Events record a UUID, UTC timestamp, phase, decision/reason, policy version, classification, input digest, evidence references and provider/model/output digest when available.

Denied/review-required → `stopped`. Allowed → `preflight` → `completed` or `failed`. Audit preflight must succeed before a provider call; terminal audit must succeed before output release. There is no current recovery process for an orphaned preflight.

SQLite's insert-only application API is not immutable or tamper-resistant storage. Metadata-only events do not necessarily satisfy public-record obligations. Retention, access, required payload storage, event signatures/linking and recovery are separate contracts to design in `services/audit/` with records specialists. Do not silently add raw payloads to solve a records gap.
