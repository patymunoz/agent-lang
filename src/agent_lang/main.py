from dotenv import load_dotenv
load_dotenv()

import argparse
from langchain.messages import HumanMessage

from agent_lang.chains.agent import build_personal_chef_agent
from agent_lang.utils.images import image_to_base64

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=str, help="Path to an image (png/jpg) with ingredients")
    parser.add_argument("--text", type=str, help="Ingredients as text, e.g. 'chicken, rice, tomato'")
    parser.add_argument("--thread-id", type=str, default="1")
    args = parser.parse_args()

    agent = build_personal_chef_agent()

    config = {"configurable": {"thread_id": args.thread_id}}

    if args.image:
        img_b64 = image_to_base64(args.image)
        msg = HumanMessage(content=[
            {"type": "text", "text": "Give me a recipe using the ingredients in this image:"},
            {"type": "image", "base64": img_b64, "mime_type": "image/png"},
        ])
    elif args.text:
        msg = HumanMessage(content=f"These are my ingredients: {args.text}. Suggest recipes and instructions.")
    else:
        raise SystemExit("Use --image PATH or --text '...ingredients...'")

    response = agent.invoke({"messages": [msg]}, config=config)
    print(response["messages"][-1].content)

if __name__ == "__main__":
    main()