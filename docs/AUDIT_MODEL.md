# Audit model

Current schema: `src/govai_nz/core.py::AuditEvent`. Schema version `0.2` is distinct from application version `0.0.1`. The request ID is also the trace ID for the single-call foundation. Events record a UUID, UTC timestamp, phase, decision/reason, policy version, classification, input digest, evidence references and provider/model/output digest when available.

Denied/review-required → `stopped`. Allowed → `preflight` → `completed` or `failed`. Audit preflight must succeed before a provider call; terminal audit must succeed before output release. `SQLiteAuditStore.orphaned_preflights()` reports preflights without a terminal event. It does not retry execution, infer provider success, or repair records. A terminal write failure still propagates and prevents release; the failed store cannot be relied on to record its own failure. Crash recovery and reconciliation remain roadmap work.

Schema `0.2` adds early `failed` events with reason `input_error` or `policy_error`. These contain null decision, policy version, classification and input hash, and empty evidence; unvalidated metadata and exception text are never retained. Gateway ingress, hashing, policy exceptions and invalid policy results use this path. Construction errors raised before `Gateway.run` are outside its audit boundary. Audit failure itself can leave no event and propagates.

`decision` describes the policy authorisation, not execution success: provider `failed` events retain `decision="allow"`. Early failures have no trustworthy policy decision. Existing `0.1` records retain their original interpretation; exporters must inspect schema versions rather than reinterpret old events.

SQLite's insert-only application API is not immutable or tamper-resistant storage. Metadata-only events do not necessarily satisfy public-record obligations. Retention, access, required payload storage, event signatures/linking and recovery are separate contracts to design in `services/audit/` with records specialists. Do not silently add raw payloads to solve a records gap.
