"""MCP server A: incident catalog with tools, resources, and a prompt.

Usage:
  python code/incident_server.py          # stdio (spawned by MCP client)
  python code/incident_server.py --http   # local Streamable HTTP on :8000/mcp

IMPORTANT: Never print to stdout while using stdio; stdout carries JSON-RPC.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from mcp.server import MCPServer

# Allow execution from any working directory, not only repository root.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from incident_data import find_incidents, get_incident_record, incident_metrics  # noqa: E402

mcp = MCPServer(
    "enterprise-incidents",
    instructions="Read-only incident information for a fictional training environment.",
)


@mcp.tool()
def list_incidents(severity: str = "all", service: str = "all") -> list[dict[str, Any]]:
    """List fictional incidents. Exact filters: severity=all/SEV1/SEV2/SEV3/SEV4, service=all or service name."""
    return find_incidents(severity, service)


@mcp.tool()
def get_incident(incident_id: str) -> dict[str, Any]:
    """Get the details of one fictional incident, such as INC-1001, by its exact ID."""
    return get_incident_record(incident_id)


@mcp.tool()
def get_incident_metrics() -> dict[str, Any]:
    """Return severity counts, status counts and total estimated affected users for the training data."""
    return incident_metrics()


@mcp.resource("incident://severity-policy")
def severity_policy() -> str:
    """Read-only severity classification policy."""
    return (
        "SEV1: critical customer impact, coordinate incident command immediately.\n"
        "SEV2: major partial degradation, triage within 30 minutes.\n"
        "SEV3: contained degradation, planned remediation.\n"
        "SEV4: informational or low-impact issue.\n"
        "All action recommendations need validation against observed telemetry."
    )


@mcp.resource("incident://{incident_id}")
def incident_resource(incident_id: str) -> str:
    """Resource template: read a single incident as a compact text document."""
    record = get_incident_record(incident_id)
    return "\n".join(f"{key}: {value}" for key, value in record.items())


@mcp.prompt()
def triage_brief(incident_id: str) -> str:
    """User-invoked prompt template for incident analysis."""
    return (
        f"Create a structured triage brief for {incident_id}. Distinguish observed facts from "
        "hypotheses. Cite the incident ID, list likely contributing factors, propose a "
        "low-risk diagnostic plan, and explicitly flag actions requiring human approval."
    )


if __name__ == "__main__":
    if "--http" in sys.argv:
        # Local demonstration only. Put authenticated HTTPS reverse proxy in front
        # of any remotely reachable HTTP deployment; never open this to the internet.
        mcp.run(transport="streamable-http", host="127.0.0.1", port=8000, json_response=True)
    else:
        mcp.run(transport="stdio")
