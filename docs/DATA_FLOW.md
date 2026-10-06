# Data flow

**Current:** a local caller supplies a synthetic request and declared classification. The public-only policy evaluates it. Denied/review-required requests record a stop event. Allowed requests record a preflight, reach a mock provider, then record an outcome before returning synthetic text. SQLite receives metadata/digests and caller-supplied evidence references, not raw prompts/responses. The demo database is temporary and deleted on exit.

**Planned:** verified identity; classification/detection; provider permission and cost checks; approved retrieval with validated provenance; permitted tools; output checks; authenticated review where needed; record retention/export; release. Enforcement precedes each outbound boundary. Tool and retrieval results remain untrusted.

Before adding a boundary, document data transmitted, recipient, jurisdiction/deployment, authority, storage/retention, failure behaviour and evaluation evidence. `services/` folders do not require network boundaries or separate processes.
