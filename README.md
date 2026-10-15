# Enterprise RAG Agent

This directory contains the Python API for Nexus, a tool-calling chat agent. It uses DeepSeek's OpenAI-compatible chat API, exposes an OpenAI-style streaming endpoint for the Next.js app, and can dispatch tool calls to local SQLite handlers or configured remote MCP servers.

## How it works

1. The Next.js chat app sends conversation messages to `POST /v1/chat/completions`.
2. The agent streams the model response. If the model requests tools, the agent dispatches each call and adds the result to the conversation before asking the model to continue.
3. Local knowledge search reads text chunks from `project/sqlite.db`. Remote tool definitions and calls are loaded from `mcp_servers.json`.

The agent's local tools are:

- `search_company_knowledge`: searches uploaded document chunks using SQLite `LIKE` matching.
- `save_note_to_knowledge_base`: inserts a note into the same chunks table.
- `generate_report`: returns a Markdown-style report summary; it does not persist a report.

## Requirements

- Python 3.11 or newer
- Node.js and pnpm, for initializing the shared SQLite database through the Next.js project
- A DeepSeek API key

## Local setup

From the repository root, install the web project's dependencies, create the SQLite tables, and add your DeepSeek key to `.env`:

```bash
cd project
pnpm install
node init-db.js
cd ..
cp .env.example .env
```

Set `DEEPSEEK_API_KEY` in the root `.env`. The agent loads this key with `python-dotenv` and sends requests to `https://api.deepseek.com` using the `deepseek-chat` model.

Install and start the Python API:

```bash
cd agent
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn main:app --reload --port 8000
```

The agent API is now available at `http://localhost:8000`. Its health check is `GET /health`. Start the web app separately from `project/` with `pnpm dev`; the frontend is configured to use the local agent API on port 8000.

## Remote MCP tools

Remote MCP servers are configured in `mcp_servers.json`. The client attempts the `/mcp/tools` and `/mcp/call` HTTP endpoints first, then falls back to MCP JSON-RPC requests. The included `remote_mcp_server.py` is a static demo server with sample weather and employee-directory tools. Run it in a second terminal from this directory:

```bash
source .venv/bin/activate
python remote_mcp_server.py
```

It listens on port 8001, matching the `local_test_server` entry in the default config. Edit the config to add or remove servers. Keep real credentials out of source control; use a local, ignored configuration for any server requiring authentication.

## Current scope

This is an early prototype, not a production-ready semantic RAG system. Knowledge search is exact substring matching rather than vector similarity, and uploaded chunks currently have empty embeddings. The sample remote server returns fixed example data. The API does not implement user authentication or authorization, so keep it on a trusted local network and do not expose it publicly as-is.
