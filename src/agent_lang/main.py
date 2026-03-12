from dotenv import load_dotenv

load_dotenv()

import argparse
import sys

from langchain.messages import HumanMessage
from pydantic import ValidationError

from agent_lang.chains.agent import build_personal_chef_agent
from agent_lang.config import ConfigError, load_config, validate_runtime_config
from agent_lang.utils.images import detect_image_mime_type, image_to_base64


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=str, help="Path to an image (png/jpg/jpeg/webp) with ingredients")
    parser.add_argument("--text", type=str, help="Ingredients as text, e.g. 'chicken, rice, tomato'")
    parser.add_argument("--thread-id", type=str, default="1")
    args = parser.parse_args()

    if args.image and args.text:
        raise SystemExit("Use either --image PATH or --text '...ingredients...', not both.")

    try:
        config = load_config()
        warnings = validate_runtime_config(config)
        for warning in warnings:
            print(f"Warning: {warning}", file=sys.stderr)

        agent = build_personal_chef_agent(
            model_name=config.model_name,
            temperature=config.temperature,
            enable_web_search=config.web_search_enabled,
        )
    except (ConfigError, ValidationError) as exc:
        raise SystemExit(f"Configuration error: {exc}") from exc

    run_config = {"configurable": {"thread_id": args.thread_id}}

    try:
        if args.image:
            img_b64 = image_to_base64(args.image)
            mime_type = detect_image_mime_type(args.image)
            msg = HumanMessage(
                content=[
                    {"type": "text", "text": "Give me a recipe using the ingredients in this image:"},
                    {"type": "image", "base64": img_b64, "mime_type": mime_type},
                ]
            )
        elif args.text:
            msg = HumanMessage(content=f"These are my ingredients: {args.text}. Suggest recipes and instructions.")
        else:
            raise SystemExit("Use --image PATH or --text '...ingredients...'")

        response = agent.invoke({"messages": [msg]}, config=run_config)
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        raise SystemExit(f"Execution error: {exc}") from exc

    print(response["messages"][-1].content)


if __name__ == "__main__":
    main()
