from mcp.server.fastmcp import FastMCP
from tools.gender_guess_tool import guess_gender_tool

mcp = FastMCP("Gender_Guess_Server")

@mcp.tool()
def guess_gender(name : str) -> str:
    
    """predicts the gender by using our name"""
    
    response =  guess_gender_tool(name)
    
    return response

if __name__ == "__main__":
    print("Gender server started")
    mcp.run()