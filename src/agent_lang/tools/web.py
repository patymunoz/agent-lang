import os
from functools import lru_cache
from typing import Any, Dict

from langchain.tools import tool
from tavily import TavilyClient


@lru_cache(maxsize=1)
def _get_tavily_client() -> TavilyClient:
    api_key = os.getenv("TAVILY_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("TAVILY_API_KEY is not set. Set it in your environment or .env file.")
    return TavilyClient(api_key=api_key)


@tool
def web_search(query: str) -> Dict[str, Any]:
    """Search the web for information using Tavily."""
    cleaned_query = query.strip()
    if not cleaned_query:
        return {"error": "web_search requires a non-empty query."}

    try:
        return _get_tavily_client().search(cleaned_query)
    except Exception as exc:
        return {"error": f"Web search failed: {type(exc).__name__}: {exc}"}
