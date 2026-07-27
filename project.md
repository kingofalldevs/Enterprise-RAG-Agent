# Project: Enterprise RAG Agent System (`mcptester`)

## 1. Vision & Purpose
The goal of this project is to build a custom, Python-based autonomous **Company RAG (Retrieval-Augmented Generation) Agent** from scratch. This system will serve as the intelligent core for internal employees, allowing them to instantly query company knowledge bases, automate repetitive workflows, and generate comprehensive reports. By building this from scratch using the Model Context Protocol (MCP), we maintain full control over data privacy, system design, and tool orchestration.

## 2. Core Architecture
This system will be built in **Python** and structured around three primary pillars:
1. **The RAG Engine:** A vector database and retrieval system capable of ingesting internal company documents (PDFs, wikis, codebase) and performing semantic search.
2. **The Agentic Orchestrator (ReAct):** The central logic loop that forces the LLM to Observe, Think, Act, and Observe again. It decides *when* to search the knowledge base and *when* to execute a workflow tool.
3. **The MCP Server Interface:** A protocol layer that exposes this Python backend and its tools to external clients (like our Next.js frontend or Claude Desktop), making the agent accessible to the entire company.

## 3. Product Requirements (PRD)

### Phase 1: Knowledge Retrieval (RAG Foundation)
*   **Requirement:** Implement a document ingestion pipeline to chunk and embed company data into a vector database (e.g., ChromaDB, Qdrant, or Pinecone).
*   **Requirement:** Build a `search_company_knowledge` tool that performs similarity search against the vector database based on user queries.
*   **Requirement:** Connect to an LLM provider to synthesize the retrieved context into accurate, hallucination-free answers.

### Phase 2: Autonomous Workflows & Tooling
*   **Requirement:** Build the ReAct `while` loop that intercepts tool calls and executes them locally.
*   **Requirement:** Create standard automation tools for employees:
    *   `generate_report`: Compiles data into structured formats (CSV/Markdown).
    *   `query_internal_api`: Connects to internal company services (HR, Jira, etc.).
*   **Requirement:** Ensure the agent can handle multi-step workflows (e.g., "Find the Q3 marketing stats and generate a summary report").

### Phase 3: Deployment & Next.js Bridge
*   **Requirement:** Wrap the agent and RAG tools in the official Model Context Protocol (MCP).
*   **Requirement:** Expose the Python agent over an HTTP/SSE stream so the Next.js frontend (`mcp project`) can provide a beautiful chat interface for employees.

## 4. Tech Stack (Proposed)
*   **Language:** Python 3.11+
*   **LLM Interface:** `openai` package or `httpx` (for raw REST calls)
*   **Embeddings & Vector Store:** `sentence-transformers` / `chromadb` (or similar)
*   **Protocol:** `mcp` (Official Python Model Context Protocol SDK)
*   **Environment:** `uv` or `venv` for dependency management

## 5. Next Steps / Open Questions
> [!IMPORTANT]
> 1. For the RAG database, do you want to start with a lightweight local database like **ChromaDB** or **FAISS**, or a cloud solution like **Pinecone**?
> 2. What types of internal documents (PDFs, Notion pages, raw text) will we be starting with for the knowledge source?
