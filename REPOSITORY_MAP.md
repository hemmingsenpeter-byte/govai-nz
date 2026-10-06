# Where to put files

Start here before creating a file. This is the canonical placement guide. A directory marked **planned** is a contribution boundary, not a working service.

## Placement table

| What you are writing | Destination | Boundary |
| --- | --- | --- |
| Shared Python contracts, types, serialization helpers | `src/govai_nz/` | No vendor SDKs, HTTP handlers, UI or domain calculations |
| Gateway API handlers, routing and request orchestration | `services/gateway/` | Enforce controls before outbound calls; consume shared contracts |
| Document ingestion, search and provenance | `services/retrieval/` | Approved public sources only for reference fixtures |
| Policy evaluation and information controls | `services/policy/` | Interpret declarative rules; fail closed on invalid configuration |
| Audit persistence, export and records handling | `services/audit/` | No raw payload logging by default |
| Tool registry, permission checks and dispatch | `services/tools/` | Generic execution boundary, not tool implementations |
| Identity verification and authorisation | `services/identity/` | Identity is trusted only after verification |
| Human-review state and authorised resume | `services/review/` | Bind approvals to the exact request context |
| Model/vendor SDK integration | `providers/<provider>/` | Provider-neutral contracts; no SDK imports in gateway/core |
| Approved legislation/statistics/search tool implementation | `tools/<domain>/` | Tool definitions and versions; enforcement stays in services/tools |
| Generic deterministic demo tool | `tools/calculations/` | Synthetic arithmetic only; no tax/welfare/eligibility model in core |
| Copilot UI | `apps/copilot/` | Call GovAI API, never provider APIs directly |
| Admin UI | `apps/admin/` | Do not grant authority based on UI state |
| Classification/provider/review/tool/cost configuration | `policies/` | Example files are not automatically enforced |
| Behavioural/adversarial AI evaluation cases | `evaluations/<category>/` | Expected outcome, scoring, source/fixture and reproducible procedure |
| Unit/contract/integration/end-to-end test code | `tests/<category>/` | Default checks run offline; live tests are explicitly opt-in |
| Synthetic/public test inputs | `tests/fixtures/` | Provenance and licence for public material; no real personal data |
| Public-source manifests and synthetic demo datasets | `data/public/`, `data/synthetic/` | No nationwide data archive; generated caches stay untracked |
| Local/Azure/AWS deployment code | `infrastructure/<target>/` | No credentials or tenant-specific secrets |
| Assurance/privacy/review/records/system/deployment documents | `docs/` | Distinguish implemented, partial and planned controls |
| NZ guidance mapping and implementation evidence | `controls/` | Exact source provision, implementation, test and residual gap |
| Architecture decisions | `docs/decisions/` | Numbered ADR with context, decision and consequences |
| Model and provider inventory/risk records | `docs/registers/` | Record real configured instances; no invented approvals |
| End-to-end example applications/workflows | `examples/` | Small synthetic/public demonstration using approved interfaces |
| Developer scripts | `scripts/` | Idempotent when possible, no hidden external mutations |
| CI workflows, issue forms, PR templates, owners | `.github/` | Minimal permissions and maintainable checks |

## Current foundation

The working offline demo currently lives in `src/govai_nz/core.py`, `adapters.py`, and `demo.py`, with tests in `tests/test_gateway.py`. It remains unchanged while the module contracts are agreed. When implementing the first service/adapter, **move** its demo implementation to its canonical area and update imports and tests in the same PR. Do not copy it and create two implementations. Until that migration, run the commands in `CONTRIBUTING.md`.

Top-level `services/`, `providers/`, and `tools/` are ownership boundaries; they do not imply separate deployed microservices. Start with one application and one process. Do not add Dockerfiles, npm projects, SDK dependencies, or cloud modules just to fill directories.

## Dependency direction

Apps → service interfaces. Services → shared contracts and injected adapters. Provider/storage/tool adapters → shared contracts. Shared contracts do not import apps, service implementations, vendor SDKs or cloud infrastructure. Policies are configuration; tool implementations cannot authorise their own calls. Keep runtime code out of `evaluations/` and fixtures out of runtime source directories.

## Canonical documents

Root `ARCHITECTURE.md`, `SECURITY.md`, `CONTRIBUTING.md`, `GOVERNANCE.md` and `ROADMAP.md` remain authoritative. `docs/README.md` links to them and indexes detailed documents. Do not create competing copies named `docs/ARCHITECTURE.md` or `docs/SECURITY.md`.

## File naming

- Python modules: `snake_case.py`; tests: `test_<behaviour>.py`.
- Human-readable documents: descriptive Markdown names; decisions: `NNNN-short-title.md`.
- Fixtures: stable descriptive filenames; manifests record source/version/hash/licence.
- Each new module directory begins with a README describing purpose, inputs/outputs, owner boundary, status and tests.
- Generated outputs go in ignored `var/`; examples contain reproducible inputs and instructions, not unreviewed generated results.

Read `CONTRIBUTING.md` and agree one scoped issue before implementation. The folder framework does not supersede the gated build order in `ROADMAP.md`.
