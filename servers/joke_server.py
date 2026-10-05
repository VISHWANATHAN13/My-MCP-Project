from mcp.server.fastmcp import FastMCP
import requests 
from tools.joke_tool import tell_joke_tool

mcp = FastMCP("Personal_Joke_Server")

@mcp.tool()
def get_joke(name : str) -> str:
    """ Tell a personalized joke """
    
    response = tell_joke_tool(name)
    
    return response

if __name__ == "__main__":
    print("Joke server started")
    mcp.run()