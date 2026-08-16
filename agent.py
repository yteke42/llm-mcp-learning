import json
import urllib.request

from mcp_client import MCPClient


OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen3:8b"


def call_llm(messages, tools):

    data = {
        "model": MODEL,
        "messages": messages,
        "tools": tools,
        "stream": False
    }

    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(data).encode("utf-8"),
        headers={
            "Content-Type": "application/json"
        }
    )

    with urllib.request.urlopen(request) as response:
        return json.loads(response.read())


def convert_mcp_tools_to_llm_tools(mcp_tools):

    tools = []

    for tool in mcp_tools:

        tools.append({
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema
            }
        })

    return tools


def extract_tool_result(result):

    """
    Convert MCP CallToolResult into a string
    that can be sent back to the LLM.
    """

    if not result.content:
        return ""

    parts = []

    for item in result.content:

        if hasattr(item, "text"):
            parts.append(item.text)

        else:
            parts.append(str(item))

    return "\n".join(parts)


async def run_agent(user_input: str):

    mcp = MCPClient("mcp_server.py")

    await mcp.connect()

    try:

        # ------------------------------------------------
        # Discover MCP tools
        # ------------------------------------------------

        mcp_tools = await mcp.list_tools()

        llm_tools = (
            convert_mcp_tools_to_llm_tools(
                mcp_tools
            )
        )

        # ------------------------------------------------
        # Conversation
        # ------------------------------------------------

        messages = [
            {
                "role": "user",
                "content": user_input
            }
        ]

        # ------------------------------------------------
        # Agent loop
        # ------------------------------------------------

        while True:

            result = call_llm(
                messages,
                llm_tools
            )

            assistant_message = result["message"]

            messages.append(
                assistant_message
            )

            # --------------------------------------------
            # No tool call
            # --------------------------------------------

            if "tool_calls" not in assistant_message:

                return assistant_message["content"]

            # --------------------------------------------
            # Tool calls
            # --------------------------------------------

            for tool_call in assistant_message["tool_calls"]:

                function = tool_call["function"]

                tool_name = function["name"]

                arguments = function["arguments"]

                print(
                    f"\n[Agent] Tool requested: "
                    f"{tool_name}"
                )

                print(
                    f"[Agent] Arguments: "
                    f"{arguments}"
                )

                # ----------------------------------------
                # MCP
                # ----------------------------------------

                tool_result = await mcp.call_tool(
                    tool_name,
                    arguments
                )

                result_text = extract_tool_result(
                    tool_result
                )

                print(
                    f"[Agent] Tool result: "
                    f"{result_text}"
                )

                # ----------------------------------------
                # Send tool result to LLM
                # ----------------------------------------

                messages.append({
                    "role": "tool",
                    "content": result_text
                })

    finally:

        await mcp.close()