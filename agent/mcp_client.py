import os
import json
import httpx
from typing import List, Dict, Any

CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "mcp_servers.json"))

class RemoteMCPClient:
    """Client for discovering and invoking remote MCP server tools over HTTP endpoints."""
    
    def __init__(self, config_path: str = CONFIG_PATH):
        self.config_path = config_path
        self.client = httpx.AsyncClient(timeout=15.0)

    def load_config(self) -> Dict[str, Any]:
        """Loads mcp_servers.json configuration."""
        if not os.path.exists(self.config_path):
            return {}
        try:
            with open(self.config_path, "r") as f:
                return json.load(f).get("mcpServers", {})
        except Exception as e:
            print(f"⚠️ [Config Error] Failed to read {self.config_path}: {e}")
            return {}

    async def fetch_remote_tools(self) -> List[Dict[str, Any]]:
        """Queries all configured remote MCP servers for their available tool schemas."""
        servers = self.load_config()
        all_formatted_tools = []
        
        req_headers = {"Accept": "application/json, text/event-stream"}

        for server_name, server_info in servers.items():
            url = server_info.get("url", "").rstrip("/")
            headers = {**req_headers, **server_info.get("headers", {})}
            
            if not url:
                continue

            # Try custom REST endpoint first (/mcp/tools)
            try:
                res = await self.client.get(f"{url}/mcp/tools", headers=headers)
                if res.status_code == 200:
                    tools = res.json().get("tools", [])
                    for tool in tools:
                        all_formatted_tools.append({
                            "type": "function",
                            "function": {
                                "name": tool["name"],
                                "description": f"[{server_name.upper()} MCP TOOL] {tool.get('description', '')}",
                                "parameters": tool.get("parameters", tool.get("inputSchema", {}))
                            }
                        })
                    print(f"✅ [MCP Client] Loaded {len(tools)} tools from server '{server_name}' ({url})")
                    continue
            except Exception:
                pass

            # Fallback to standard MCP JSON-RPC protocol over SSE / POST
            try:
                rpc_body = {"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1}
                res = await self.client.post(url, json=rpc_body, headers=headers)
                if res.status_code in (200, 201):
                    raw_text = res.text
                    rpc_data = None
                    if raw_text.startswith("event:") or "data: {" in raw_text:
                        for line in raw_text.splitlines():
                            if line.startswith("data: "):
                                try:
                                    rpc_data = json.loads(line[6:])
                                    break
                                except Exception:
                                    pass
                    else:
                        rpc_data = res.json()

                    if rpc_data:
                        tools = rpc_data.get("result", {}).get("tools", [])
                        for tool in tools:
                            all_formatted_tools.append({
                                "type": "function",
                                "function": {
                                    "name": tool["name"],
                                    "description": f"[{server_name.upper()} MCP TOOL] {tool.get('description', '')}",
                                    "parameters": tool.get("inputSchema", tool.get("parameters", {}))
                                }
                            })
                        print(f"✅ [MCP Client] Loaded {len(tools)} standard MCP tools from '{server_name}' ({url})")
            except Exception as e:
                print(f"⚠️ [MCP Client] Could not connect to '{server_name}' at {url}: {e}")
                
        return all_formatted_tools

    async def invoke_remote_tool(self, tool_name: str, arguments: dict) -> str:
        """Finds the server that owns tool_name and executes it."""
        servers = self.load_config()
        req_headers = {"Accept": "application/json, text/event-stream"}
        
        for server_name, server_info in servers.items():
            url = server_info.get("url", "").rstrip("/")
            headers = {**req_headers, **server_info.get("headers", {})}
            
            if not url:
                continue

            # Check via REST /mcp/tools first
            try:
                tools_res = await self.client.get(f"{url}/mcp/tools", headers=headers)
                if tools_res.status_code == 200:
                    tool_names = [t["name"] for t in tools_res.json().get("tools", [])]
                    if tool_name in tool_names:
                        print(f"🌐 [MCP Client] Invoking '{tool_name}' on '{server_name}' ({url})...")
                        res = await self.client.post(
                            f"{url}/mcp/call",
                            json={"name": tool_name, "arguments": arguments},
                            headers=headers
                        )
                        if res.status_code == 200:
                            data = res.json()
                            if "result" in data:
                                return str(data["result"])
                            elif "error" in data:
                                return f"Remote Tool Error: {data['error']}"
            except Exception:
                pass

            # Fallback to standard MCP JSON-RPC protocol (tools/call)
            try:
                rpc_list = {"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1}
                list_res = await self.client.post(url, json=rpc_list, headers=headers)
                if list_res.status_code in (200, 201):
                    raw_text = list_res.text
                    rpc_data = None
                    if raw_text.startswith("event:") or "data: {" in raw_text:
                        for line in raw_text.splitlines():
                            if line.startswith("data: "):
                                try:
                                    rpc_data = json.loads(line[6:])
                                    break
                                except Exception:
                                    pass
                    else:
                        rpc_data = list_res.json()

                    if rpc_data:
                        tool_names = [t["name"] for t in rpc_data.get("result", {}).get("tools", [])]
                        if tool_name in tool_names:
                            rpc_call = {
                                "jsonrpc": "2.0",
                                "method": "tools/call",
                                "params": {"name": tool_name, "arguments": arguments},
                                "id": 2
                            }
                            res = await self.client.post(url, json=rpc_call, headers=headers)
                            if res.status_code in (200, 201):
                                call_raw = res.text
                                result_data = None
                                if call_raw.startswith("event:") or "data: {" in call_raw:
                                    for line in call_raw.splitlines():
                                        if line.startswith("data: "):
                                            try:
                                                result_data = json.loads(line[6:]).get("result", {})
                                                break
                                            except Exception:
                                                pass
                                else:
                                    result_data = res.json().get("result", {})

                                if result_data:
                                    content = result_data.get("content", [])
                                    if content:
                                        return "\n".join(item.get("text", "") for item in content if item.get("type") == "text")
                                    return json.dumps(result_data)
            except Exception as e:
                print(f"⚠️ [MCP Client Error] Failed invocation on '{server_name}': {e}")

        return f"Error: Tool '{tool_name}' was not found on any configured MCP server."
