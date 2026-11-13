"""Standard-library unit tests, no MCP package or API key needed."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))

from incident_data import find_incidents, get_incident_record, incident_metrics  # noqa: E402


class TestIncidentDomain(unittest.TestCase):
    def test_get_incident(self):
        self.assertEqual(get_incident_record(" inc-1001 ")["severity"], "SEV1")

    def test_filter(self):
        self.assertEqual([x["id"] for x in find_incidents("SEV2")], ["INC-1002", "INC-1004"])

    def test_unknown_severity_rejected(self):
        with self.assertRaises(ValueError):
            find_incidents("SEV0")

    def test_missing_incident_rejected(self):
        with self.assertRaises(ValueError):
            get_incident_record("INC-9999")

    def test_metrics(self):
        metrics = incident_metrics()
        self.assertEqual(metrics["incident_count"], 4)
        self.assertEqual(metrics["by_severity"]["SEV2"], 2)


if __name__ == "__main__":
    unittest.main()
