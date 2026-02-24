from pathlib import Path
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent

from agent_lang.tools.web import web_search

def load_system_prompt() -> str:
    prompt_path = Path(__file__).resolve().parents[1] / "prompts" / "system.txt"
    return prompt_path.read_text(encoding="utf-8")

def build_personal_chef_agent(model_name: str = "gpt-5-nano", temperature: float = 0.7):
    model = init_chat_model(model=model_name, temperature=temperature)
    system_prompt = load_system_prompt()

    agent = create_agent(
        model=model,
        checkpointer=InMemorySaver(),
        tools=[web_search],
        system_prompt=system_prompt,
    )
    return agent