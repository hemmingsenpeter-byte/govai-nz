# Security

This is an offline foundation demonstrator. Do not process real personal, sensitive, or classified information, expose it as a public service, or treat its results as advice for decisions about people.

Implemented: declared public-only enforcement; stop before execution for denied/review-required input; audit preflight before execution; audit failure prevents release; generic provider failure recording; no raw payload logging.

Missing: authentication, authoritative classification, PII/secret detection, prompt-injection defence, live evidence verification, output factuality checking, reviewer authentication, resume authorisation, retention policy, tamper-resistant storage, and deployment accreditation.

Report vulnerabilities privately through GitHub's **Report a vulnerability** feature if the maintainer has enabled it. If unavailable, ask the maintainer for a private reporting channel without publishing exploit details, credentials, or affected data in an issue. A formal response SLA is not yet established.

Read `docs/THREAT_MODEL.md`. Security and disclosure processes will evolve before live providers or deployments are added.
