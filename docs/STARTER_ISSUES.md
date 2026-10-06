# Starter tasks

Create issues from these contracts after reviewing the foundation. Work through dependencies in order; do not start all tasks simultaneously.

1. **Versioned runtime schemas.** Validate labels, lengths, IDs, timestamps and evidence fields at ingress. Reject unknown labels and unexpected keys. Publish JSON Schemas; add valid/invalid round-trip tests. Dependency: foundation architecture review.
2. **AuditStore conformance and recovery.** Specify duplicate-ID, append, export, failure, and crash semantics; detect orphan preflight events. Test a second store without changing orchestration. Dependency: agreed audit schema.
3. **Verified public evidence fixture.** Commit a small licensed public excerpt with exact source/version, retrieval time and digest; distinguish trusted retrieval from caller claims. Reject missing or mismatched evidence. Dependency: evidence schema.
4. **Authenticated review contract.** Specify pending/approved/rejected/expired states, reviewer permissions and binding to immutable request context. Test replay and modified-request denial before implementing resume. Dependency: identity and threat model review.
5. **First live ModelProvider adapter.** Isolate SDK, validate response, record actual model ID and usage, redact failures, set timeouts and limits. Offline contract tests plus opt-in live smoke test. Dependency: provider schema and approved public-only boundary.
6. **Second-provider portability demo.** Implement a genuinely independent provider; same orchestration and same conformance suite. Document unsupported capabilities; no silent routing to a provider lacking permission. Dependency: first working vertical slice.

Later: guidance mapping evidence, security scans, SBOM, branch rules and a reproducible ten-minute demo. No issue should promise complete injection prevention or automatic government compliance.
