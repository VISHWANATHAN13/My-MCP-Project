import asyncio
import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


async def main(user_query: str):

    client = MultiServerMCPClient(
        {
            "age": {
                "command": "python",
                "args": ["-m", "servers.age_guess_server"],
                "transport": "stdio",
            },
            "gender": {
                "command": "python",
                "args": ["-m", "servers.gender_guess_server"],
                "transport": "stdio",
            },
            "joke": {
                "command": "python",
                "args": ["-m", "servers.joke_server"],
                "transport": "stdio",
            },
        }
    )

    tools = await client.get_tools()

    print("\nTools discovered:")
    for tool in tools:
        print(f"- {tool.name}")

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=OPENAI_API_KEY,
        temperature=0
    )

    agent = create_agent(
        model=llm,
        tools=tools
    )

    response = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": user_query
                }
            ]
        }
    )

    print("\nFinal Response:\n")

    for message in response["messages"]:
        if hasattr(message, "content") and message.content:
            print(message.content)


if __name__ == "__main__":

    user_query = input(
        "Enter your details to predict your age, gender and tell me a joke: "
    )

    if not user_query.strip():
        user_query = (
            "My name is Vishwanathan. "
            "Guess my age, gender and tell me a joke."
        )

    asyncio.run(main(user_query))