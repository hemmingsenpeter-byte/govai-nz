# Privacy model — foundation

Only synthetic or explicitly public input is allowed. The demo blocks requests declared to contain personal information; it does not detect it. Source metadata and hashes may still expose information, and digests do not anonymise guessable data.

No raw prompts, responses or provider exception details are stored in audit events. The reference implementation does not currently implement retention schedules, access controls, erasure, a Privacy Impact Assessment, or public-record capture obligations.

Before live adapters, identify each collected field, purpose, disclosure destination, retention, permitted logging, access and deletion controls. Add synthetic leakage fixtures to `evaluations/pii_leakage/` and code assertions to `tests/security/`. Keep real agency records out of this repository and issue tracker.
