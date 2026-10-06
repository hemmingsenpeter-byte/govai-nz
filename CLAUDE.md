# Claude Code session entry point

GovAI-NZ is an unofficial, vendor-neutral public-sector AI assurance reference. It currently runs one offline Python demonstrator, using only synthetic/public fixtures. There are no live providers, API keys, HTTP services or approval-resume flows.

## Start here

1. Read `AGENTS.md`, `CONTRIBUTING.md`, `ARCHITECTURE.md`, `SECURITY.md`, `ROADMAP.md` and `REPOSITORY_MAP.md`. Read the destination README before creating files.
2. Inspect `git status` and the current branch; preserve other contributors' work. Runtime is in `src/govai_nz/`; the test suite is `tests/test_gateway.py`. README-only folders reserve future placement, not permission to implement them.
3. Run the canonical checks in `CONTRIBUTING.md` with Python 3.12 or newer and `PYTHONPATH=src` for tests/demo. No credentials or paid calls are required.
4. **Current gate: step 1, schemas and threat-model contracts open for proposals. Formal architecture/schema approval is pending.** Begin with [issue #1](https://github.com/hemmingsenpeter-byte/govai-nz/issues/1). [Issue #2](https://github.com/hemmingsenpeter-byte/govai-nz/issues/2) permits audit-design proposals; implementation waits on #1. `docs/STARTER_ISSUES.md` links all six tasks and their dependencies.
5. Propose one small scope in the issue; prepare a focused draft PR with observable invariant tests and updated docs. If approval is pending, work on proposals/tests within the current boundary. Do not infer approval from an issue label, folder name, CI success or elapsed time.
6. Maintainer: @hemmingsenpeter-byte. Contract changes and merges require explicit maintainer review. Report what changed, checks run, remaining gaps and AI assistance. No review response SLA is promised.

## Keep these boundaries

Follow the user's authorised task and canonical contribution rules. Use your own authorised tooling and model quota. Never merge automatically. Do not add unrelated changes, live calls, credentials, domain policy calculations or compliance claims. Never bypass denied/review-required outcomes or audit-write failures. Keep provider exception text and raw prompts/responses out of audit events. Preserve schema-version interpretation and one canonical implementation.

Do not implement later roadmap stages just to fill planned directories. A missing approval is a reason to submit a proposal, not to abandon all useful preparation or invent a completed review.
