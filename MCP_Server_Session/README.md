# MCP Server & Agent Integration


## Contents

- `01_MCP_2_Hour_Intermediate_Workshop.md` — full 120-minute session plan, detailed MCP architecture, wire protocol, security, explanations, demo instructions and references.
- `02_Homework_MCP_Enterprise_Agent.md` — individual practical assignment, acceptance scenarios, deliverables and 100-point rubric.
- `code/incident_data.py` — dependency-free fictional incident data and validation logic.
- `code/incident_server.py` — MCP server with tools, resources, templated resources and prompt; stdio or HTTP.
- `code/runbook_server.py` — second independent read-only MCP server.
- `code/client_inspect.py` — protocol-level SDK client showing tool discovery/call, resource read and prompt get.
- `code/agent_single.py` — LangChain agent using one MCP server.
- `code/agent_multi.py` — agent using two MCP servers, with namespaced tools.
- `code/agent_http.py` — LangChain agent connecting to localhost MCP over Streamable HTTP.
- `tests/test_domain.py` — five standard-library unit tests; no MCP dependencies.
- `tests/test_mcp_inprocess.py` — MCP protocol integration tests using the official in-process client.
- `requirements.txt`, `.env.example` — Python dependency hints and optional LLM settings.

## Quickstart

Requires **Python 3.11+** and access to install packages. Run from the extracted workshop directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s tests -p 'test_domain.py' -v
python -m unittest discover -s tests -p 'test_mcp_inprocess.py' -v
python code/client_inspect.py
```

For HTTP, use two terminals:

```bash
# Terminal 1
python code/incident_server.py --http
# Terminal 2
python code/client_inspect.py --http
```

For model-backed agents (provider charges may apply):

```bash
export OPENAI_API_KEY='YOUR_KEY'  # PowerShell: $env:OPENAI_API_KEY='YOUR_KEY'
python code/agent_single.py
python code/agent_multi.py
# With HTTP server still running:
python code/agent_http.py
```

`MCP_DEMO_MODEL` defaults to `openai:gpt-4.1-mini`. If switching providers, install the relevant LangChain provider integration and configure its credentials. Avoid sharing API keys in code, logs or homework submissions.

## Notes for architects

- **Local stdio is not ordinary stdout logging.** The server must reserve stdout for MCP JSON-RPC and log through stderr.
- **This package is read-only.** It never touches production ITSM, databases, payment APIs or infrastructure. The homework's write functionality is deliberately restricted to an approval-bound *draft proposal*.
- **The HTTP listener is loopback-only and unauthenticated.** It is for teaching transport differences, not a production-ready service.
- **A tool schema is not access control.** Add per-principal resource authorisation at server/backend layers when connecting to real data.
- **Latest MCP protocol:** the July 2026 version has stateless per-request metadata and `server/discover`, replacing the old per-connection `initialize` core. Older examples on the internet may not work against the v2 SDK unchanged.
- **Current LangChain integration:** use `from langchain.mcp import MCPAdapter`; older tutorials may refer to `langchain_mcp_adapters` and `MultiServerMCPClient`.
- **Dependency discipline:** these are workshop version ranges, not a production lockfile. Pin compatible versions and check upgrades before enterprise release.

## Verification status

**Verified in the authoring environment:** all included `.py` files passed Python `compileall`; all **five dependency-free unit tests passed**.

**Not verified in the authoring environment:** installing `mcp`/`langchain` packages and executing the protocol-level or model-backed integrations. Package-network access was unavailable, so code was checked against published upstream documentation but could not be end-to-end executed here. Please install dependencies and run `tests/test_mcp_inprocess.py` and the agent demos on a connected development machine before delivery. Do not treat these examples as audited production code.

## Primary references

- MCP specification: https://modelcontextprotocol.io/specification/2026-07-28
- Official MCP Python SDK: https://github.com/modelcontextprotocol/python-sdk
- Python SDK migration guide: https://github.com/modelcontextprotocol/python-sdk/blob/main/docs/migration.md
- LangChain MCPAdapter integration: https://www.langchain.com/blog/mcp-in-langchain-stateless-protocol-elicitation-and-more
- OWASP MCP security: https://cheatsheetseries.owasp.org/cheatsheets/MCP_Security_Cheat_Sheet.html
