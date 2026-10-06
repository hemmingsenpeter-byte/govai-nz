"""Small contracts and fail-closed orchestration, with no vendor SDKs."""

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Protocol
from urllib.parse import urlsplit
from uuid import UUID, uuid4


MAX_PROMPT_LENGTH = 32_000
MAX_RESPONSE_LENGTH = 1_000_000
MAX_EVIDENCE_ITEMS = 32
MAX_URI_LENGTH = 2_048
MAX_IDENTIFIER_LENGTH = 256
SHA256_LENGTH = 64

_TOKEN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/@+-]*$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_UTC_TIMESTAMP = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|\+00:00)$"
)


def _mapping(value: object, required: set[str], optional: set[str], name: str) -> dict:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object")
    keys = set(value)
    if keys - required - optional or required - keys:
        raise ValueError(f"{name} has missing or unexpected fields")
    return value


def _text(value: object, name: str, minimum: int, maximum: int) -> str:
    if not isinstance(value, str) or not minimum <= len(value) <= maximum:
        raise ValueError(f"{name} must be a string of length {minimum}..{maximum}")
    return value


def _token(value: object, name: str, maximum: int = MAX_IDENTIFIER_LENGTH) -> str:
    text = _text(value, name, 1, maximum)
    if not _TOKEN.fullmatch(text):
        raise ValueError(f"{name} has an invalid format")
    return text


def _hash(value: object, name: str) -> str:
    text = _text(value, name, SHA256_LENGTH, SHA256_LENGTH)
    if not _SHA256.fullmatch(text):
        raise ValueError(f"{name} must be a lowercase SHA-256 digest")
    return text


def _uuid4(value: object, name: str) -> str:
    text = _text(value, name, 36, 36)
    try:
        parsed = UUID(text)
    except ValueError as error:
        raise ValueError(f"{name} must be a UUIDv4") from error
    if parsed.version != 4 or str(parsed) != text:
        raise ValueError(f"{name} must be a canonical lowercase UUIDv4")
    return text


def _utc_timestamp(value: object, name: str) -> str:
    text = _text(value, name, 20, 32)
    if not _UTC_TIMESTAMP.fullmatch(text):
        raise ValueError(f"{name} must be an RFC 3339 UTC timestamp")
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(f"{name} must be an RFC 3339 UTC timestamp") from error
    if parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise ValueError(f"{name} must be UTC")
    return text


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

    def __post_init__(self) -> None:
        source_uri = _text(self.source_uri, "source_uri", 1, MAX_URI_LENGTH)
        try:
            parsed_uri = urlsplit(source_uri)
            if (
                parsed_uri.scheme not in {"http", "https"}
                or not parsed_uri.hostname
                or "@" in parsed_uri.netloc
                or not source_uri.isascii()
                or any(character.isspace() or ord(character) < 0x20 for character in source_uri)
                or re.search(r'[<>"{}|\\^`]', source_uri)
                or re.search(r"%(?![0-9A-Fa-f]{2})", source_uri)
            ):
                raise ValueError
            parsed_uri.port
        except ValueError as error:
            raise ValueError("source_uri must be an absolute HTTP(S) URI without credentials") from error
        _token(self.version_id, "version_id")
        _utc_timestamp(self.retrieved_at, "retrieved_at")
        _hash(self.content_hash, "content_hash")

    def to_dict(self) -> dict:
        self.__post_init__()
        return {
            "source_uri": self.source_uri,
            "version_id": self.version_id,
            "retrieved_at": self.retrieved_at,
            "content_hash": self.content_hash,
        }

    @classmethod
    def from_dict(cls, value: object) -> "Evidence":
        fields = _mapping(value, {"source_uri", "version_id", "retrieved_at", "content_hash"}, set(), "Evidence")
        return cls(**fields)


@dataclass(frozen=True)
class Request:
    prompt: str
    classification: Classification
    contains_personal_information: bool = False
    high_impact: bool = False
    evidence: tuple[Evidence, ...] = ()

    def __post_init__(self) -> None:
        _text(self.prompt, "prompt", 1, MAX_PROMPT_LENGTH)
        if not self.prompt.strip():
            raise ValueError("prompt must not contain only whitespace")
        if not isinstance(self.classification, Classification):
            raise ValueError("An explicit supported classification is required")
        if type(self.contains_personal_information) is not bool or type(self.high_impact) is not bool:
            raise ValueError("Policy flags must be booleans")
        if (
            not isinstance(self.evidence, tuple)
            or len(self.evidence) > MAX_EVIDENCE_ITEMS
            or not all(isinstance(item, Evidence) for item in self.evidence)
        ):
            raise ValueError(f"Evidence must be an immutable tuple of at most {MAX_EVIDENCE_ITEMS} references")
        for item in self.evidence:
            item.__post_init__()

    def to_dict(self) -> dict:
        self.__post_init__()
        return {
            "prompt": self.prompt,
            "classification": self.classification.value,
            "contains_personal_information": self.contains_personal_information,
            "high_impact": self.high_impact,
            "evidence": [item.to_dict() for item in self.evidence],
        }

    @classmethod
    def from_dict(cls, value: object) -> "Request":
        fields = _mapping(
            value,
            {"prompt", "classification"},
            {"contains_personal_information", "high_impact", "evidence"},
            "Request",
        )
        data = dict(fields)
        try:
            data["classification"] = Classification(data["classification"])
        except (TypeError, ValueError) as error:
            raise ValueError("An explicit supported classification is required") from error
        if "evidence" in data:
            if not isinstance(data["evidence"], list):
                raise ValueError("evidence must be an array")
            data["evidence"] = tuple(Evidence.from_dict(item) for item in data["evidence"])
        return cls(**data)


@dataclass(frozen=True)
class PolicyResult:
    decision: Decision
    reason: str
    policy_version: str

    def __post_init__(self) -> None:
        if not isinstance(self.decision, Decision):
            raise ValueError("decision must be a supported policy decision")
        _token(self.reason, "reason", 128)
        _token(self.policy_version, "policy_version")

    def to_dict(self) -> dict:
        self.__post_init__()
        return {
            "decision": self.decision.value,
            "reason": self.reason,
            "policy_version": self.policy_version,
        }

    @classmethod
    def from_dict(cls, value: object) -> "PolicyResult":
        fields = _mapping(value, {"decision", "reason", "policy_version"}, set(), "PolicyResult")
        data = dict(fields)
        try:
            data["decision"] = Decision(data["decision"])
        except (TypeError, ValueError) as error:
            raise ValueError("decision must be a supported policy decision") from error
        return cls(**data)


@dataclass(frozen=True)
class ModelResponse:
    text: str
    model_id: str

    def __post_init__(self) -> None:
        _text(self.text, "text", 1, MAX_RESPONSE_LENGTH)
        _token(self.model_id, "model_id")

    def to_dict(self) -> dict:
        self.__post_init__()
        return {"text": self.text, "model_id": self.model_id}

    @classmethod
    def from_dict(cls, value: object) -> "ModelResponse":
        fields = _mapping(value, {"text", "model_id"}, set(), "ModelResponse")
        return cls(**fields)


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

    def __post_init__(self) -> None:
        if self.schema_version != "0.1":
            raise ValueError("Unsupported audit schema_version")
        _uuid4(self.event_id, "event_id")
        _uuid4(self.request_id, "request_id")
        _utc_timestamp(self.timestamp, "timestamp")
        _token(self.application, "application")
        _token(self.application_version, "application_version")
        if not isinstance(self.phase, str) or self.phase not in {"stopped", "preflight", "completed", "failed"}:
            raise ValueError("phase must be a supported audit phase")
        if not isinstance(self.decision, str) or self.decision not in {item.value for item in Decision}:
            raise ValueError("decision must be a supported policy decision")
        _token(self.reason, "reason", 128)
        _token(self.policy_version, "policy_version")
        if not isinstance(self.classification, str) or self.classification not in {item.value for item in Classification}:
            raise ValueError("classification must be a supported label")
        _hash(self.input_hash, "input_hash")
        if (
            not isinstance(self.evidence, tuple)
            or len(self.evidence) > MAX_EVIDENCE_ITEMS
            or not all(isinstance(item, Evidence) for item in self.evidence)
        ):
            raise ValueError(f"Evidence must be an immutable tuple of at most {MAX_EVIDENCE_ITEMS} references")
        for item in self.evidence:
            item.__post_init__()
        if self.provider_id is not None:
            _token(self.provider_id, "provider_id", 128)
        if self.model_id is not None:
            _token(self.model_id, "model_id")
        if self.output_hash is not None:
            _hash(self.output_hash, "output_hash")

    def to_dict(self) -> dict:
        self.__post_init__()
        return {
            "schema_version": self.schema_version,
            "event_id": self.event_id,
            "request_id": self.request_id,
            "timestamp": self.timestamp,
            "application": self.application,
            "application_version": self.application_version,
            "phase": self.phase,
            "decision": self.decision,
            "reason": self.reason,
            "policy_version": self.policy_version,
            "classification": self.classification,
            "input_hash": self.input_hash,
            "evidence": [item.to_dict() for item in self.evidence],
            "provider_id": self.provider_id,
            "model_id": self.model_id,
            "output_hash": self.output_hash,
        }

    @classmethod
    def from_dict(cls, value: object) -> "AuditEvent":
        required = {
            "schema_version", "event_id", "request_id", "timestamp", "application",
            "application_version", "phase", "decision", "reason", "policy_version",
            "classification", "input_hash", "evidence",
        }
        optional = {"provider_id", "model_id", "output_hash"}
        fields = _mapping(value, required, optional, "AuditEvent")
        data = dict(fields)
        if not isinstance(data["evidence"], list):
            raise ValueError("evidence must be an array")
        data["evidence"] = tuple(Evidence.from_dict(item) for item in data["evidence"])
        return cls(**data)


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
        request.__post_init__()
        request_id = str(uuid4())
        decision = self.policy.evaluate(request)
        if not isinstance(decision, PolicyResult):
            raise ValueError("Invalid policy result")
        decision.__post_init__()
        input_hash = digest(json.dumps(request.to_dict(), sort_keys=True, separators=(",", ":")))

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
        record("preflight", decision.reason)
        try:
            response = self.provider.generate(request)
            if not isinstance(response, ModelResponse):
                raise ValueError("Invalid provider response")
            response.__post_init__()
        except Exception:
            record("failed", "provider_error")
            return Result(request_id, "provider_error")
        record("completed", "response_ready", response)
        return Result(request_id, "completed", response.text)
