"""Small contracts and fail-closed orchestration, with no vendor SDKs."""

import hashlib
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Protocol
from uuid import uuid4


class Classification(str, Enum):
    PUBLIC = "public"
    NON_PUBLIC = "non_public"  # Demo label, not an NZ protective marking.


class Decision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class Evidence:
    source_uri: str
    version_id: str
    retrieved_at: str
    content_hash: str


@dataclass(frozen=True)
class Request:
    prompt: str
    classification: Classification
    contains_personal_information: bool = False
    high_impact: bool = False
    evidence: tuple[Evidence, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.prompt, str) or not self.prompt.strip():
            raise ValueError("A non-empty prompt is required")
        if not isinstance(self.classification, Classification):
            raise ValueError("An explicit supported classification is required")
        if type(self.contains_personal_information) is not bool or type(self.high_impact) is not bool:
            raise ValueError("Policy flags must be booleans")
        if not isinstance(self.evidence, tuple) or not all(isinstance(e, Evidence) for e in self.evidence):
            raise ValueError("Evidence must be an immutable tuple of references")


@dataclass(frozen=True)
class PolicyResult:
    decision: Decision
    reason: str
    policy_version: str


@dataclass(frozen=True)
class ModelResponse:
    text: str
    model_id: str


class ModelProvider(Protocol):
    @property
    def provider_id(self) -> str: ...

    def generate(self, request: Request) -> ModelResponse: ...


class PolicyEngine(Protocol):
    def evaluate(self, request: Request) -> PolicyResult: ...


@dataclass(frozen=True)
class AuditEvent:
    schema_version: str
    event_id: str
    request_id: str
    timestamp: str
    application: str
    application_version: str
    phase: str
    decision: str
    reason: str
    policy_version: str
    classification: str
    input_hash: str
    evidence: tuple[Evidence, ...]
    provider_id: str | None = None
    model_id: str | None = None
    output_hash: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


class AuditStore(Protocol):
    def append(self, event: AuditEvent) -> None: ...


@dataclass(frozen=True)
class Result:
    request_id: str
    status: str
    text: str | None = None


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class PublicOnlyPolicy:
    def evaluate(self, request: Request) -> PolicyResult:
        # Revalidate at ingress even if a caller bypassed normal construction.
        request.__post_init__()
        if request.classification is not Classification.PUBLIC or request.contains_personal_information:
            return PolicyResult(Decision.DENY, "public_only", "public-only/v1")
        if request.high_impact:
            return PolicyResult(Decision.REVIEW_REQUIRED, "human_review_needed", "public-only/v1")
        return PolicyResult(Decision.ALLOW, "declared_public", "public-only/v1")


class Gateway:
    def __init__(self, provider: ModelProvider, policy: PolicyEngine, audit: AuditStore) -> None:
        self.provider = provider
        self.policy = policy
        self.audit = audit

    def run(self, request: Request) -> Result:
        import json

        request.__post_init__()
        request_id = str(uuid4())  # Also the trace ID for this single-call foundation.
        decision = self.policy.evaluate(request)
        if not isinstance(decision.decision, Decision):
            raise ValueError("Invalid policy decision")
        input_hash = digest(json.dumps(asdict(request), sort_keys=True, separators=(",", ":")))

        def record(phase: str, reason: str, response: ModelResponse | None = None) -> None:
            self.audit.append(AuditEvent(
                schema_version="0.1", event_id=str(uuid4()), request_id=request_id,
                timestamp=datetime.now(timezone.utc).isoformat(), application="govai-nz-demo",
                application_version="0.0.1", phase=phase, decision=decision.decision.value,
                reason=reason, policy_version=decision.policy_version,
                classification=request.classification.value, input_hash=input_hash,
                evidence=request.evidence,
                provider_id=self.provider.provider_id if decision.decision is Decision.ALLOW else None,
                model_id=response.model_id if response else None,
                output_hash=digest(response.text) if response else None,
            ))

        if decision.decision is not Decision.ALLOW:
            record("stopped", decision.reason)
            return Result(request_id, decision.decision.value)
        record("preflight", decision.reason)  # Failure prevents outbound execution.
        try:
            response = self.provider.generate(request)
            if not isinstance(response, ModelResponse) or not isinstance(response.text, str) or not response.model_id:
                raise ValueError("Invalid provider response")
        except Exception:
            record("failed", "provider_error")  # Never store provider exception text.
            return Result(request_id, "provider_error")
        record("completed", "response_ready", response)  # Failure prevents release.
        return Result(request_id, "completed", response.text)
