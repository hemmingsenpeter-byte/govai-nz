import json
import sqlite3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from govai_nz.adapters import SQLiteAuditStore
from govai_nz.core import Classification, Evidence, Gateway, ModelResponse, PublicOnlyPolicy, Request, digest


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

    def test_sqlite_rejects_duplicate_event_id(self):
        self.gateway.run(Request("Synthetic", Classification.PUBLIC))
        event_id = self.audit.export()[0]["event_id"]
        with self.assertRaises(sqlite3.IntegrityError):
            with self.audit.connection:
                self.audit.connection.execute("INSERT INTO events (event_id, payload) VALUES (?, ?)", (event_id, "{}"))
        self.assertEqual(len(self.audit.export()), 2)


if __name__ == "__main__":
    unittest.main()
