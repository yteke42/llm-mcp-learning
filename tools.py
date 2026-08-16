def calculator(a: float, b: float, operation: str):

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


TOOLS = {
    "calculator": calculator
}