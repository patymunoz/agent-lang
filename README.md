## agent-lang

Example "personal chef" agent built with LangChain and LangGraph. It accepts either a text list of ingredients or an image of ingredients, optionally uses Tavily web search, and returns recipe suggestions.

**What’s included**
- CLI entry point `agent-lang`
- Agent setup with LangChain + LangGraph checkpointing
- Tavily web search tool
- Image-to-base64 utility for multimodal input
- Placeholder system prompt file

**Repository layout**
- `src/agent_lang/main.py` CLI entry point
- `src/agent_lang/chains/agent.py` agent construction
- `src/agent_lang/tools/web.py` Tavily search tool
- `src/agent_lang/utils/images.py` image helper
- `src/agent_lang/prompts/system.txt` system prompt (currently empty)

## Requirements
- Python 3.12–3.13
- A model provider API key supported by your LangChain setup
- Tavily API key if you want web search

## Setup
1. Create a virtual environment and install dependencies.
2. Copy `.env.example` to `.env` and add your keys.

Example with `uv`:
```bash
uv venv
uv pip install -r pyproject.toml
```

Example with `pip`:
```bash
python -m venv .venv
./.venv/Scripts/activate
pip install -e .
```

## Environment variables
Populate `.env` with the keys your chosen model/tooling needs. Typical entries include:
- `OPENAI_API_KEY` (if using OpenAI models)
- `TAVILY_API_KEY` (for `web_search` tool)

## Usage
Text ingredients:
```bash
agent-lang --text "chicken, rice, tomato"
```

Image ingredients:
```bash
agent-lang --image "path/to/ingredients.png"
```

Optional thread ID (LangGraph checkpoint key):
```bash
agent-lang --text "eggs, cheese" --thread-id 2
```

## Configuration
The system prompt is loaded from:
- `src/agent_lang/prompts/system.txt`

You can customize behavior by editing that prompt or adjusting the model name and temperature in:
- `src/agent_lang/chains/agent.py`

## Development
Install in editable mode and run the CLI locally:
```bash
pip install -e .
agent-lang --text "beans, onion, garlic"
```

## Tests
If you add tests in `src/tests`, run them with your test runner of choice. There are no test commands wired in yet.

## Troubleshooting
- If the app exits complaining about missing inputs, provide `--image` or `--text`.
- If model calls fail, confirm your API key is set in `.env`.
- If web search fails, confirm `TAVILY_API_KEY` is set.
