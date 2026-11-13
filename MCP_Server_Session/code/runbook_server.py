"""MCP server B: mock operations runbook knowledge base (read-only)."""
from __future__ import annotations

import sys
from typing import Any

from mcp.server import MCPServer

mcp = MCPServer("operations-runbooks")

RUNBOOKS: dict[str, dict[str, Any]] = {
    "RB-PAY-01": {
        "id": "RB-PAY-01", "title": "Payment API elevated 5xx and connection saturation",
        "tags": ["payments-api", "HTTP 503", "database", "connection saturation"],
        "diagnostics": [
            "Compare error ratio and latency by deployment version and region.",
            "Inspect database pool saturation, open connections and query timeouts.",
            "Correlate symptoms to recent change ID and dependency telemetry.",
        ],
        "mitigation": [
            "Stage a rollback proposal for the incident commander to approve.",
            "After approval, roll back safely or reduce traffic to unhealthy shard.",
            "Monitor error ratio, p99 latency and database pool metrics post-change.",
        ],
        "risk": "Rollback or traffic changes are production actions requiring approval.",
    },
    "RB-ID-02": {
        "id": "RB-ID-02", "title": "Identity token refresh timeouts",
        "tags": ["identity-service", "token", "cache", "timeout"],
        "diagnostics": [
            "Compare token refresh timeout rates by platform and region.",
            "Check cache hit rate, eviction volume and upstream latency.",
            "Validate whether retry bursts amplify load.",
        ],
        "mitigation": [
            "Propose safe cache parameter changes for human review.",
            "Validate rate limiting and client retry backoff in staging.",
        ],
        "risk": "Identity changes can lock out users; require change approval and rollback plan.",
    },
    "RB-DATA-03": {
        "id": "RB-DATA-03", "title": "Data pipeline worker queue backlog",
        "tags": ["data-pipeline", "queue", "worker", "ingestion"],
        "diagnostics": [
            "Inspect oldest message age, queue depth and worker concurrency.",
            "Compare retry and dead-letter rates by batch identifier.",
        ],
        "mitigation": ["Propose replay after idempotency assessment and operator approval."],
        "risk": "Uncontrolled replays can duplicate events; require idempotency verification.",
    },
}


@mcp.tool()
def search_runbooks(query: str) -> list[dict[str, Any]]:
    """Search runbooks by literal keywords; returns runbook IDs and previews, not production instructions."""
    query_tokens = {t for t in query.lower().replace("-", " ").split() if len(t) >= 2}
    if not query_tokens:
        raise ValueError("Enter at least one keyword or service name.")
    matches: list[tuple[int, dict[str, Any]]] = []
    for rb in RUNBOOKS.values():
        haystack = " ".join([rb["title"], *rb["tags"]]).lower().replace("-", " ")
        score = sum(token in haystack for token in query_tokens)
        if score:
            matches.append((score, {"id": rb["id"], "title": rb["title"], "score": score, "risk": rb["risk"]}))
    return [rb for _, rb in sorted(matches, key=lambda item: (-item[0], item[1]["id"]))]


@mcp.tool()
def get_runbook(runbook_id: str) -> dict[str, Any]:
    """Read diagnostic and mitigation guidance by runbook ID; no execution is performed."""
    key = runbook_id.strip().upper()
    if key not in RUNBOOKS:
        raise ValueError(f"Unknown runbook ID: {key}. Available: {sorted(RUNBOOKS)}")
    return dict(RUNBOOKS[key])


@mcp.resource("runbook://catalog")
def runbook_catalog() -> str:
    """Published runbook catalog as an application-readable resource."""
    return "\n".join(f'{rb["id"]}: {rb["title"]}' for rb in RUNBOOKS.values())


@mcp.prompt()
def remediation_review(service: str) -> str:
    """User-invoked prompt template for reviewing remediation recommendations."""
    return (
        f"For {service}, produce: evidence, candidate root causes, reversible checks, "
        "mitigation options, validation metrics and human approval checkpoints. "
        "Never claim a production change was made."
    )


if __name__ == "__main__":
    # Both servers are local stdio subprocesses in the multi-server agent demo.
    mcp.run(transport="stdio")
