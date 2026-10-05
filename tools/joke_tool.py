import requests
import json

def tell_joke_tool(name : str) -> str:
    
    url = "https://official-joke-api.appspot.com/random_joke"
    
    response = requests.get(url)
    joke = response.json()
    
    return (
        f"Hey {name}! Here's a joke for you:\n\n"
        f"{joke['setup']}\n\n"
        f"{joke['punchline']}"
    )

if __name__ == "__main__":
    tell_joke_tool()