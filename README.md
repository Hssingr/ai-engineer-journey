# AI Engineer Journey

A structured, self-paced program to become an AI Engineer — built week by week, project by project.

Every week has a clear theme, concrete deliverables, and real code pushed to this repo.  
No courses. No certificates. Just building.

---

## Progress

| Week | Theme | Project | Status |
|------|-------|---------|--------|
| 01 | Python CLI + REST APIs | [weather-cli](./week-01-python-cli/weather-cli/) | ✅ Done |
| 02 | LLM APIs (OpenAI & Anthropic) | [llm-api-learning](./week-02-llm-apis/) | 🔄 In progress |

---

## Structure

```
ai-engineer-journey/
├── week-01-python-cli/
│   └── weather-cli/          # CLI tool — OpenWeatherMap API, argparse, modular architecture
└── week-02-llm-apis/
    ├── claude_api_learning.py # 8 progressive examples with the Anthropic Claude API
    └── openai_api_learning.py # 12 progressive examples with the OpenAI API
```

---

## What I'm Learning

**Week 01 — Python CLI**
- Modular Python project structure (client / models / display / utils)
- REST API calls with `requests` + error handling
- CLI argument parsing with `argparse`
- Secret management with `python-dotenv` and `.gitignore`

**Week 02 — LLM APIs**
- Calling OpenAI and Anthropic APIs from Python
- Core parameters: `model`, `temperature`, `max_tokens`, `system`
- Structured JSON output for backend integration
- Multi-turn conversation history (stateless API pattern)
- Streaming responses token by token
- Tool / function calling — the foundation of AI agents
- Token cost calculation per API call

---

## Stack

- Python 3.11+
- `anthropic` — Anthropic Claude API
- `openai` — OpenAI GPT API
- `requests` — HTTP calls
- `python-dotenv` — API key management
