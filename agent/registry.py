from tools import tools_definition as local_tools_def, execute_tool as execute_local_tool
from mcp_client import RemoteMCPClient

# Initialize MCP client instance loading from mcp_servers.json configuration
remote_mcp_client = RemoteMCPClient()

_cached_remote_tools = None

async def get_all_tools() -> list:
    """Combines local tools and dynamically fetched remote MCP tools."""
    global _cached_remote_tools
    
    # Start with local tools
    all_tools = list(local_tools_def)
    
    # Fetch remote tools from remote MCP server only once
    if _cached_remote_tools is None:
        _cached_remote_tools = await remote_mcp_client.fetch_remote_tools()
        
    all_tools.extend(_cached_remote_tools)
    
    return all_tools

async def dispatch_tool(name: str, arguments: dict) -> str:
    """Dispatches tool execution to either local handler or remote MCP server."""
    # Check if tool is a local tool
    local_names = [t["function"]["name"] for t in local_tools_def]
    
    if name in local_names:
        print(f"🏠 [Registry] Routing to LOCAL tool: {name}")
        return await execute_local_tool(name, arguments)
    else:
        print(f"🌐 [Registry] Routing to REMOTE MCP tool: {name}")
        return await remote_mcp_client.invoke_remote_tool(name, arguments)
