"""No-LLM MCP protocol client: list + invoke tools, read resource, get prompt.

Usage: python code/client_inspect.py [--http]
Run incident_server.py --http in a separate terminal for the HTTP path.
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from mcp import Client
from mcp.client.stdio import StdioServerParameters

SERVER = Path(__file__).resolve().parent / "incident_server.py"


async def main() -> None:
    endpoint = (
        "http://127.0.0.1:8000/mcp"
        if "--http" in sys.argv
        else StdioServerParameters(command=sys.executable, args=[str(SERVER)])
    )
    async with Client(endpoint) as client:
        print("Negotiated MCP version:", client.protocol_version)
        tool_page = await client.list_tools()
        print("Tools:", [(tool.name, tool.description) for tool in tool_page.tools])
        resource_page = await client.list_resources()
        print("Resources:", [str(resource.uri) for resource in resource_page.resources])
        prompt_page = await client.list_prompts()
        print("Prompts:", [prompt.name for prompt in prompt_page.prompts])

        result = await client.call_tool("get_incident", {"incident_id": "INC-1001"})
        if result.is_error:
            raise RuntimeError(f"Tool returned an error: {result.content}")
        print("Tool result:", json.dumps(result.model_dump(mode="json"), indent=2))

        policy = await client.read_resource("incident://severity-policy")
        print("Policy resource:", [getattr(block, "text", "") for block in policy.contents])

        prompt = await client.get_prompt("triage_brief", {"incident_id": "INC-1001"})
        print("Prompt template:", prompt.model_dump(mode="json"))


if __name__ == "__main__":
    asyncio.run(main())
