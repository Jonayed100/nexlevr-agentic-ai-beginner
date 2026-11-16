# My First Tool-Using AI

A small Python script where an AI model answers price questions by calling
one function, `get_product_price`, which reads a local file (`products.json`).

Built as Task 1 of the Beginner track of the NEXLEVR Agentic AI Developer
internship.

## What it does

Ask: *"How much is the wireless mouse?"*

The model cannot know the shop's prices. Instead of guessing, it asks the
script to run `get_product_price("Wireless Mouse")`, reads the result, and
answers with the real price from the file.

## Files

| File | Purpose |
|------|---------|
| `agent.py` | The tool, the tool description and the tool-use loop |
| `products.json` | The local price list the tool reads |

No packages to install. The script uses only the Python standard library
(Python 3.9+).

## How to run

The script works with any OpenAI-compatible chat API that supports tool
calling. You need three values from your provider:

| Variable | Meaning |
|----------|---------|
| `LLM_API_KEY` | Your API key |
| `LLM_BASE_URL` | The provider's OpenAI-compatible URL (default: Groq's, `https://api.groq.com/openai/v1`) |
| `LLM_MODEL` | A model name from the provider's model list that supports tool calling |

Windows (PowerShell):

```powershell
$env:LLM_API_KEY = "your-key"
$env:LLM_MODEL = "model-name-from-your-provider"
python agent.py "How much is the wireless mouse?"
```

macOS / Linux:

```bash
export LLM_API_KEY="your-key"
export LLM_MODEL="model-name-from-your-provider"
python agent.py "How much is the wireless mouse?"
```

## Example output

The numbered lines come from the script. The wording of the final answer
depends on the model.

```
[1] User asks: How much is the wireless mouse?
[2] Model requests tool: get_product_price({'product_name': 'Wireless Mouse'})
[3] Tool returns: {'found': True, 'name': 'Wireless Mouse', 'price': 850, 'currency': 'BDT', 'in_stock': True}
[4] Sending tool result back to the model (turn 1)
[5] Final answer: The Wireless Mouse costs 850 BDT and is in stock.
```

## The tool-use loop, step by step

The key idea: **the model never runs code.** It only writes a request saying
which function it wants and with which arguments. The script runs the
function and reports the result back.

```
User question ──> Model ──> "call get_product_price" ──> Script runs it
                    ^                                         │
                    └────────────── tool result ──────────────┘
                    │
                    └──> Final answer
```

**Step 1 - Write the tool.**
`get_product_price(product_name)` is an ordinary Python function. It opens
`products.json`, finds the product (ignoring upper/lower case) and returns a
dictionary. If the product is missing, it returns the list of available
products so the model can give a helpful reply.

**Step 2 - Describe the tool to the model.**
The `TOOLS` list holds a JSON description: the tool's name, what it does,
and its parameters. The model never sees the Python code, so this
description is how it decides when and how to use the tool.

**Step 3 - Start the conversation.**
`messages` begins with a system prompt ("always use the tool, never guess a
price") and the user's question.

**Step 4 - Call the model.**
`call_model` sends the messages and the tool description to the API.

**Step 5 - The model replies with a tool call, not text.**
The reply contains `tool_calls`: the function name, the arguments as a JSON
string, and an `id`. The script adds this reply to `messages` so the
conversation history stays complete.

**Step 6 - The script runs the function.**
The name is looked up in `AVAILABLE_TOOLS`, the JSON arguments are parsed,
and the real Python function runs. Unknown tool names and bad arguments are
returned as an error message instead of crashing.

**Step 7 - Send the result back.**
The result is added as a message with `role: "tool"` and the same
`tool_call_id`, so the model knows which request it answers.

**Step 8 - The model writes the final answer.**
The loop calls the model again. This time it has the real price, so it
replies with plain text and no tool call. That ends the loop.

A `MAX_TURNS` limit of 5 stops the loop if a model keeps calling tools
without ever answering.

## What I learned

- A tool is a function plus a description; the description matters as much
  as the code.
- The model decides *when* to call a tool; the program decides *whether and
  how* to run it. That split is where safety checks belong.
- Returning useful errors (such as the list of available products) lets the
  model recover instead of failing.

## Things to try

- Ask for a product that does not exist: `python agent.py "Price of a gaming chair?"`
- Ask about two products in one question.
- Add a second tool, such as `list_products`.
