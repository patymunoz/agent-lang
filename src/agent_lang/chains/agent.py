from pathlib import Path
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent

from agent_lang.config import load_config
from agent_lang.tools.web import web_search


DEFAULT_SYSTEM_PROMPT = (
    "You are a practical personal chef assistant. "
    "Use available ingredients and constraints from the user. "
    "When information is uncertain, use tools and explain assumptions briefly. "
    "Prioritize safe cooking guidance and clear step-by-step recipes."
)


def load_system_prompt() -> str:
    prompt_path = Path(__file__).resolve().parents[1] / "prompts" / "system.txt"
    try:
        prompt_text = prompt_path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise RuntimeError(f"Could not read system prompt file at {prompt_path}: {exc}") from exc
    return prompt_text or DEFAULT_SYSTEM_PROMPT


def build_personal_chef_agent(
    model_name: str | None = None,
    temperature: float | None = None,
    enable_web_search: bool | None = None,
):
    config = load_config()
    resolved_model = model_name or config.model_name
    resolved_temperature = config.temperature if temperature is None else temperature
    resolved_web_search = config.web_search_enabled if enable_web_search is None else enable_web_search

    model = init_chat_model(model=resolved_model, temperature=resolved_temperature)
    system_prompt = load_system_prompt()
    tools = [web_search] if resolved_web_search else []

    agent = create_agent(
        model=model,
        checkpointer=InMemorySaver(),
        tools=tools,
        system_prompt=system_prompt,
    )
    return agent
