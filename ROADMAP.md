# Roadmap

This repository is a foundation, not the completed v0.1. Current gate: step 1, open for scoped schema/threat-model proposals in issue #1. Formal architecture/schema approval is pending; maintainer @hemmingsenpeter-byte records gate approval before later implementation proceeds.

1. **Contracts and threat model.** Agree versioned request, decision, evidence, review, and audit schemas. Add strict runtime validation and serialization contracts. Define information-label semantics without pretending demo labels implement NZ protective markings.
2. **Audit and recovery.** Add crash recovery, retention/export rules, event linkage verification, access boundaries, and adapter conformance tests. Document what metadata can be safely retained.
3. **Identity and review.** Authenticate principals; bind review to exact request, evidence, provider, policy version, and expiry. Test bypass, replay, modification, and reviewer permissions before enabling resume.
4. **One public-document vertical slice.** Add an allowlisted, versioned public source fixture/retriever with verified digests. Implement one live model adapter and output/evidence checks. Keep default CI offline.
5. **Portability.** Add a second provider adapter, then a local option. Run the same application request through each and record actual resolved model identity and usage. Provider capability differences must be explicit.
6. **Assurance and demonstration.** Add adversarial evaluations, dependency/secret scanning, pinned dependencies/actions, SBOM and guidance control evidence. Configure repository rules and private reporting. Demonstrate allowed, blocked, review-required, missing-evidence, unavailable-provider, and changed-model cases with accurate limits.

Finish and review each gate before expanding. HTTP/FastAPI, Pydantic validation, OPA, PostgreSQL, cloud deployment and a small demonstration UI are possible implementations, not prerequisites for the initial offline contracts. The existing README-only provider and cloud directories are placement guides requested for contributors, not executable stubs. Keep them as documentation; do not implement multiple provider adapters or cloud deployments before one working slice.
