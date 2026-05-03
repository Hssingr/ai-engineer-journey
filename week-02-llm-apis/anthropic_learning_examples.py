"""
╔══════════════════════════════════════════════════════════════════════════════╗
║           CLAUDE API — FROM BEGINNER TO ADVANCED                           ║
║           A complete learning file for AI engineers                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

This file walks you through 8 progressive examples using the Anthropic Claude API.
Each example builds on the previous one. Read the comments carefully — they are
as important as the code itself.

Prerequisites:
    pip install anthropic python-dotenv

Setup:
    Create a .env file at the root of your project:
        ANTHROPIC_API_KEY=sk-ant-...

Author: Your AI Engineer Journey — Week 2
"""

import os
import json
from dotenv import load_dotenv
import anthropic

# Load environment variables from .env file
# This is the correct way to manage API keys — NEVER hardcode them in source code.
load_dotenv()

# Initialize the Anthropic client once and reuse it across all examples.
# The client automatically reads ANTHROPIC_API_KEY from your environment.
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# model: chooses which AI model will answer.
# Keep it configurable so you can change it without editing all examples.
# The model to use. Haiku = fastest & cheapest.
# Other options: claude-sonnet-4-6, claude-opus-4-6
DEFAULT_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")


# -----------------------------------------------------------------------------
# Helper function
# -----------------------------------------------------------------------------

def print_section(title: str) -> None:
    """Small helper to separate examples in the console output."""
    print("\n" + "=" * 90)
    print(title)
    print("=" * 90)


# ─────────────────────────────────────────────────────────────────────────────
# EXAMPLE 1 — Basic Request
# ─────────────────────────────────────────────────────────────────────────────
#
# This is the most minimal call you can make to the Claude API.
# It demonstrates the two required parameters: `model` and `messages`.
# Think of this as your "Hello World" for LLM APIs.
# Every more complex example is just an extension of this pattern.
#
def example_1_basic_request():
    print_section("EXAMPLE 1 — Basic Request")

    response = client.messages.create(
        model=DEFAULT_MODEL,  # The model to use.
        max_tokens=256,  # Required. Maximum number of tokens in the response.
        messages=[
            {
                "role": "user",  # "user" = the human's message
                "content": "What is the capital of France? Answer in one sentence."
            }
        ]
    )

    # The response text lives inside response.content[0].text
    print(response.content[0].text)

    # Example output:
    # "The capital of France is Paris."


# ─────────────────────────────────────────────────────────────────────────────
# EXAMPLE 2 — Adding a System Prompt
# ─────────────────────────────────────────────────────────────────────────────
#
# A system prompt is a set of instructions given to the model BEFORE the user speaks.
# It defines the model's persona, tone, constraints, and behavior.
# The user message is what changes per request; the system prompt is usually fixed.
# This is how you build specialized assistants (customer support bot, code reviewer, etc.)
#
def example_2_system_prompt():
    print_section("EXAMPLE 2 — System Prompt")

    response = client.messages.create(
        model=DEFAULT_MODEL,  # The model to use.
        max_tokens=256,
        system=(  # <-- system: sets the model's behavior globally
            "You are a senior Python engineer. "
            "Answer all questions concisely and with code examples when relevant. "
            "Never explain basic concepts — assume the user is a developer."
        ),
        messages=[
            {
                "role": "user",
                "content": "How do I read a JSON file in Python?"
            }
        ]
    )

    print(response.content[0].text)

    # Example output:
    # with open("data.json") as f:
    #     data = json.load(f)


# ─────────────────────────────────────────────────────────────────────────────
# EXAMPLE 3 — Controlling Output: temperature & max_tokens
# ─────────────────────────────────────────────────────────────────────────────
#
# `temperature` controls how creative (or deterministic) the model is.
#   → 0.0 = always the same output (great for data extraction, classification)
#   → 1.0 = very creative/random (great for storytelling, brainstorming)
# `max_tokens` controls the maximum length of the response.
# Understanding these two levers is essential for production apps.
# Here we run the same prompt with two different temperatures to feel the difference.
#
def example_3_temperature_and_tokens():
    print_section("EXAMPLE 3 — temperature & max_tokens")

    prompt = "Describe the feeling of drinking a morning coffee in 2 sentences."

    for temp in [0.0, 1.0]:
        print(f"\n--- temperature={temp} ---")
        response = client.messages.create(
            model=DEFAULT_MODEL,  # The model to use.
            max_tokens=80,  # Short cap — observe truncation at low values
            temperature=temp,  # 0.0 = deterministic, 1.0 = creative
            messages=[{"role": "user", "content": prompt}]
        )
        print(response.content[0].text)

    # Example output (temperature=0.0):
    # "Drinking morning coffee provides a warm, comforting ritual that gradually
    # awakens the senses and prepares the mind for the day ahead."

    # Example output (temperature=1.0):
    # "There's something almost sacred about that first sip — the steam curling up
    # like a whispered promise, the bitterness cutting through morning fog."


# ─────────────────────────────────────────────────────────────────────────────
# EXAMPLE 4 — Structured Output (JSON)
# ─────────────────────────────────────────────────────────────────────────────
#
# Real applications rarely just display text — they parse model output and
# feed it to databases, UIs, or downstream services.
# To do this reliably, you instruct the model to return valid JSON.
# This is one of the most important patterns in production AI engineering.
# Note: temperature=0 + a strict system prompt = maximum consistency.
#
def example_4_structured_output():
    print_section("EXAMPLE 4 — Structured Output (JSON)")

    response = client.messages.create(
        model=DEFAULT_MODEL,  # The model to use.
        max_tokens=256,
        temperature=0,  # Deterministic — we want consistent structure
        system=(
            "You are a data extraction assistant. "
            "Always respond with valid JSON only. No explanation, no markdown, no backticks. "
            "Use the exact schema the user specifies."
        ),
        messages=[
            {
                "role": "user",
                "content": (
                    "Extract the following info from this sentence and return JSON:\n"
                    "Schema: {name: string, city: string, job: string}\n\n"
                    "Sentence: 'Marie is a data scientist based in Lyon.'"
                )
            }
        ]
    )

    raw = response.content[0].text
    print("Raw response:", raw)

    # Parse and use the structured output
    data = json.loads(raw)
    print("Parsed:", data)
    print(f"Name: {data['name']}, City: {data['city']}, Job: {data['job']}")

    # Example output:
    # Raw response: {"name": "Marie", "city": "Lyon", "job": "data scientist"}
    # Parsed: {'name': 'Marie', 'city': 'Lyon', 'job': 'data scientist'}
    # Name: Marie, City: Lyon, Job: data scientist


# ─────────────────────────────────────────────────────────────────────────────
# EXAMPLE 5 — Multi-turn Conversation
# ─────────────────────────────────────────────────────────────────────────────
#
# LLM APIs are STATELESS — the model has no memory between calls.
# To simulate a conversation, you must send the FULL message history every time.
# This is how ChatGPT, Claude.ai, and every chat interface work under the hood.
# In real apps, you store this history in a database or in-memory session.
#
def example_5_multi_turn_conversation():
    print_section("EXAMPLE 5 — Multi-turn Conversation")

    # This list grows with each turn — it IS the conversation memory
    conversation_history = []

    turns = [
        "My name is Amir and I'm learning to build AI applications.",
        "What should I focus on in my first month?",
        "Can you remind me what my name is?"  # Tests if history is correctly sent
    ]

    for user_input in turns:
        print(f"\nUser: {user_input}")

        # Add the new user message to history
        conversation_history.append({
            "role": "user",
            "content": user_input
        })

        response = client.messages.create(
            model=DEFAULT_MODEL,  # The model to use.
            max_tokens=200,
            system="You are a helpful AI engineering mentor.",
            messages=conversation_history  # Send full history every time
        )

        assistant_reply = response.content[0].text

        # Add assistant response to history so it's included in the next call
        conversation_history.append({
            "role": "assistant",
            "content": assistant_reply
        })

        print(f"Claude: {assistant_reply[:120]}...")

    # Example output (turn 3):
    # User: Can you remind me what my name is?
    # Claude: "Your name is Amir! You mentioned it at the start of our conversation..."


# ─────────────────────────────────────────────────────────────────────────────
# EXAMPLE 6 — Streaming Responses
# ─────────────────────────────────────────────────────────────────────────────
#
# By default, the API waits until the full response is ready before returning it.
# With streaming, you receive tokens as they are generated — word by word.
# This is essential for chat applications where you want the UI to feel responsive.
# Think of every chat interface you've used: the text appearing live IS streaming.
#
def example_6_streaming():
    print_section("EXAMPLE 6 — Streaming Responses")

    # Use stream=True to enter streaming mode
    with client.messages.stream(
            model=DEFAULT_MODEL,  # The model to use.
            max_tokens=150,
            messages=[
                {
                    "role": "user",
                    "content": "Explain what an API is in 3 sentences, simply."
                }
            ]
    ) as stream:
        for text_chunk in stream.text_stream:  # Iterate token by token
            print(text_chunk, end="", flush=True)  # Print each chunk immediately

    print()  # Newline after stream ends

    # Example output (printed live, word by word):
    # Claude: "An API, or Application Programming Interface, is a set of rules that
    # allows different software programs to communicate with each other.
    # Think of it as a waiter in a restaurant — you place an order (a request),
    # and the waiter brings back your food (the response) from the kitchen (another system).
    # APIs are the backbone of modern software integration."


# ─────────────────────────────────────────────────────────────────────────────
# EXAMPLE 7 — Tool / Function Calling
# ─────────────────────────────────────────────────────────────────────────────
#
# Tool calling lets the model trigger real functions in your code.
# The model doesn't execute the function — it decides WHEN to call it and with
# what arguments. YOUR code runs the function and sends the result back.
# Real-world usage: query a database, call an external API, run a calculation,
# look up user data, trigger a workflow.
# This is the foundation of AI agents.
#
def example_7_tool_calling():
    print_section("EXAMPLE 7 — Tool / Function Calling")

    # Step 1: Define the tool schema (what the function does and what params it takes)
    tools = [
        {
            "name": "get_weather",
            "description": (
                "Returns the current weather for a given city. "
                "Call this when the user asks about weather in a specific location."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The name of the city, e.g. 'Paris'"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Temperature unit"
                    }
                },
                "required": ["city"]
            }
        }
    ]

    # Step 2: Send the user's message along with the available tools
    response = client.messages.create(
        model=DEFAULT_MODEL,  # The model to use.
        max_tokens=256,
        tools=tools,  # Tell the model which tools are available
        messages=[
            {"role": "user", "content": "What's the weather like in Tokyo right now?"}
        ]
    )

    print(f"Stop reason: {response.stop_reason}")  # "tool_use" means the model wants to call a tool

    # Step 3: Check if the model decided to call a tool
    if response.stop_reason == "tool_use":
        tool_use_block = next(b for b in response.content if b.type == "tool_use")
        tool_name = tool_use_block.name
        tool_input = tool_use_block.input
        tool_use_id = tool_use_block.id

        print(f"Model wants to call: {tool_name}")
        print(f"With arguments: {tool_input}")

        # Step 4: YOUR code runs the actual function (here we simulate it)
        def get_weather(city, unit="celsius"):
            # In a real app, you'd call a weather API here
            return {"city": city, "temperature": 22, "unit": unit, "condition": "Sunny"}

        tool_result = get_weather(**tool_input)
        print(f"Tool result: {tool_result}")

        # Step 5: Send the tool result back so the model can formulate a final answer
        final_response = client.messages.create(
            model=DEFAULT_MODEL,  # The model to use.
            max_tokens=256,
            tools=tools,
            messages=[
                {"role": "user", "content": "What's the weather like in Tokyo right now?"},
                {"role": "assistant", "content": response.content},  # Model's tool call
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_use_id,
                            "content": json.dumps(tool_result)
                        }
                    ]
                }
            ]
        )

        print(f"\nFinal answer: {final_response.content[0].text}")

    # Example output:
    # Stop reason: tool_use
    # Model wants to call: get_weather
    # With arguments: {'city': 'Tokyo', 'unit': 'celsius'}
    # Tool result: {'city': 'Tokyo', 'temperature': 22, 'unit': 'celsius', 'condition': 'Sunny'}
    # Final answer: "The weather in Tokyo right now is sunny with a temperature of 22°C."


# ─────────────────────────────────────────────────────────────────────────────
# EXAMPLE 8 — Advanced / Production-like Config
# ─────────────────────────────────────────────────────────────────────────────
#
# This example combines everything you've learned into a single, production-grade call.
# It simulates a real-world scenario: an AI assistant for an e-commerce backend
# that needs to extract structured order data AND optionally look up product info.
# In production, you'd also add: retry logic, logging, cost tracking, and error handling.
# This is the pattern you'll use in real applications.
#
def example_8_advanced_production():
    print_section("EXAMPLE 8 — Advanced / Production-like Config")

    tools = [
        {
            "name": "lookup_product",
            "description": "Look up product details by SKU from the product catalog database.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "sku": {"type": "string", "description": "Product SKU code"}
                },
                "required": ["sku"]
            }
        }
    ]

    response = client.messages.create(
        model=DEFAULT_MODEL,  # The model to use.
        max_tokens=512,
        temperature=0,  # Deterministic for data extraction
        system=(
            "You are an intelligent order processing assistant for an e-commerce platform. "
            "Extract structured order data from user messages and respond ONLY in valid JSON. "
            "Schema: {customer_name, items: [{sku, quantity}], delivery_city, priority: bool}. "
            "If you need to verify a product, use the lookup_product tool first."
        ),
        tools=tools,
        messages=[
            {
                "role": "user",
                "content": (
                    "Process this order: John Smith wants 3 units of SKU-789 "
                    "and 1 unit of SKU-042 delivered to Berlin. Mark it as priority."
                )
            }
        ]
    )

    print(f"Stop reason: {response.stop_reason}")

    # Handle tool call if triggered
    if response.stop_reason == "tool_use":
        tool_block = next(b for b in response.content if b.type == "tool_use")
        print(f"Tool called: {tool_block.name} with {tool_block.input}")

        # Simulate product lookup
        mock_product_db = {
            "SKU-789": {"name": "Wireless Headphones", "price": 89.99, "in_stock": True},
            "SKU-042": {"name": "USB-C Cable 2m", "price": 12.99, "in_stock": True}
        }
        product_info = mock_product_db.get(tool_block.input["sku"], {"error": "Not found"})

        # Continue conversation with tool result
        final = client.messages.create(
            model=DEFAULT_MODEL,  # The model to use.
            max_tokens=512,
            temperature=0,
            system=(
                "You are an intelligent order processing assistant for an e-commerce platform. "
                "Extract structured order data from user messages and respond ONLY in valid JSON. "
                "Schema: {customer_name, items: [{sku, quantity, product_name}], delivery_city, priority: bool}."
            ),
            tools=tools,
            messages=[
                {"role": "user", "content": (
                    "Process this order: John Smith wants 3 units of SKU-789 "
                    "and 1 unit of SKU-042 delivered to Berlin. Mark it as priority."
                )},
                {"role": "assistant", "content": response.content},
                {"role": "user", "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_block.id,
                        "content": json.dumps(product_info)
                    }
                ]}
            ]
        )
        output = final.content[0].text
    else:
        output = response.content[0].text

    print("Structured output:")
    print(output)

    try:
        parsed = json.loads(output)
        print("\nParsed order:", json.dumps(parsed, indent=2))
    except json.JSONDecodeError:
        print("(Could not parse as JSON — adjust system prompt for stricter output)")

    # Calculate token cost (claude-sonnet-4-6 pricing as of 2025)
    input_cost = response.usage.input_tokens * 0.000003  # $3 per 1M input tokens
    output_cost = response.usage.output_tokens * 0.000015  # $15 per 1M output tokens
    total_cost = input_cost + output_cost
    print(f"\n💰 Cost: ${total_cost:.6f} "
          f"({response.usage.input_tokens} in / {response.usage.output_tokens} out tokens)")

    # Example output:
    # Structured output:
    # {"customer_name": "John Smith", "items": [{"sku": "SKU-789", "quantity": 3,
    #   "product_name": "Wireless Headphones"}, {"sku": "SKU-042", "quantity": 1,
    #   "product_name": "USB-C Cable 2m"}], "delivery_city": "Berlin", "priority": true}
    # 💰 Cost: $0.000312 (87 in / 89 out tokens)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN — Run all examples
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Uncomment the example you want to run.

    example_1_basic_request()
    # example_2_system_prompt()
    # example_3_temperature_and_tokens()
    # example_4_structured_output()
    # example_5_multi_turn_conversation()
    # example_6_streaming()
    # example_7_tool_calling()
    # example_8_advanced_production()
