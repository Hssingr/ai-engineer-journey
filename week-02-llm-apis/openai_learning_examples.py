"""
╔══════════════════════════════════════════════════════════════════════════════╗
║           OPENAI API — FROM BEGINNER TO ADVANCED                           ║
║           A complete learning file for AI engineers                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

This file walks you through 8 progressive examples using the OPENAI API.
Each example builds on the previous one. Read the comments carefully — they are
as important as the code itself.

Prerequisites:
   pip install openai

Setup:
    Create a .env file at the root of your project:
        OPENAI_API_KEY="your_api_key_here"

Author: Your AI Engineer Journey — Week 2

"""

import json
import os
from typing import Any, Dict

from openai import OpenAI

# The OpenAI client reads OPENAI_API_KEY from your environment automatically.
client = OpenAI()

# model: chooses which AI model will answer.
# Keep it configurable so you can change it without editing all examples.
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.1")


# -----------------------------------------------------------------------------
# Helper function
# -----------------------------------------------------------------------------

def print_section(title: str) -> None:
    """Small helper to separate examples in the console output."""
    print("\n" + "=" * 90)
    print(title)
    print("=" * 90)


# =============================================================================
# Example 1 - Basic text generation
# =============================================================================
"""
USE CASE:
This is the smallest useful API call. You give the model a simple input string,
and the model returns text.

WHAT CHANGED COMPARED TO NOTHING:
We only provide two attributes: model and input.

WHY:
Use this when you want a simple answer and do not need special formatting,
conversation history, tools, or JSON.
"""


def example_01_basic_text() -> None:
    print_section("Example 1 - Basic text generation")

    response = client.responses.create(
        model=DEFAULT_MODEL,  # model: the AI model that will generate the answer.
        input="Write a one-sentence bedtime story about a unicorn.",  # input: the user request/prompt.
    )

    # output_text: convenient property containing the final text answer.
    print(response.output_text)

    # Example possible output:
    # "Under a silver moon, a tiny unicorn followed a trail of stars home and fell asleep beside a glowing lake."


# =============================================================================
# Example 2 - Add instructions to control behavior
# =============================================================================
"""
USE CASE:
Sometimes the user request is not enough. You want to define how the model should
behave: tone, role, language, answer style, constraints, etc.

WHAT CHANGED:
We added the instructions parameter.

WHY:
instructions are useful for stable behavior across many calls. For example, in a
backend app, you can say: "Always answer as a senior software engineer" or
"Always answer in JSON only".
"""


def example_02_instructions() -> None:
    print_section("Example 2 - Instructions")

    response = client.responses.create(
        model=DEFAULT_MODEL,  # model: which model to use.
        instructions=(
            "You are a patient programming teacher. "
            "Explain concepts simply, with one short example."
        ),  # instructions: high-level behavior rules for the model.
        input="Explain what an API is.",  # input: the actual user task.
    )

    print(response.output_text)

    # Example possible output:
    # "An API is a way for one program to talk to another program..."


# =============================================================================
# Example 3 - Control creativity with temperature
# =============================================================================
"""
USE CASE:
The same prompt can produce different answers. temperature controls how creative
or predictable the answer should be.

WHAT CHANGED:
We added temperature.

WHY:
For production extraction, classification, or backend logic, use low temperature
like 0 or 0.2. For creative writing, brainstorming, or marketing ideas, use a
higher value like 0.8 or 1.0.
"""


def example_03_temperature() -> None:
    print_section("Example 3 - Temperature")

    response = client.responses.create(
        model=DEFAULT_MODEL,  # model: the AI model.
        input="Give me 5 creative names for an AI note-taking app.",  # input: task.
        temperature=0.9,  # temperature: higher = more creative/random; lower = more deterministic.
    )

    print(response.output_text)

    # Example possible output:
    # 1. MindScribe
    # 2. EchoNotes
    # 3. NotePilot
    # 4. BrainInk
    # 5. RecallAI


# =============================================================================
# Example 4 - Limit output length with max_output_tokens
# =============================================================================
"""
USE CASE:
Sometimes you want to control cost and avoid very long answers.

WHAT CHANGED:
We added max_output_tokens.

WHY:
This is important in real applications because long outputs cost more and can
make your UI slow or messy. It is also useful when you need short summaries.
"""


def example_04_max_output_tokens() -> None:
    print_section("Example 4 - Max output tokens")

    response = client.responses.create(
        model=DEFAULT_MODEL,  # model: the model used for generation.
        input="Explain microservices in simple terms.",  # input: user prompt.
        max_output_tokens=80,  # max_output_tokens: maximum number of tokens the model can generate.
    )

    print(response.output_text)

    # Example possible output:
    # "Microservices are a way to build an application as small independent services..."


# =============================================================================
# Example 5 - Use structured message input instead of a simple string
# =============================================================================
"""
USE CASE:
For chat-like apps, you often need roles: user, assistant, system/developer.
Instead of a plain string, input can be a list of messages.

WHAT CHANGED:
input is now a list of message objects, not just a string.

WHY:
This is useful when building chatbots or when you want to send conversation
history to the model.
"""


def example_05_message_input() -> None:
    print_section("Example 5 - Message input")

    response = client.responses.create(
        model=DEFAULT_MODEL,  # model: AI model.
        input=[
            {
                "role": "user",  # role: tells the model who said this message.
                "content": "Explain the difference between frontend and backend.",  # content: message text.
            }
        ],
    )

    print(response.output_text)

    # Example possible output:
    # "Frontend is what users see and interact with. Backend is the server-side logic..."


# =============================================================================
# Example 6 - Multi-turn conversation history
# =============================================================================
"""
USE CASE:
The OpenAI API is normally stateless: it does not automatically remember your
previous calls unless you send the relevant history again.

WHAT CHANGED:
We send a list containing previous user and assistant messages.

WHY:
This lets the model understand context, follow-up questions, and previous
answers. In a real app, you usually store the conversation in your database and
send the important parts with each request.
"""


def example_06_conversation_history() -> None:
    print_section("Example 6 - Conversation history")

    response = client.responses.create(
        model=DEFAULT_MODEL,
        input=[
            {
                "role": "user",
                "content": "Explain REST APIs in one sentence.",
            },
            {
                "role": "assistant",
                "content": "A REST API lets applications communicate over HTTP using resources like users, products, "
                           "or orders.",
            },
            {
                "role": "user",
                "content": "Now explain it with a restaurant analogy.",
            },
        ],
    )

    print(response.output_text)

    # Example possible output:
    # "A REST API is like a waiter: your app orders data from the server, and the server brings back the result."


# =============================================================================
# Example 7 - Structured JSON output with json_schema
# =============================================================================
"""
USE CASE:
In real software, you often do not want free text. You want reliable JSON that
your backend can parse safely.

WHAT CHANGED:
We added text.format with a JSON schema.

WHY:
This is critical for extraction, classification, form filling, database inserts,
and API responses. Instead of asking "please return JSON", you define the exact
shape you expect.
"""


def example_07_structured_json() -> None:
    print_section("Example 7 - Structured JSON output")

    response = client.responses.create(
        model=DEFAULT_MODEL,
        input="Extract the customer name, product, and urgency from: 'Hi, I am Firas. I need the invoice for my RAV4 "
              "today.'",
        text={
            "format": {
                "type": "json_schema",  # type : tells the API we want schema-enforced JSON.
                "name": "support_request",  # name: identifier for this schema.
                "schema": {  # schema: the exact JSON structure expected.
                    "type": "object",
                    "properties": {
                        "customer_name": {"type": "string"},
                        "product": {"type": "string"},
                        "urgency": {
                            "type": "string",
                            "enum": ["low", "medium", "high"],
                        },
                    },
                    "required": ["customer_name", "product", "urgency"],
                    "additionalProperties": False,
                },
                "strict": True,  # strict: makes the model follow the schema more strictly.
            }
        },
    )

    data = json.loads(response.output_text)
    print(data)

    # Example possible output:
    # {'customer_name': 'Firas', 'product': 'RAV4 invoice', 'urgency': 'high'}


# =============================================================================
# Example 8 - Classification with low temperature and JSON
# =============================================================================
"""
USE CASE:
This is a production-style classification example. You give the model a message
and it returns a controlled category.

WHAT CHANGED:
We combine instructions, low temperature, and structured JSON.

WHY:
This pattern is good for routing tickets, detecting intent, labeling emails,
classifying user requests, and deciding which backend workflow to trigger.
"""


def example_08_classification() -> None:
    print_section("Example 8 - Classification")

    response = client.responses.create(
        model=DEFAULT_MODEL,
        instructions="Classify the user message. Do not invent extra categories.",
        input="The camera arrived broken and I want my money back.",
        temperature=0.0,  # low temperature: better for deterministic classification.
        text={
            "format": {
                "type": "json_schema",
                "name": "message_classification",
                "schema": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "enum": ["refund", "technical_support", "sales", "general_question"],
                        },
                        "sentiment": {
                            "type": "string",
                            "enum": ["negative", "neutral", "positive"],
                        },
                    },
                    "required": ["category", "sentiment"],
                    "additionalProperties": False,
                },
                "strict": True,
            }
        },
    )

    print(json.loads(response.output_text))

    # Example possible output:
    # {'category': 'refund', 'sentiment': 'negative'}


# =============================================================================
# Example 9 - Streaming output
# =============================================================================
"""
USE CASE:
For chat apps, waiting until the full response is complete can feel slow.
Streaming lets you display the response progressively, token by token or chunk
by chunk.

WHAT CHANGED:
We use client.responses.stream(...) instead of client.responses.create(...).

WHY:
This improves user experience in chatbots, copilots, and long-form generation.
"""


def example_09_streaming() -> None:
    print_section("Example 9 - Streaming")

    with client.responses.stream(
            model=DEFAULT_MODEL,
            input="Write a short paragraph explaining why streaming improves chatbot UX.",
    ) as stream:
        for event in stream:
            if event.type == "response.output_text.delta":
                print(event.delta, end="", flush=True)

        final_response = stream.get_final_response()

    print("\n\nFinal output_text:")
    print(final_response.output_text)

    # Example possible streaming chunks:
    # "Streaming" -> " makes" -> " the" -> " answer" -> " appear" -> " immediately"...


# =============================================================================
# Example 10 - Function/tool calling: model chooses a backend function
# =============================================================================
"""
USE CASE:
The model cannot directly access your database, payment system, calendar, or
internal services. Tool calling lets the model decide when a backend function is
needed, and your code executes that function.

WHAT CHANGED:
We added tools. The model may return a function_call instead of a normal text
answer.

WHY:
This is one of the most important AI engineering patterns. The AI decides what
should be done, but your backend remains in control of real actions.
"""


def fake_get_order_status(order_id: str) -> Dict[str, Any]:
    """Fake backend function. Replace this with a database/API call in real life."""
    fake_db = {
        "ORD-1001": {"status": "shipped", "eta": "tomorrow"},
        "ORD-2002": {"status": "processing", "eta": "in 3 days"},
    }
    return fake_db.get(order_id, {"status": "not_found", "eta": None})


def example_10_tool_calling_step_1() -> None:
    print_section("Example 10 - Tool calling step 1: let the model request a function")

    response = client.responses.create(
        model=DEFAULT_MODEL,
        input="What is the status of order ORD-1001?",
        tools=[
            {
                "type": "function",  # type : tells the API this is a custom function tool.
                "name": "get_order_status",  # name: function name the model can call.
                "description": "Get the shipping status of a customer order.",
                # description: helps the model know when to call it.
                "parameters": {  # parameters: JSON schema for function arguments.
                    "type": "object",
                    "properties": {
                        "order_id": {
                            "type": "string",
                            "description": "The order ID, for example ORD-1001.",
                        }
                    },
                    "required": ["order_id"],
                    "additionalProperties": False,
                },
                "strict": True,  # strict: model must respect the function argument schema.
            }
        ],
        tool_choice="auto",  # tool_choice: auto means model decides whether to answer or call a tool.
    )

    print("Raw output items:")
    for item in response.output:
        print(item)

    # Example possible output item:
    # ResponseFunctionToolCall(
    #   type='function_call',
    #   name='get_order_status',
    #   arguments='{"order_id":"ORD-1001"}',
    #   call_id='call_abc123'
    # )


# =============================================================================
# Example 11 - Function/tool calling: execute tool and send result back
# =============================================================================
"""
USE CASE:
A full tool-calling loop has two API calls:
1) Ask the model what tool it wants to call.
2) Execute the tool in your code, then send the tool result back to the model so
   it can produce the final user-friendly answer.

WHAT CHANGED:
We now parse the function call, execute fake_get_order_status(...), and send a
function_call_output item back to the model.

WHY:
This is the real pattern used in AI agents and assistants connected to backend
systems.
"""


def example_11_tool_calling_full_loop() -> None:
    print_section("Example 11 - Tool calling full loop")

    first_response = client.responses.create(
        model=DEFAULT_MODEL,
        input="What is the status of order ORD-1001?",
        tools=[
            {
                "type": "function",
                "name": "get_order_status",
                "description": "Get the shipping status of a customer order.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "order_id": {"type": "string"}
                    },
                    "required": ["order_id"],
                    "additionalProperties": False,
                },
                "strict": True,
            }
        ],
        tool_choice="auto",
    )

    function_call = None
    for item in first_response.output:
        if item.type == "function_call":
            function_call = item
            break

    if function_call is None:
        print("The model answered directly instead of calling the tool:")
        print(first_response.output_text)
        return

    arguments = json.loads(function_call.arguments)
    tool_result = fake_get_order_status(arguments["order_id"])

    second_response = client.responses.create(
        model=DEFAULT_MODEL,
        input=[
            # Send back the original function call item so the model knows what happened.
            function_call,
            {
                "type": "function_call_output",  # type : tells API this is the tool result.
                "call_id": function_call.call_id,  # call_id: links result to the exact function call.
                "output": json.dumps(tool_result),  # output: result from your backend function.
            },
        ],
    )

    print(second_response.output_text)

    # Example possible output:
    # "Your order ORD-1001 has shipped and is expected to arrive tomorrow."


# =============================================================================
# Example 12 - Metadata for tracking/debugging
# =============================================================================
"""
USE CASE:
In real applications, you may want to attach metadata to requests so you can
trace usage by user, feature, environment, or experiment.

WHAT CHANGED:
We added metadata.

WHY:
Metadata is useful for debugging, analytics, and organizing API usage. Do not put
private secrets or sensitive data in metadata.
"""


def example_12_metadata() -> None:
    print_section("Example 12 - Metadata")

    response = client.responses.create(
        model=DEFAULT_MODEL,
        input="Summarize: OpenAI APIs help developers add AI features to software.",
        metadata={
            "app": "learning_project",  # metadata: custom key-value info for tracking.
            "feature": "summary_demo",
            "environment": "local",
        },
    )

    print(response.output_text)

    # Example possible output:
    # "OpenAI APIs let developers integrate AI capabilities into their applications."


# =============================================================================
# Main runner
# =============================================================================
"""
HOW TO USE THIS FILE:
Uncomment one example at a time. This avoids spending API credits accidentally.
Start from example_01 and move down step by step.
"""

if __name__ == "__main__":
    # Uncomment the example you want to run.

    example_01_basic_text()
    # example_02_instructions()
    # example_03_temperature()
    # example_04_max_output_tokens()
    # example_05_message_input()
    # example_06_conversation_history()
    # example_07_structured_json()
    # example_08_classification()
    # example_09_streaming()
    # example_10_tool_calling_step_1()
    # example_11_tool_calling_full_loop()
    # example_12_metadata()
