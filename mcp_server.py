"""MCP stdio server exposing find_film to OpenClaw (tools appear as filmfinder__find_film)."""
from mcp.server.mcpserver import MCPServer

from find_film import find_film as _find_film

server = MCPServer("filmfinder")


@server.tool()
def find_film(description: str) -> dict:
    """Identify a film from a half-remembered description. Pass the user's full description;
    on a follow-up, pass the original description plus the user's answer.
    Returns verdict (answer | ask | not_sure | busy), title, year, poster_url,
    matched_clues, mismatched_clues, follow_up_question and timing."""
    return _find_film(description)


if __name__ == "__main__":
    server.run("stdio")
