# Starter tasks

These are live GitHub issues. Current gate: step 1, schemas and threat-model contracts open for proposals; formal architecture/schema approval is pending. Maintainer: @hemmingsenpeter-byte. Start by proposing one small scope in #1, or an audit-design scope in #2. Submit a focused draft PR; maintainer review is required before merging contract changes. No review response SLA is promised.

| Task | Live issue | Work available now |
| --- | --- | --- |
| Runtime schemas and threat model | [#1](https://github.com/hemmingsenpeter-byte/govai-nz/issues/1) | Scoped proposals and draft contract/test work |
| Audit conformance and recovery | [#2](https://github.com/hemmingsenpeter-byte/govai-nz/issues/2) | Design proposals; implementation waits on #1 |
| Verified evidence fixture | [#3](https://github.com/hemmingsenpeter-byte/govai-nz/issues/3) | Source/fixture proposals; implementation waits on #1 |
| Authenticated review | [#4](https://github.com/hemmingsenpeter-byte/govai-nz/issues/4) | Design proposals; implementation waits on contracts and identity review |
| First live provider | [#5](https://github.com/hemmingsenpeter-byte/govai-nz/issues/5) | Blocked on #1 and #3 approval |
| Second-provider portability | [#6](https://github.com/hemmingsenpeter-byte/govai-nz/issues/6) | Blocked on a reviewed working slice and #5 |

The `good first issue` label marks an entry point for a small proposal. It does not mean the entire task is beginner-sized or ready for implementation. Work through dependencies in order; do not start all tasks simultaneously.

1. **Versioned runtime schemas.** Basic field types and non-empty metadata are now checked. Add semantic validation for lengths, IDs, timestamps and evidence formats at ingress. Reject unknown labels and unexpected keys. Publish JSON Schemas; add valid/invalid round-trip tests. Dependency: foundation architecture review.
2. **AuditStore conformance and recovery.** Specify duplicate-ID, append, export, failure, and crash semantics; extend the current read-only orphan report into durable reconciliation without replaying provider calls. Test a second store without changing orchestration. Dependency: agreed audit schema.
3. **Verified public evidence fixture.** Commit a small licensed public excerpt with exact source/version, retrieval time and digest; distinguish trusted retrieval from caller claims. Reject missing or mismatched evidence. Dependency: evidence schema.
4. **Authenticated review contract.** Specify pending/approved/rejected/expired states, reviewer permissions and binding to immutable request context. Test replay and modified-request denial before implementing resume. Dependency: identity and threat model review.
5. **First live ModelProvider adapter.** Isolate SDK, validate response, record actual model ID and usage, redact failures, set timeouts and limits. Offline contract tests plus opt-in live smoke test. Dependency: provider schema and approved public-only boundary.
6. **Second-provider portability demo.** Implement a genuinely independent provider; same orchestration and same conformance suite. Document unsupported capabilities; no silent routing to a provider lacking permission. Dependency: first working vertical slice.

Later: guidance mapping evidence, security scans, SBOM, branch rules and a reproducible ten-minute demo. No issue should promise complete injection prevention or automatic government compliance.
