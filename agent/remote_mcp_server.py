import json
import asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

app = FastAPI(title="Sample Remote MCP Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Remote tool definitions offered by this external MCP server
REMOTE_TOOLS = [
    {
        "name": "remote_weather_lookup",
        "description": "Fetches current weather and environmental data for a remote location from external service.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City or location name."
                }
            },
            "required": ["location"]
        }
    },
    {
        "name": "remote_company_directory",
        "description": "Queries the remote corporate employee directory service.",
        "parameters": {
            "type": "object",
            "properties": {
                "department": {
                    "type": "string",
                    "description": "Department name (e.g. Engineering, Sales, Support)."
                }
            },
            "required": ["department"]
        }
    }
]

@app.get("/mcp/tools")
async def list_tools():
    """Endpoint for MCP client to discover available remote tools."""
    return {"tools": REMOTE_TOOLS}

@app.post("/mcp/call")
async def call_tool(request: Request):
    """Endpoint for executing a remote tool call."""
    payload = await request.json()
    tool_name = payload.get("name")
    arguments = payload.get("arguments", {})

    print(f"🌐 [Remote MCP Server] Executing tool '{tool_name}' with args: {arguments}")

    if tool_name == "remote_weather_lookup":
        location = arguments.get("location", "Unknown")
        return {
            "result": f"[Remote Service] Weather in {location}: 22°C (71°F), Partly Cloudy, Humidity 45%, Wind 10 mph. Status: Optimal."
        }
    elif tool_name == "remote_company_directory":
        dept = arguments.get("department", "General")
        return {
            "result": f"[Remote Service Directory - {dept}]\n- Lead: Alex Rivera (alex@{dept.lower()}.kestrel.com)\n- Team Size: 14 active members\n- On-call: Sam Taylor"
        }

    return {"error": f"Tool '{tool_name}' not found on remote MCP server."}

@app.get("/health")
async def health():
    return {"status": "ok", "service": "Remote MCP Server"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
