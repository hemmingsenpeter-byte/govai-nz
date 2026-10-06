import json
import sqlite3
import unittest

from govai_nz.adapters import SQLiteAuditStore
from govai_nz.core import Classification, Decision, Evidence, Gateway, ModelResponse, PolicyResult, PublicOnlyPolicy, Request, digest


class SpyProvider:
    provider_id = "spy"

    def __init__(self, fail=False):
        self.calls = 0
        self.fail = fail

    def generate(self, request):
        self.calls += 1
        if self.fail:
            raise RuntimeError("DO_NOT_LOG_secret_fixture")
        return ModelResponse("Synthetic response text.", "spy/resolved-v2")


class FailingStore:
    def __init__(self, fail_at):
        self.calls = 0
        self.fail_at = fail_at

    def append(self, event):
        self.calls += 1
        if self.calls == self.fail_at:
            raise OSError("Synthetic unavailable audit store")


class GatewayTests(unittest.TestCase):
    def setUp(self):
        self.audit = SQLiteAuditStore(":memory:")
        self.provider = SpyProvider()
        self.gateway = Gateway(self.provider, PublicOnlyPolicy(), self.audit)

    def tearDown(self):
        self.audit.close()

    def test_allowed_records_actual_model_and_hashes_without_payloads(self):
        request = Request("DO_NOT_LOG_prompt_fixture", Classification.PUBLIC)
        result = self.gateway.run(request)
        events = self.audit.export()
        self.assertEqual(result.status, "completed")
        self.assertEqual(self.provider.calls, 1)
        self.assertEqual([e["phase"] for e in events], ["preflight", "completed"])
        self.assertEqual(events[0]["request_id"], result.request_id)
        self.assertEqual(events[1]["request_id"], result.request_id)
        self.assertNotEqual(events[0]["event_id"], events[1]["event_id"])
        self.assertEqual(events[1]["model_id"], "spy/resolved-v2")
        self.assertEqual(events[1]["output_hash"], digest(result.text))
        self.assertNotIn(request.prompt, json.dumps(events))
        self.assertNotIn(result.text, json.dumps(events))

    def test_non_public_never_calls_provider(self):
        result = self.gateway.run(Request("Synthetic", Classification.NON_PUBLIC))
        self.assertEqual(result.status, "deny")
        self.assertEqual(self.provider.calls, 0)
        self.assertEqual(self.audit.export()[0]["phase"], "stopped")

    def test_personal_information_never_calls_provider(self):
        result = self.gateway.run(Request("Synthetic", Classification.PUBLIC, contains_personal_information=True))
        self.assertEqual(result.status, "deny")
        self.assertEqual(self.provider.calls, 0)

    def test_review_stops_before_execution(self):
        result = self.gateway.run(Request("Synthetic", Classification.PUBLIC, high_impact=True))
        self.assertEqual(result.status, "review_required")
        self.assertIsNone(result.text)
        self.assertEqual(self.provider.calls, 0)

    def test_deny_takes_precedence_over_review(self):
        result = self.gateway.run(Request("Synthetic", Classification.NON_PUBLIC, high_impact=True))
        self.assertEqual(result.status, "deny")
        self.assertEqual(self.provider.calls, 0)

    def test_preflight_failure_prevents_provider_call(self):
        gateway = Gateway(self.provider, PublicOnlyPolicy(), FailingStore(1))
        with self.assertRaises(OSError):
            gateway.run(Request("Synthetic", Classification.PUBLIC))
        self.assertEqual(self.provider.calls, 0)

    def test_outcome_audit_failure_prevents_release(self):
        gateway = Gateway(self.provider, PublicOnlyPolicy(), FailingStore(2))
        with self.assertRaises(OSError):
            gateway.run(Request("Synthetic", Classification.PUBLIC))
        self.assertEqual(self.provider.calls, 1)

    def test_provider_failure_is_audited_without_secret(self):
        provider = SpyProvider(fail=True)
        gateway = Gateway(provider, PublicOnlyPolicy(), self.audit)
        result = gateway.run(Request("Synthetic", Classification.PUBLIC))
        self.assertEqual(result.status, "provider_error")
        self.assertIsNone(result.text)
        self.assertEqual([e["phase"] for e in self.audit.export()], ["preflight", "failed"])
        self.assertNotIn("DO_NOT_LOG_secret_fixture", json.dumps(self.audit.export()))

    def test_evidence_is_carried_but_not_claimed_verified(self):
        evidence = Evidence("https://example.invalid/synthetic", "fixture/v1", "2026-10-06T00:00:00Z", digest("fixture"))
        self.gateway.run(Request("Synthetic", Classification.PUBLIC, evidence=(evidence,)))
        self.assertEqual(self.audit.export()[1]["evidence"][0]["content_hash"], evidence.content_hash)

    def test_unknown_classification_rejected(self):
        with self.assertRaises(ValueError):
            Request("Synthetic", "unknown")

    def test_non_boolean_policy_flags_rejected(self):
        with self.assertRaises(ValueError):
            Request("Synthetic", Classification.PUBLIC, high_impact="false")

    def test_evidence_field_types_rejected(self):
        for invalid in (None, 42, {}, "", " "):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                Evidence(invalid, "v1", "timestamp", "hash")

    def test_policy_failures_are_audited_without_payload(self):
        class BrokenPolicy:
            def evaluate(self, request):
                raise RuntimeError("DO_NOT_LOG_policy_secret")

        result = Gateway(self.provider, BrokenPolicy(), self.audit).run(
            Request("DO_NOT_LOG_prompt", Classification.PUBLIC))
        self.assertEqual(result.status, "policy_error")
        self.assertEqual(self.provider.calls, 0)
        event = self.audit.export()[0]
        self.assertEqual(event["phase"], "failed")
        self.assertIsNone(event["decision"])
        self.assertNotIn("DO_NOT_LOG", json.dumps(event))

    def test_invalid_policy_result_is_audited(self):
        class InvalidPolicy:
            def evaluate(self, request):
                return object()

        result = Gateway(self.provider, InvalidPolicy(), self.audit).run(
            Request("Synthetic", Classification.PUBLIC))
        self.assertEqual(result.status, "policy_error")
        self.assertEqual(self.provider.calls, 0)
        self.assertEqual(len(self.audit.export()), 1)

    def test_policy_metadata_types_rejected(self):
        for args in (("allow", "reason", "v1"), (Decision.ALLOW, 42, "v1"),
                     (Decision.ALLOW, "reason", "")):
            with self.subTest(args=args), self.assertRaises(ValueError):
                PolicyResult(*args)

    def test_tampered_evidence_is_audited_without_fields(self):
        evidence = Evidence("uri", "v1", "timestamp", "hash")
        request = Request("Synthetic", Classification.PUBLIC, evidence=(evidence,))
        object.__setattr__(evidence, "source_uri", {"DO_NOT_LOG": object()})
        result = self.gateway.run(request)
        self.assertEqual(result.status, "input_error")
        self.assertEqual(self.provider.calls, 0)
        event = self.audit.export()[0]
        self.assertEqual(event["evidence"], [])
        self.assertIsNone(event["input_hash"])
        self.assertNotIn("DO_NOT_LOG", json.dumps(event))

    def test_hashing_failure_is_audited(self):
        from unittest.mock import patch
        with patch("govai_nz.core.digest", side_effect=ValueError("DO_NOT_LOG_hash")):
            result = self.gateway.run(Request("Synthetic", Classification.PUBLIC))
        self.assertEqual(result.status, "input_error")
        self.assertEqual(self.provider.calls, 0)
        self.assertNotIn("DO_NOT_LOG", json.dumps(self.audit.export()))

    def test_early_failure_audit_error_propagates(self):
        gateway = Gateway(self.provider, PublicOnlyPolicy(), FailingStore(1))
        with self.assertRaises(OSError):
            gateway.run(object())
        self.assertEqual(self.provider.calls, 0)

    def test_invalid_model_id_is_audited_as_provider_error(self):
        class InvalidProvider(SpyProvider):
            def generate(self, request):
                self.calls += 1
                response = ModelResponse("Synthetic", "valid")
                object.__setattr__(response, "model_id", 42)
                return response

        provider = InvalidProvider()
        result = Gateway(provider, PublicOnlyPolicy(), self.audit).run(
            Request("Synthetic", Classification.PUBLIC))
        self.assertEqual(result.status, "provider_error")
        self.assertIsNone(result.text)
        self.assertIsNone(self.audit.export()[-1]["model_id"])
        self.assertEqual(self.audit.export()[-1]["decision"], "allow")

    def test_model_response_types_rejected(self):
        for text, model in ((42, "model"), ("text", 42), ("text", " ")):
            with self.subTest(model=model), self.assertRaises(ValueError):
                ModelResponse(text, model)

    def test_orphaned_preflight_is_detectable_after_terminal_write_failure(self):
        audit = self.audit

        class FailTerminal:
            def append(self, event):
                if event.phase != "preflight":
                    raise OSError("Synthetic unavailable audit store")
                audit.append(event)

        with self.assertRaises(OSError):
            Gateway(self.provider, PublicOnlyPolicy(), FailTerminal()).run(
                Request("Synthetic", Classification.PUBLIC))
        self.assertEqual(len(audit.orphaned_preflights()), 1)
        self.assertEqual(self.provider.calls, 1)

    def test_completed_requests_are_not_orphans(self):
        self.gateway.run(Request("Synthetic", Classification.PUBLIC))
        self.assertEqual(self.audit.orphaned_preflights(), [])

    def test_sqlite_rejects_duplicate_event_id(self):
        self.gateway.run(Request("Synthetic", Classification.PUBLIC))
        event_id = self.audit.export()[0]["event_id"]
        with self.assertRaises(sqlite3.IntegrityError):
            with self.audit.connection:
                self.audit.connection.execute("INSERT INTO events (event_id, payload) VALUES (?, ?)", (event_id, "{}"))
        self.assertEqual(len(self.audit.export()), 2)


if __name__ == "__main__":
    unittest.main()
