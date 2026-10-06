# Security model — foundation

Canonical security status is [SECURITY.md](../SECURITY.md). See [THREAT_MODEL.md](THREAT_MODEL.md).

Current controls rely on explicit demo labels. There is no trusted user identity, agency isolation, authoritative classification, real-model routing, or tool execution.

Implementation contracts must verify identity in `services/identity/`; evaluate permissions in `services/policy/`; enforce every provider/retrieval/tool boundary through services; and bind reviewer authority in `services/review/`. UI settings and model-generated text cannot grant permission.

Fail closed on invalid policies, unknown providers/tools, missing required evidence, unavailable audit writes and unauthorised review. Provider fallback requires a fresh permission check; an outage cannot permit an otherwise forbidden route. This is a target design requiring code and tests, not an implemented accreditation.
