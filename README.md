# Enterprise RAG Agent System (`mcptester`)

## Vision & Purpose
This project is a custom, Python-based autonomous **Company RAG (Retrieval-Augmented Generation) Agent** built from scratch. It serves as an intelligent core for internal employees, allowing them to instantly query company knowledge bases, automate repetitive workflows, and generate comprehensive reports. By leveraging the Model Context Protocol (MCP), the system maintains full control over data privacy, system design, and tool orchestration.

The agent, named **Nexus**, is an Enterprise Intelligence Agent designed to be professional, precise, and highly analytical. It operates on a strict ReAct (Reason + Act) loop, ensuring it never guesses and always consults the internal knowledge base for company data.

## Core Architecture
The system is structured around three primary pillars:
1. **The RAG Engine (Python Backend):** A vector database (currently SQLite-based) and retrieval system capable of ingesting internal documents and performing semantic search.
2. **The Agentic Orchestrator (ReAct):** The central logic loop that forces the LLM to Observe, Think, Act, and Observe again. It decides when to search the knowledge base and when to execute workflow tools.
3. **The MCP Server Interface & Next.js Frontend:** A protocol layer that exposes the Python backend tools to external clients. A Next.js frontend provides a chat interface for employees to interact with the agent.

## Project Structure
- `agent/`: The Python backend containing the FastAPI server, ReAct agent logic, and MCP tools.
- `project/`: The Next.js frontend application providing the user interface.
- `project.md`: Product Requirements Document outlining phases and tech stack.
- `persona.md`: Defines the Nexus agent's persona and system prompts.

## Setup Instructions

### 1. Python Backend (`agent/`)
The backend is built with Python 3.11+, FastAPI, and the official MCP SDK.

1. Navigate to the agent directory:
   ```bash
   cd agent
   ```
2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```bash
   # If you use uv (recommended as per project.md)
   uv pip install -r pyproject.toml # or install individual dependencies listed in pyproject.toml

   # Or using standard pip
   pip install fastapi mcp openai pydantic python-dotenv sse-starlette uvicorn
   ```
4. Configure environment variables:
   Create a `.env` file in the `agent/` directory based on `.env.example` (or set `DEEPSEEK_API_KEY`).
5. Run the backend server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

### 2. Next.js Frontend (`project/`)
The frontend is a Next.js application using the Vercel AI SDK.

1. Navigate to the project directory:
   ```bash
   cd project
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Configure environment variables:
   Create a `.env` file in the `project/` directory based on `.env.example`. You will need API keys for your chosen providers (e.g., OPENAI_API_KEY).
4. Run the development server:
   ```bash
   npm run dev
   ```
5. Open your browser and navigate to `http://localhost:3000` to interact with the Nexus agent.

## Tools Overview
The agent is currently equipped with the following tools:
- `search_company_knowledge`: Searches the internal SQLite knowledge base.
- `generate_report`: Compiles retrieved data into structured Markdown reports.
- `save_note_to_knowledge_base`: Saves new notes, policies, or decisions directly into the knowledge base for future retrieval.
