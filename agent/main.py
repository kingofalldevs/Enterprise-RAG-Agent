import os
import json
from fastapi import FastAPI, Request
from sse_starlette.sse import EventSourceResponse
from typing import AsyncGenerator
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

from registry import get_all_tools, dispatch_tool

SYSTEM_PROMPT = """You are Nexus, an autonomous Enterprise RAG Agent.
You have access to internal company knowledge, local database tools, and remote MCP microservices.
Rules:
1. When asked to save a note, decision, policy, or memory, call the `save_note_to_knowledge_base` tool.
2. When asked to search or lookup info, use `search_company_knowledge`.
3. When asked for weather, employee directory info, or external data, use the appropriate remote MCP tool.
4. Be professional, clear, and direct.
"""

# DeepSeek uses an OpenAI-compatible API format with custom base_url
client = AsyncOpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY", "dummy"),
    base_url="https://api.deepseek.com"
)

async def openai_stream(messages: list) -> AsyncGenerator[bytes, None]:
    formatted_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + [
        {"role": m.get("role", "user"), "content": m.get("content", "")} for m in messages
    ]
    
    # Dynamically discover all tools (local + remote MCP)
    current_tools = await get_all_tools()
    
    while True:
        response = await client.chat.completions.create(
            model="deepseek-chat",
            messages=formatted_messages,
            tools=current_tools if current_tools else None,
            stream=True,
        )
        
        tool_calls_acc = {}
        
        async for chunk in response:
            delta = chunk.choices[0].delta if chunk.choices else None
            delta_content = delta.content if delta and delta.content else ""
            finish_reason = chunk.choices[0].finish_reason if chunk.choices else None
            
            if delta and delta.tool_calls:
                for tc in delta.tool_calls:
                    if tc.index not in tool_calls_acc:
                        tool_calls_acc[tc.index] = {
                            "id": tc.id or f"call_{len(tool_calls_acc)}",
                            "type": "function",
                            "function": {"name": tc.function.name, "arguments": ""}
                        }
                    if tc.function.arguments:
                        tool_calls_acc[tc.index]["function"]["arguments"] += tc.function.arguments
            
            if delta_content:
                data = {
                    "id": chunk.id or "",
                    "object": "chat.completion.chunk",
                    "created": chunk.created or 0,
                    "model": chunk.model or "deepseek-chat",
                    "choices": [{
                        "index": 0,
                        "delta": {
                            "content": delta_content,
                            "toolCalls": [],
                        },
                        "finish_reason": finish_reason,
                    }],
                }
                yield f"data: {json.dumps(data)}\n\n".encode()

        if not tool_calls_acc:
            finish_data = {
                "id": "chatcmpl-finish",
                "object": "chat.completion.chunk",
                "created": 0,
                "model": "deepseek-chat",
                "choices": [{
                    "index": 0,
                    "delta": {"content": "", "toolCalls": []},
                    "finish_reason": "stop",
                }],
            }
            yield f"data: {json.dumps(finish_data)}\n\n".encode()
            break

        # If tools were called, execute them via registry (handles local & remote dispatch)
        tool_list = list(tool_calls_acc.values())
        formatted_messages.append({"role": "assistant", "content": None, "tool_calls": tool_list})
        
        for tc in tool_list:
            t_name = tc["function"]["name"]
            try:
                t_args = json.loads(tc["function"]["arguments"])
            except Exception:
                t_args = tc["function"]["arguments"]
                
            t_args_str = json.dumps(t_args, indent=2) if isinstance(t_args, dict) else str(t_args)

            info_msg_start = (
                f"\n\n<details>\n"
                f"  <summary>⚙️ Tool Call: {t_name}</summary>\n"
                f"  <div class=\"tool-content\">\n"
                f"    <strong>Arguments:</strong>\n"
                f"    <pre>{t_args_str}</pre>\n"
                f"    <em>Executing...</em>\n"
            )
            
            yield f"data: {json.dumps({'id': 'tool-start', 'object': 'chat.completion.chunk', 'created': 0, 'model': 'deepseek-chat', 'choices': [{'index': 0, 'delta': {'content': info_msg_start, 'toolCalls': []}, 'finish_reason': None}]})}\n\n".encode()
            
            tool_res = await dispatch_tool(t_name, t_args if isinstance(t_args, dict) else {})
            
            info_msg_end = (
                f"    <strong>Result:</strong>\n"
                f"    <pre>{tool_res}</pre>\n"
                f"  </div>\n"
                f"</details>\n\n"
            )
            
            yield f"data: {json.dumps({'id': 'tool-end', 'object': 'chat.completion.chunk', 'created': 0, 'model': 'deepseek-chat', 'choices': [{'index': 0, 'delta': {'content': info_msg_end, 'toolCalls': []}, 'finish_reason': None}]})}\n\n".encode()

            formatted_messages.append({
                "tool_call_id": tc["id"],
                "role": "tool",
                "name": t_name,
                "content": tool_res
            })

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    payload = await request.json()
    messages = payload.get("messages", [])
    return EventSourceResponse(openai_stream(messages))

@app.get("/health")
async def health():
    return {"status": "ok"}
