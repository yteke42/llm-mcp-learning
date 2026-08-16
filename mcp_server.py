from mcp.server.fastmcp import FastMCP


mcp = FastMCP("Technical Publishing Tools")


@mcp.tool()
def calculator(a: float, b: float, operation: str) -> float:
    """
    Perform an arithmetic operation on two numbers.
    """

    if operation == "add":
        return a + b

    if operation == "subtract":
        return a - b

    if operation == "multiply":
        return a * b

    if operation == "divide":
        if b == 0:
            raise ValueError("Cannot divide by zero")

        return a / b

    raise ValueError(f"Unknown operation: {operation}")


@mcp.tool()
def get_text_length(text: str) -> int:
    """
    Return the number of characters in a text.
    """

    return len(text)


if __name__ == "__main__":
    mcp.run()