import json
import sqlite3
import os
import uuid

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "project", "sqlite.db"))

tools_definition = [
    {
        "type": "function",
        "function": {
            "name": "search_company_knowledge",
            "description": "Searches the internal company knowledge base for information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to look up in the company database."
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_report",
            "description": "Generates a structured report from data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "string",
                        "description": "The data to compile into a report."
                    }
                },
                "required": ["data"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_note_to_knowledge_base",
            "description": "Saves a new note, policy, decision, or piece of knowledge directly into the company database so it can be retrieved later.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Short title or category for the note (e.g. 'Project Alpha Update', 'New Refund Policy')."
                    },
                    "content": {
                        "type": "string",
                        "description": "The full text/information to save into the database."
                    }
                },
                "required": ["title", "content"]
            }
        }
    }
]

async def execute_tool(name: str, arguments: dict) -> str:
    print(f"Executing tool {name} with args {arguments}")
    if name == "search_company_knowledge":
        query = arguments.get("query", "")
        # Query SQLite database for any chunks matching the query term
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('SELECT filePath, content FROM "Chunk" WHERE content LIKE ? LIMIT 5', (f"%{query}%",))
            rows = cursor.fetchall()
            conn.close()
            if rows:
                results = [f"[File: {r[0]}]\n{r[1]}" for r in rows]
                return "\n\n---\n\n".join(results)
            else:
                return f"No exact matches found for '{query}' in uploaded documents."
        except Exception as e:
            return f"Database search error: {str(e)}"
            
    elif name == "generate_report":
        data = arguments.get("data", "")
        return f"REPORT SAVED SUCCESSFULLY.\n# Executive Summary\n{data}"
        
    elif name == "save_note_to_knowledge_base":
        title = arguments.get("title", "Saved Note")
        content = arguments.get("content", "")
        note_id = f"note/{uuid.uuid4().hex[:8]}"
        file_path = f"notes/{title.replace(' ', '_')}.txt"
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO "Chunk" (id, filePath, content, embedding) VALUES (?, ?, ?, ?)',
                (note_id, file_path, f"Title: {title}\nContent: {content}", "[]")
            )
            conn.commit()
            conn.close()
            return f"Successfully saved note '{title}' into the database (ID: {note_id}, Path: {file_path})."
        except Exception as e:
            return f"Failed to save note to database: {str(e)}"
            
    return "Error: Tool not found."
