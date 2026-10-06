# Architecture

## Foundation flow

Request → policy decision → audit preflight → permitted provider → outcome audit → response.

Denied and review-required requests produce audit events without calling a provider. Provider failures produce a generic error event; exception messages are not persisted. If audit storage fails, no response is released. The preflight must succeed before any provider call.

The initial policy accepts only explicitly declared public material and blocks records labelled as containing personal information. An explicitly high-impact request needs review. This is a demonstration of ordering and enforcement, not a classifier.

## Boundaries

| Contract | Foundation implementation | Next implementation |
| --- | --- | --- |
| `ModelProvider` | Deterministic mock | One live provider, then an independent second provider |
| `PolicyEngine` | Public-only Python policy | Versioned rules, optional OPA adapter |
| `AuditStore` | SQLite insert and JSON export | Retention-aware durable storage adapter |
| Evidence reference | Caller-supplied, unverified metadata | Allowlisted public retrieval with snapshot verification |
| Human review | Stop with `review_required` | Authenticated reviewer, durable decision, bound request resume |

Provider adapters implement the contract; vendor SDKs stay inside adapters. The core must not depend on a particular model vendor or cloud. Use narrow separate capability contracts for future streaming, embeddings, retrieval, identity, and tools rather than forcing every provider to pretend to support every feature.

## Audit semantics

Events have UUIDs, UTC timestamps, a schema version, trace/request IDs, phase, decision reasons, input/output digests, application identity, evidence references, and the actual model identifier when a provider returns it. Input and output text are excluded. A preflight and an outcome are separate events; existing records are never updated through the public adapter API.

This is application-level append-only behaviour. A SQLite file owner can edit the database: this is **not immutable or tamper-proof storage**. Hashes do not anonymise low-entropy personal data. Model output and evidence remain untrusted. The demo does not prove factual accuracy or reproducibility of model output.

## Future vertical slice

Authenticate caller → validate/classify input → evaluate provider, retrieval and tool permissions → retrieve allowlisted evidence → record preflight → execute permitted provider → validate evidence references/output → obtain any required authenticated review before release → record outcome → release result.

Check each outbound boundary before transmission. Record metadata without copying sensitive payloads into logs. Audit failure is fail-closed for release; a provider call already made cannot be undone. Startup recovery must eventually identify preflight events without terminal outcomes.
