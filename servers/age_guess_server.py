from mcp.server.fastmcp import FastMCP
from tools.age_guess_tool import guess_age_tool

mcp = FastMCP("Age_Guessing_Server")

@mcp.tool()
def age_guess(name : str) -> dict:
    
    """Guess the age by the user's name"""
    
    response = guess_age_tool(name)
    
    return response['predicted_age']

if __name__ == "__main__":
    print("Age server started")
    mcp.run()