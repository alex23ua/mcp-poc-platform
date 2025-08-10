from fastmcp import FastMCP

mcp = FastMCP("My HTTP Server")


@mcp.tool(description="Greet a person by name")
def greet(name: str) -> str:
    return f"Hello, {name}!"


@mcp.tool(description="add two numbers and return the result")
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8000)
    #mcp.run(transport="http", host="0.0.0.0", port=8000, path="/mcp")
