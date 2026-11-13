"""Fictional incident dataset and pure domain logic for MCP training.

No network calls, credentials, production data, or side effects are used.
The functions here can be tested without installing the MCP SDK.
"""
from __future__ import annotations

from collections import Counter
from typing import Any


INCIDENTS: dict[str, dict[str, Any]] = {
    "INC-1001": {
        "id": "INC-1001", "service": "payments-api", "severity": "SEV1",
        "status": "investigating", "started_at": "2026-11-10T08:05:00Z",
        "summary": "Payment authorisations intermittently fail after a deployment.",
        "symptoms": ["HTTP 503 spike", "elevated p99 latency", "database connection saturation"],
        "affected_regions": ["ap-south-1"], "estimated_users_affected": 18000,
        "change_reference": "CHG-208", "owner_team": "payments-platform",
        "reporter_note": "Rollback decision requires incident commander approval.",
    },
    "INC-1002": {
        "id": "INC-1002", "service": "identity-service", "severity": "SEV2",
        "status": "mitigating", "started_at": "2026-11-10T09:40:00Z",
        "summary": "Login attempts time out for a subset of mobile users.",
        "symptoms": ["token refresh timeout", "high cache miss rate"],
        "affected_regions": ["ap-south-1", "ap-southeast-1"],
        "estimated_users_affected": 3200, "change_reference": "CHG-203",
        "owner_team": "identity-platform", "reporter_note": "Some clients retry aggressively.",
    },
    "INC-1003": {
        "id": "INC-1003", "service": "data-pipeline", "severity": "SEV3",
        "status": "monitoring", "started_at": "2026-11-09T18:20:00Z",
        "summary": "Scheduled ingestion is delayed due to worker backlog.",
        "symptoms": ["queue lag", "retries increased"],
        "affected_regions": ["ap-south-1"], "estimated_users_affected": 200,
        "change_reference": "CHG-197", "owner_team": "data-engineering",
        "reporter_note": "Batch replay tested in staging only.",
    },
    "INC-1004": {
        "id": "INC-1004", "service": "payments-api", "severity": "SEV2",
        "status": "resolved", "started_at": "2026-11-08T05:00:00Z",
        "summary": "Gateway throttling triggered elevated checkout failures.",
        "symptoms": ["HTTP 429", "rate-limit exhaustion"],
        "affected_regions": ["eu-west-1"], "estimated_users_affected": 740,
        "change_reference": "CHG-188", "owner_team": "payments-platform",
        "reporter_note": "Resolved by approved traffic shaping change.",
    },
}

VALID_SEVERITIES = {"SEV1", "SEV2", "SEV3", "SEV4"}


def get_incident_record(incident_id: str) -> dict[str, Any]:
    """Retrieve a record by exact ID, raising a clear error for unknown IDs."""
    clean_id = incident_id.strip().upper()
    if clean_id not in INCIDENTS:
        raise ValueError(f"Unknown incident ID: {clean_id}. Choose from {sorted(INCIDENTS)}")
    return dict(INCIDENTS[clean_id])


def find_incidents(severity: str = "all", service: str = "all") -> list[dict[str, Any]]:
    """Read-only exact-filter search; results are ordered by incident ID."""
    sev = severity.strip().upper()
    svc = service.strip().lower()
    if sev != "ALL" and sev not in VALID_SEVERITIES:
        raise ValueError(f"Severity must be one of ALL, {', '.join(sorted(VALID_SEVERITIES))}")
    if svc != "all" and svc not in {i["service"] for i in INCIDENTS.values()}:
        raise ValueError("Unknown service. Use 'all' or a service from the incident catalog.")
    return [
        dict(incident)
        for _, incident in sorted(INCIDENTS.items())
        if (sev == "ALL" or incident["severity"] == sev)
        and (svc == "all" or incident["service"] == svc)
    ]


def incident_metrics() -> dict[str, Any]:
    """Deterministic counts for demonstrations of structured tool output."""
    records = list(INCIDENTS.values())
    return {
        "incident_count": len(records),
        "by_severity": dict(Counter(r["severity"] for r in records)),
        "by_status": dict(Counter(r["status"] for r in records)),
        "total_estimated_users_affected": sum(r["estimated_users_affected"] for r in records),
        "dataset_type": "fictional_training_data",
    }
