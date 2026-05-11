# Week 02 — LLM APIs

Calling real AI models from Python code for the first time.  
This week covers OpenAI and Anthropic APIs — from a basic "Hello World" call  
all the way to tool calling, streaming, and cost tracking.

> Part of my [ai-engineer-journey](../README.md)

---

## Goal

Understand how LLM APIs work at the code level — not just as a chat interface,  
but as programmable components you can integrate into any application.

---

## Files

| File | Description |
|------|-------------|
| `claude_api_learning.py` | 8 progressive examples using the Anthropic Claude API |
| `openai_api_learning.py` | 12 progressive examples using the OpenAI API |
| `main.py` | Side-by-side GPT vs Claude comparison across 5 prompts with token counts, cost, and latency |

---

## What Each File Covers

### `claude_api_learning.py`

| # | Example | Concept |
|---|---------|---------|
| 1 | Basic request | `model`, `messages`, `max_tokens` |
| 2 | System prompt | Controlling model behavior and persona |
| 3 | Temperature & max_tokens | Deterministic vs creative output |
| 4 | Structured JSON output | Reliable data extraction for backends |
| 5 | Multi-turn conversation | Stateless API + manual history management |
| 6 | Streaming | Token-by-token output for chat UX |
| 7 | Tool calling | Letting the model trigger your functions |
| 8 | Production config | All concepts combined in one real-world call |

### `openai_api_learning.py`

| # | Example | Concept |
|---|---------|---------|
| 1 | Basic text generation | `model`, `input` |
| 2 | Instructions | System-level behavior control |
| 3 | Temperature | Creative vs deterministic output |
| 4 | Max output tokens | Cost and length control |
| 5 | Message input | Structured role-based messages |
| 6 | Conversation history | Multi-turn with full context |
| 7 | Structured JSON | Schema-enforced output |
| 8 | Classification | Intent detection with low temperature |
| 9 | Streaming | Live token output |
| 10 | Tool calling — step 1 | Model decides to call a function |
| 11 | Tool calling — full loop | Execute function + return result to model |
| 12 | Metadata | Request tagging for tracking and debugging |

### `main.py`

| # | Feature | What it does |
|---|---------|-------------|
| 1 | Dual API calls | Sends the same prompt to both OpenAI and Anthropic |
| 2 | Side-by-side display | Renders responses in two columns for easy comparison |
| 3 | Token tracking | Input/output token counts per provider |
| 4 | Cost calculation | Per-call cost using configurable pricing via env vars |
| 5 | Latency measurement | Response time in ms for each API call |
| 6 | Summary stats | Total tokens and average latency across all prompts |

---

## Running the Examples

Each file has a `main` block at the bottom.  
Uncomment one example at a time to avoid burning API credits on every run.

```bash
# Anthropic examples
python claude_api_learning.py

# OpenAI examples
python openai_api_learning.py

# Comparison runner
python main.py

# Override models or pricing via env vars
OPENAI_MODEL=gpt-4o ANTHROPIC_MODEL=claude-opus-4-6 python main.py
OPENAI_INPUT_PRICING=2.5 ANTHROPIC_OUTPUT_PRICING=20 python main.py
```

---

## Cost Awareness

Both files include cost calculation at the API call level.  
Pricing reference used (as of May 2025):

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|----------------------|------------------------|
| claude-haiku-4-5 | $0.80 | $4.00 |
| claude-sonnet-4-6 | $3.00 | $15.00 |
| gpt-4o-mini | $0.15 | $0.60 |
| gpt-4.1-mini | $0.40 | $1.60 |

Running all examples in this week costs roughly **$0.05–0.15 total**.

---

## Key Concepts Learned

**The stateless API pattern**  
LLMs have no memory between calls. Every conversation is rebuilt by sending  
the full message history on each request. This is how every chatbot works.

**temperature = control**  
`0.0` for extraction, classification, structured output.  
`0.7–1.0` for brainstorming, creative writing, varied responses.

**Structured output is non-negotiable in production**  
Asking the model to return JSON with a defined schema is the difference  
between a demo and a real backend integration.

**Tool calling = the foundation of agents**  
The model doesn't run your code — it decides *when* and *with what arguments*  
to call a function. Your code executes it and sends the result back.  
This is the core loop behind every AI agent.

**Cost tracking from day one**  
`tokens_in x price_in + tokens_out x price_out`.  
Build this habit now — it matters at scale.

---

## Resources

- [Anthropic API Docs](https://docs.anthropic.com/en/api/getting-started)
- [OpenAI API Docs](https://platform.openai.com/docs/guides/text-generation)
- [Anthropic Pricing](https://www.anthropic.com/pricing)
- [OpenAI Pricing](https://openai.com/pricing)