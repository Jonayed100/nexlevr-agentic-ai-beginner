"""
Task 1 - Your first tool-using AI
---------------------------------
An AI model answers a price question by calling ONE function
(get_product_price) that reads a local file (products.json).

The script uses only the Python standard library and talks to any
OpenAI-compatible chat API (Groq, Google Gemini, OpenAI, Ollama...).

Run:
    python agent.py "How much is the wireless mouse?"
"""

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

# ---------------------------------------------------------------------------
# Settings (read from environment variables, so no secret lives in the code)
# ---------------------------------------------------------------------------
API_KEY = os.environ.get("LLM_API_KEY", "")
BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.groq.com/openai/v1").rstrip("/")
MODEL = os.environ.get("LLM_MODEL", "")

PRODUCTS_FILE = Path(__file__).parent / "products.json"
MAX_TURNS = 5  # safety limit so the loop can never run forever


# ---------------------------------------------------------------------------
# STEP 1 - The tool: a normal Python function the model is allowed to use
# ---------------------------------------------------------------------------
def get_product_price(product_name: str) -> dict:
    """Look up one product in products.json and return its price."""
    data = json.loads(PRODUCTS_FILE.read_text(encoding="utf-8"))
    wanted = product_name.strip().lower()

    for product in data["products"]:
        if product["name"].lower() == wanted:
            return {
                "found": True,
                "name": product["name"],
                "price": product["price"],
                "currency": data["currency"],
                "in_stock": product["in_stock"],
            }

    # Not found: tell the model what IS available so it can recover.
    return {
        "found": False,
        "requested": product_name,
        "available_products": [p["name"] for p in data["products"]],
    }


# Maps the tool name the model uses to the real Python function.
AVAILABLE_TOOLS = {"get_product_price": get_product_price}

# ---------------------------------------------------------------------------
# STEP 2 - The tool description: this is all the model knows about the tool.
# It never sees the Python code, only this name, description and parameters.
# ---------------------------------------------------------------------------
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_product_price",
            "description": (
                "Get the current price and stock status of a product "
                "from the shop's price list."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "Product name, e.g. 'Wireless Mouse'",
                    }
                },
                "required": ["product_name"],
            },
        },
    }
]

SYSTEM_PROMPT = (
    "You are a shop assistant. Always use the get_product_price tool to "
    "look up prices. Never guess a price. If a product is not found, say "
    "so and list the products that are available."
)


# ---------------------------------------------------------------------------
# Helper - send the conversation to the model and return its reply message
# ---------------------------------------------------------------------------
def call_model(messages: list) -> dict:
    body = json.dumps({"model": MODEL, "messages": messages, "tools": TOOLS})
    request = urllib.request.Request(
        f"{BASE_URL}/chat/completions",
        data=body.encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
            "User-Agent": "first-tool-agent/1.0",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            reply = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")
        sys.exit(f"API error {error.code}: {details}")
    except urllib.error.URLError as error:
        sys.exit(f"Could not reach {BASE_URL}: {error.reason}")
    return reply["choices"][0]["message"]


# ---------------------------------------------------------------------------
# The tool-use loop
# ---------------------------------------------------------------------------
def run_agent(question: str) -> str:
    # STEP 3 - Start the conversation with the user's question.
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    print(f"[1] User asks: {question}")

    for turn in range(1, MAX_TURNS + 1):
        # STEP 4 - Send the conversation + tool description to the model.
        message = call_model(messages)
        tool_calls = message.get("tool_calls") or []

        # STEP 8 - No tool call means the model wrote its final answer.
        if not tool_calls:
            answer = message.get("content") or ""
            print(f"[5] Final answer: {answer}")
            return answer

        # STEP 5 - The model asked for a tool. Keep its request in history.
        messages.append(message)

        for call in tool_calls:
            name = call["function"]["name"]
            try:
                arguments = json.loads(call["function"]["arguments"] or "{}")
            except json.JSONDecodeError:
                arguments = {}
            print(f"[2] Model requests tool: {name}({arguments})")

            # STEP 6 - WE run the function. The model cannot run code itself.
            function = AVAILABLE_TOOLS.get(name)
            if function is None:
                result = {"error": f"Unknown tool: {name}"}
            else:
                try:
                    result = function(**arguments)
                except TypeError as error:
                    result = {"error": f"Bad arguments: {error}"}
            print(f"[3] Tool returns: {result}")

            # STEP 7 - Send the result back, linked to the request by its id.
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call["id"],
                    "content": json.dumps(result),
                }
            )
        print(f"[4] Sending tool result back to the model (turn {turn})")

    return "Stopped: the model kept calling tools without answering."


if __name__ == "__main__":
    if not API_KEY or not MODEL:
        sys.exit(
            "Set LLM_API_KEY and LLM_MODEL first (see README.md, 'How to run')."
        )
    user_question = " ".join(sys.argv[1:]) or "How much is the wireless mouse?"
    run_agent(user_question)
