import json
import urllib.request

from mcp_client import MCPClient


OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen3:8b"


# ============================================================
# LLM
# ============================================================

def call_llm(messages, tools):

    data = {
        "model": MODEL,
        "messages": messages,
        "tools": tools,
        "stream": False
    }

    print("\n")
    print("=" * 70)
    print("LLM REQUEST")
    print("=" * 70)

    print("\nMessages:")
    print(json.dumps(
        messages,
        indent=2,
        ensure_ascii=False
    ))

    print("\nTools given to LLM:")
    print(json.dumps(
        tools,
        indent=2,
        ensure_ascii=False
    ))

    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(data).encode("utf-8"),
        headers={
            "Content-Type": "application/json"
        }
    )

    with urllib.request.urlopen(request) as response:

        result = json.loads(
            response.read()
        )

    print("\n")
    print("=" * 70)
    print("LLM RAW RESPONSE")
    print("=" * 70)

    print(json.dumps(
        result,
        indent=2,
        ensure_ascii=False
    ))

    return result


# ============================================================
# MCP TOOL -> LLM TOOL
# ============================================================

def convert_mcp_tools_to_llm_tools(mcp_tools):

    tools = []

    print("\n")
    print("=" * 70)
    print("MCP -> LLM TOOL CONVERSION")
    print("=" * 70)

    for tool in mcp_tools:

        print(f"\nMCP TOOL FOUND: {tool.name}")

        print("\nMCP TOOL SCHEMA:")
        print(json.dumps(
            tool.inputSchema,
            indent=2,
            ensure_ascii=False
        ))

        llm_tool = {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema
            }
        }

        tools.append(llm_tool)

        print("\nLLM TOOL REPRESENTATION:")
        print(json.dumps(
            llm_tool,
            indent=2,
            ensure_ascii=False
        ))

    return tools


# ============================================================
# MCP RESULT -> STRING
# ============================================================

def extract_tool_result(result):

    print("\n")
    print("=" * 70)
    print("RAW MCP TOOL RESULT")
    print("=" * 70)

    print(result)

    if not result.content:
        return ""

    parts = []

    for item in result.content:

        if hasattr(item, "text"):
            parts.append(item.text)

        else:
            parts.append(str(item))

    return "\n".join(parts)


# ============================================================
# AGENT
# ============================================================

async def run_agent(user_input: str):

    print("\n")
    print("=" * 70)
    print("AGENT START")
    print("=" * 70)

    print("\nUser input:")
    print(user_input)

    # --------------------------------------------------------
    # MCP CLIENT
    # --------------------------------------------------------

    print("\n")
    print("-" * 70)
    print("CONNECTING TO MCP SERVER")
    print("-" * 70)

    mcp = MCPClient("mcp_server.py")

    await mcp.connect()

    print("MCP connection established.")

    try:

        # ----------------------------------------------------
        # DISCOVER MCP TOOLS
        # ----------------------------------------------------

        print("\n")
        print("-" * 70)
        print("DISCOVERING MCP TOOLS")
        print("-" * 70)

        mcp_tools = await mcp.list_tools()

        print("\nMCP tools discovered:")

        for tool in mcp_tools:
            print(f"  - {tool.name}")

        # ----------------------------------------------------
        # CONVERT TO LLM FORMAT
        # ----------------------------------------------------

        llm_tools = convert_mcp_tools_to_llm_tools(
            mcp_tools
        )

        # ----------------------------------------------------
        # INITIAL MESSAGE HISTORY
        # ----------------------------------------------------

        messages = [
            {
                "role": "user",
                "content": user_input
            }
        ]

        iteration = 0

        # ====================================================
        # AGENT LOOP
        # ====================================================

        while True:

            iteration += 1

            print("\n")
            print("#" * 70)
            print(f"AGENT LOOP ITERATION #{iteration}")
            print("#" * 70)

            # ------------------------------------------------
            # SEND EVERYTHING TO LLM
            # ------------------------------------------------

            result = call_llm(
                messages,
                llm_tools
            )

            assistant_message = result["message"]

            # ------------------------------------------------
            # SHOW THINKING IF AVAILABLE
            # ------------------------------------------------

            if "thinking" in assistant_message:

                print("\n")
                print("=" * 70)
                print("MODEL PUBLISHED THINKING / REASONING")
                print("=" * 70)

                print(
                    assistant_message["thinking"]
                )

            # ------------------------------------------------
            # SHOW ASSISTANT CONTENT
            # ------------------------------------------------

            print("\n")
            print("=" * 70)
            print("ASSISTANT MESSAGE")
            print("=" * 70)

            print(
                assistant_message.get(
                    "content",
                    ""
                )
            )

            # ------------------------------------------------
            # ADD ASSISTANT MESSAGE TO HISTORY
            # ------------------------------------------------

            messages.append(
                assistant_message
            )

            print("\n")
            print("-" * 70)
            print("MESSAGE HISTORY AFTER ASSISTANT RESPONSE")
            print("-" * 70)

            print(json.dumps(
                messages,
                indent=2,
                ensure_ascii=False
            ))

            # ------------------------------------------------
            # DOES MODEL WANT A TOOL?
            # ------------------------------------------------

            tool_calls = assistant_message.get(
                "tool_calls"
            )

            if not tool_calls:

                print("\n")
                print("=" * 70)
                print("NO TOOL CALL")
                print("=" * 70)

                print("\nAgent finished.")

                return assistant_message.get(
                    "content",
                    ""
                )

            # ------------------------------------------------
            # MODEL REQUESTED TOOL(S)
            # ------------------------------------------------

            print("\n")
            print("=" * 70)
            print(
                f"MODEL REQUESTED {len(tool_calls)} TOOL CALL(S)"
            )
            print("=" * 70)

            # =================================================
            # PROCESS EACH TOOL CALL
            # =================================================

            for index, tool_call in enumerate(
                tool_calls,
                start=1
            ):

                print("\n")
                print("-" * 70)
                print(f"TOOL CALL #{index}")
                print("-" * 70)

                print("\nRaw tool call:")
                print(json.dumps(
                    tool_call,
                    indent=2,
                    ensure_ascii=False
                ))

                function = tool_call["function"]

                tool_name = function["name"]

                arguments = function["arguments"]

                print("\nTool name:")
                print(tool_name)

                print("\nTool arguments:")
                print(json.dumps(
                    arguments,
                    indent=2,
                    ensure_ascii=False
                ))

                # ------------------------------------------------
                # CALL MCP
                # ------------------------------------------------

                print("\n")
                print("=" * 70)
                print("MCP REQUEST")
                print("=" * 70)

                print("\nCalling MCP tool:")
                print(tool_name)

                print("\nArguments:")
                print(json.dumps(
                    arguments,
                    indent=2,
                    ensure_ascii=False
                ))

                tool_result = await mcp.call_tool(
                    tool_name,
                    arguments
                )

                # ------------------------------------------------
                # MCP RESULT
                # ------------------------------------------------

                result_text = extract_tool_result(
                    tool_result
                )

                print("\n")
                print("=" * 70)
                print("MCP RESULT SENT BACK TO AGENT")
                print("=" * 70)

                print(result_text)

                # ------------------------------------------------
                # ADD TOOL RESULT TO MESSAGE HISTORY
                # ------------------------------------------------

                messages.append({
                    "role": "tool",
                    "content": result_text
                })

                print("\n")
                print("-" * 70)
                print("MESSAGE HISTORY AFTER TOOL RESULT")
                print("-" * 70)

                print(json.dumps(
                    messages,
                    indent=2,
                    ensure_ascii=False
                ))

            # ------------------------------------------------
            # LOOP STARTS AGAIN
            # ------------------------------------------------

            print("\n")
            print("=" * 70)
            print("TOOL PROCESSING FINISHED")
            print("=" * 70)

            print(
                "Sending updated conversation back to LLM..."
            )

    finally:

        print("\n")
        print("-" * 70)
        print("CLOSING MCP CONNECTION")
        print("-" * 70)

        await mcp.close()

        print("MCP connection closed.")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    import asyncio

    user_input = input(
        "You: "
    )

    answer = asyncio.run(
        run_agent(user_input)
    )

    print("\n")
    print("=" * 70)
    print("FINAL ANSWER")
    print("=" * 70)

    print(answer)