import json
import sys
import unittest
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from govai_nz.core import (
    MAX_EVIDENCE_ITEMS,
    MAX_PROMPT_LENGTH,
    MAX_RESPONSE_LENGTH,
    AuditEvent,
    Classification,
    Decision,
    Evidence,
    ModelResponse,
    PolicyResult,
    Request,
    digest,
)


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.evidence = Evidence(
            "https://example.invalid/synthetic",
            "fixture/v1",
            "2026-10-06T00:00:00Z",
            digest("synthetic fixture"),
        )
        self.request = Request(
            "Synthetic request",
            Classification.PUBLIC,
            evidence=(self.evidence,),
        )
        self.policy_result = PolicyResult(Decision.ALLOW, "declared_public", "public-only/v1")
        self.response = ModelResponse("Synthetic response", "mock/v1")
        self.audit_event = AuditEvent(
            schema_version="0.1",
            event_id=str(uuid4()),
            request_id=str(uuid4()),
            timestamp="2026-10-06T00:00:00+00:00",
            application="govai-nz-demo",
            application_version="0.0.1",
            phase="completed",
            decision="allow",
            reason="response_ready",
            policy_version="public-only/v1",
            classification="public",
            input_hash=digest("Synthetic request"),
            evidence=(self.evidence,),
            provider_id="mock",
            model_id="mock/v1",
            output_hash=digest("Synthetic response"),
        )

    def test_contracts_round_trip(self):
        cases = (
            (Evidence, self.evidence),
            (Request, self.request),
            (PolicyResult, self.policy_result),
            (ModelResponse, self.response),
            (AuditEvent, self.audit_event),
        )
        for contract, value in cases:
            with self.subTest(contract=contract.__name__):
                serialized = value.to_dict()
                restored = contract.from_dict(json.loads(json.dumps(serialized)))
                self.assertEqual(restored, value)

    def test_request_defaults_are_applied_and_unknown_fields_rejected(self):
        request = Request.from_dict({"prompt": "Synthetic", "classification": "public"})
        self.assertEqual(request, Request("Synthetic", Classification.PUBLIC))
        with self.assertRaisesRegex(ValueError, "unexpected fields"):
            Request.from_dict({
                "prompt": "Synthetic",
                "classification": "public",
                "unrecognized": True,
            })

    def test_serialization_revalidates_nested_evidence(self):
        object.__setattr__(self.evidence, "content_hash", "invalid")
        with self.assertRaises(ValueError):
            self.request.to_dict()
        with self.assertRaises(ValueError):
            self.audit_event.to_dict()

    def test_evidence_validation_rejects_invalid_uri_timestamp_and_digest(self):
        invalid_values = (
            {"source_uri": "file:///private", "version_id": "v1",
             "retrieved_at": "2026-10-06T00:00:00Z", "content_hash": digest("x")},
            {"source_uri": "https://@example.invalid", "version_id": "v1",
             "retrieved_at": "2026-10-06T00:00:00Z", "content_hash": digest("x")},
            {"source_uri": "https://éxample.invalid", "version_id": "v1",
             "retrieved_at": "2026-10-06T00:00:00Z", "content_hash": digest("x")},
            {"source_uri": "https://example.invalid/%zz", "version_id": "v1",
             "retrieved_at": "2026-10-06T00:00:00Z", "content_hash": digest("x")},
            {"source_uri": "******example.invalid", "version_id": "v1",
             "retrieved_at": "2026-10-06T00:00:00Z", "content_hash": digest("x")},
            {"source_uri": "https://example.invalid:invalid", "version_id": "v1",
             "retrieved_at": "2026-10-06T00:00:00Z", "content_hash": digest("x")},
            {"source_uri": "https://example.invalid", "version_id": "v1",
             "retrieved_at": "2026-10-06T00:00:00+01:00", "content_hash": digest("x")},
            {"source_uri": "https://example.invalid", "version_id": "v1",
             "retrieved_at": "2026-10-06T00:00:00.1234567Z", "content_hash": digest("x")},
            {"source_uri": "https://example.invalid", "version_id": "v1",
             "retrieved_at": "2026-10-06T00:00:00Z", "content_hash": "A" * 64},
        )
        for value in invalid_values:
            with self.subTest(value=value), self.assertRaises(ValueError):
                Evidence.from_dict(value)

    def test_request_limits_and_unknown_labels_are_rejected(self):
        with self.assertRaises(ValueError):
            Request("x" * (MAX_PROMPT_LENGTH + 1), Classification.PUBLIC)
        with self.assertRaises(ValueError):
            Request.from_dict({"prompt": "Synthetic", "classification": "secret"})
        with self.assertRaises(ValueError):
            Request("Synthetic", Classification.PUBLIC, evidence=tuple(
                self.evidence for _ in range(MAX_EVIDENCE_ITEMS + 1)
            ))

    def test_policy_and_response_reject_invalid_values(self):
        with self.assertRaises(ValueError):
            PolicyResult.from_dict({
                "decision": "permit",
                "reason": "declared_public",
                "policy_version": "public-only/v1",
            })
        with self.assertRaises(ValueError):
            PolicyResult.from_dict({
                "decision": "allow",
                "reason": "declared_public",
                "policy_version": "public-only/v1",
                "extra": "rejected",
            })
        with self.assertRaises(ValueError):
            ModelResponse("x" * (MAX_RESPONSE_LENGTH + 1), "mock/v1")
        with self.assertRaises(ValueError):
            ModelResponse.from_dict({"text": "response", "model_id": "mock/v1", "extra": 1})

    def test_audit_event_rejects_unknown_fields_versions_ids_and_non_utc_times(self):
        event = self.audit_event.to_dict()
        for name, value in (
            ("extra", "rejected"),
            ("schema_version", "0.2"),
            ("event_id", "not-a-uuid"),
            ("timestamp", "2026-10-06T00:00:00+01:00"),
            ("input_hash", "not-a-digest"),
        ):
            invalid = dict(event)
            invalid[name] = value
            with self.subTest(field=name), self.assertRaises(ValueError):
                AuditEvent.from_dict(invalid)

    def test_versioned_schema_bundle_is_strict_and_records_legacy_audit_version(self):
        schema_path = Path(__file__).resolve().parents[1] / "src" / "govai_nz" / "contracts.v1.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(schema["$defs"]["auditEvent"]["properties"]["schema_version"], {"const": "0.1"})
        for name in ("request", "policyResult", "evidence", "modelResponse", "auditEvent"):
            with self.subTest(contract=name):
                self.assertFalse(schema["$defs"][name]["additionalProperties"])


if __name__ == "__main__":
    unittest.main()
