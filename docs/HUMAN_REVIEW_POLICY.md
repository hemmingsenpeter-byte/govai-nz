# Human review policy

Current demo: `high_impact=True` causes `review_required`, a stop event, no provider call and no result text. There is no approval API or bypass switch.

Planned workflow in `services/review/`: authenticated reviewer identity, permissions, pending/approved/rejected/expired states, a review event distinct from model events, and approval bound to request/evidence digests, policy version, provider/model selection, tool permissions and expiry. Any material change requires re-evaluation and potentially new approval.

Before implementing resume, test unauthorised reviewer, self-approval where disallowed, replay, expiry, modified input/evidence, revoked permissions and missing audit records. Agencies determine applicable review responsibilities; this demo does not decide them.
