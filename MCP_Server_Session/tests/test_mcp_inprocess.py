"""Protocol integration tests using the official SDK in-process client.

Requires `pip install 'mcp>=2,<3'`. No network or LLM API key needed.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))

from mcp import Client
from incident_server import mcp as incident_mcp


class TestMCPProtocol(unittest.IsolatedAsyncioTestCase):
    async def test_discover_and_call(self):
        async with Client(incident_mcp) as client:
            tools = await client.list_tools()
            self.assertIn("get_incident", [x.name for x in tools.tools])
            result = await client.call_tool("get_incident", {"incident_id": "INC-1001"})
            self.assertFalse(result.is_error)
            self.assertIn("INC-1001", str(result.model_dump(mode="json")))

    async def test_resource_and_prompt(self):
        async with Client(incident_mcp) as client:
            policy = await client.read_resource("incident://severity-policy")
            self.assertIn("SEV1", str(policy.model_dump(mode="json")))
            prompt = await client.get_prompt("triage_brief", {"incident_id": "INC-1001"})
            self.assertIn("INC-1001", str(prompt.model_dump(mode="json")))

    async def test_tool_error_result(self):
        async with Client(incident_mcp) as client:
            result = await client.call_tool("get_incident", {"incident_id": "INC-9999"})
            self.assertTrue(result.is_error)


if __name__ == "__main__":
    unittest.main()
