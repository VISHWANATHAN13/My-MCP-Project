# MyMCP

A hands-on **Model Context Protocol (MCP)** playground: three small MCP servers, each
wrapping a public REST API, driven by a single LangChain agent that discovers their tools
at runtime and decides which ones to call.

Give it a sentence like *"My name is Vishwanathan. Guess my age, gender and tell me a
joke."* and the agent fans the request out across all three servers and stitches the
answers back together.

---

## What it demonstrates

- **Writing MCP servers** with `FastMCP` — turning a plain Python function into a
  discoverable tool with a docstring as its description.
- **Running multiple MCP servers at once** over `stdio` transport, each as its own
  subprocess.
- **Consuming MCP tools from LangChain** via `langchain-mcp-adapters`, so an LLM agent
  can plan and call them without any hard-coded routing logic.
- **Separating transport from logic** — the MCP server layer (`servers/`) stays thin and
  the actual API calls live in ordinary, independently testable functions (`tools/`).

---

## Architecture

```
                 ┌──────────────────────────────┐
  user query ───▶│  app/mcp_client.py           │
                 │  ChatOpenAI + create_agent   │
                 │  MultiServerMCPClient        │
                 └───────┬──────┬──────┬────────┘
                         │ stdio│      │
         ┌───────────────┘      │      └───────────────┐
         ▼                      ▼                      ▼
┌──────────────────┐  ┌────────────────────┐  ┌────────────────────┐
│ age_guess_server │  │ gender_guess_server│  │   joke_server      │
│  tool: age_guess │  │ tool: guess_gender │  │   tool: get_joke   │
└────────┬─────────┘  └─────────┬──────────┘  └─────────┬──────────┘
         ▼                      ▼                       ▼
┌──────────────────┐  ┌────────────────────┐  ┌────────────────────┐
│  agify.io        │  │  genderize.io      │  │ official-joke-api  │
└──────────────────┘  └────────────────────┘  └────────────────────┘
```

The client never imports the servers. It launches them as `python -m servers.<name>`
subprocesses, asks each one what tools it offers, and hands the combined list to the
agent — exactly how an MCP host (Claude Desktop, an IDE, a custom app) would.

### Layout

| Path | Role |
|---|---|
| `app/mcp_client.py` | MCP host + LangChain agent. The entry point you run. |
| `servers/age_guess_server.py` | MCP server `Age_Guessing_Server`, exposes `age_guess`. |
| `servers/gender_guess_server.py` | MCP server `Gender_Guess_Server`, exposes `guess_gender`. |
| `servers/joke_server.py` | MCP server `Personal_Joke_Server`, exposes `get_joke`. |
| `tools/age_guess_tool.py` | Calls `api.agify.io`, returns name / predicted age / sample size. |
| `tools/gender_guess_tool.py` | Calls `api.genderize.io`, returns gender + confidence. |
| `tools/joke_tool.py` | Calls `official-joke-api.appspot.com`, returns a personalised joke. |
| `api_urls.txt` | The upstream API endpoints this project targets. |
| `requirements.txt` | Pinned dependency set. |
| `.mymcp/` | Local virtual environment (Python 3.13.7). |

---

## Requirements

- Python **3.13** (the checked-in venv was built with 3.13.7)
- An **OpenAI API key**
- Outbound network access to the three public APIs

Key dependencies: `mcp` 1.30.0, `langchain` 1.4.3, `langchain-mcp-adapters` 0.3.2,
`langchain-openai` 1.6.7, `langgraph` 1.2.12, `openai` 3.24.0, `requests`, `python-dotenv`.

---

## Setup

```powershell
# from the project root: C:\data\MyMCP
python -m venv .mymcp
.\.mymcp\Scripts\Activate.ps1
pip install -r requirements.txt
```

Then create a `.env` file in the project root:

```
OPENAI_API_KEY=sk-your-key-here
```

> `requirements.txt` is currently UTF-16 encoded (a side effect of
> `pip freeze > requirements.txt` in PowerShell). If `pip install -r` chokes on it,
> regenerate it as UTF-8 with
> `pip freeze | Out-File -Encoding utf8 requirements.txt`.

---

## Running it

```powershell
python -m app.mcp_client
```

You'll be prompted for a query. Press Enter to accept the built-in default.

```
Enter your details to predict your age, gender and tell me a joke: My name is Priya. How old am I, and tell me a joke.

Tools discovered:
- age_guess
- guess_gender
- get_joke

Final Response:

My name is Priya. How old am I, and tell me a joke.
...
Based on your name, you're likely around 32. Here's a joke for you: ...
```

**Run from the project root.** The servers import `tools.*`, so the root must be on
`sys.path` — which is why the client launches them with `-m` rather than by file path.

### Running a single server by hand

Useful when debugging one tool in isolation, or when registering it with another MCP
host such as Claude Desktop:

```powershell
python -m servers.joke_server
```

It will sit waiting on stdin for MCP protocol messages — that's expected, not a hang.

---

## Extending it: adding a fourth tool

1. **Write the logic** in `tools/my_tool.py` as a plain function. No MCP imports.
2. **Expose it** in `servers/my_server.py`:

   ```python
   from mcp.server.fastmcp import FastMCP
   from tools.my_tool import my_tool

   mcp = FastMCP("My_Server")

   @mcp.tool()
   def my_thing(name: str) -> str:
       """One clear sentence — the LLM uses this to decide when to call the tool."""
       return my_tool(name)

   if __name__ == "__main__":
       mcp.run()
   ```
3. **Register it** in the `MultiServerMCPClient` dict in `app/mcp_client.py`.

The docstring and type hints are the tool's public contract — the agent sees nothing
else, so make them say exactly what the tool does.

---

## Known rough edges

These are real and worth knowing before you build on the code:

- **TLS verification is disabled** in `tools/age_guess_tool.py` (`verify=False`, plus a
  suppressed `InsecureRequestWarning`). It's a corporate-proxy workaround, but it means
  that one call is not protected against interception. Remove it, or point `REQUESTS_CA_BUNDLE`
  at your proxy's CA certificate, before this goes anywhere near production.
- **`age_guess` return type is mis-annotated.** The server declares `-> dict` but returns
  `response['predicted_age']`, an `int`. Harmless today, but the schema the agent sees is
  wrong.
- **No error handling on the HTTP calls.** A rate limit, a timeout, or an unknown name
  (agify returns `age: null`) will surface as a raw exception or a `None`, not a graceful
  message.
- **`servers/joke_server.py` imports `requests`** without using it — the HTTP call lives
  in the tool module.
- **`.env` holds a live secret** and there is no `.gitignore` at the project root. Add one
  that excludes `.env`, `.mymcp/`, and `__pycache__/` before initialising a repository here.

---

## Why MCP for this?

Three simple APIs don't need a protocol. But the shape of the project is the point: each
capability is a standalone process with a self-describing interface, so the same servers
can be plugged into *any* MCP host without changing a line — and the agent gains new
abilities by configuration rather than by code.
