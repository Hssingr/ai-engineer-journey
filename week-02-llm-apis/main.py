import os
import time
from dataclasses import dataclass
from enum import Enum

import anthropic
from openai import OpenAI

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5")

OPENAI_INPUT_PRICING = float(os.getenv("OPENAI_INPUT_PRICING", "0.4"))
OPENAI_OUTPUT_PRICING = float(os.getenv("OPENAI_OUTPUT_PRICING", "1.6"))

ANTHROPIC_INPUT_PRICING = float(os.getenv("ANTHROPIC_INPUT_PRICING", "3"))
ANTHROPIC_OUTPUT_PRICING = float(os.getenv("ANTHROPIC_OUTPUT_PRICING", "15"))

class Provider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"

@dataclass
class LLMResponse:
    provider: str
    model: str
    content: str
    input_tokens: int
    output_tokens: int
    latency_ms: float

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    def total_cost(self, input_pricing: float, output_pricing: float) -> float:
        return self.input_tokens * input_pricing + self.output_tokens * output_pricing


def call_llm(provider: Provider, prompt: str, system: str = "You are a helpful assistant.",
             max_tokens: int = 1024) -> LLMResponse:
    """
    Generic LLM caller.

    Args:
        provider: "openai" or "anthropic"
        prompt:   The user message.
        system:   Optional system instruction.

    Returns:
        LLMResponse with content, token counts, and latency.
    """
    openai_client = OpenAI()
    anthropic_client = anthropic.Anthropic()
    start = time.perf_counter()

    if provider == Provider.OPENAI:
        resp = openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            max_completion_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        )
        content = resp.choices[0].message.content or ""
        input_tokens = resp.usage.prompt_tokens
        output_tokens = resp.usage.completion_tokens
        model = OPENAI_MODEL

    elif provider == Provider.ANTHROPIC:
        resp = anthropic_client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        content = resp.content[0].text
        input_tokens = resp.usage.input_tokens
        output_tokens = resp.usage.output_tokens
        model = ANTHROPIC_MODEL

    else:
        raise ValueError(f"Unknown provider '{provider}'. Use 'openai' or 'anthropic'.")

    latency_ms = (time.perf_counter() - start) * 1000

    return LLMResponse(
        provider=provider,
        model=model,
        content=content,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        latency_ms=latency_ms,
    )


# ── Display ───────────────────────────────────────────────────────────────────
def print_comparison(prompt: str,
                     r1: LLMResponse, r1_input_pricing: float, r1_output_pricing: float,
                     r2: LLMResponse, r2_input_pricing: float, r2_output_pricing: float) -> None:
    width = 100
    col = (width - 3) // 2  # width of each column

    def pad(text: str, w: int) -> list[str]:
        """Word-wrap text into lines of width w."""
        words, lines, line = text.split(), [], ""
        for word in words:
            if len(line) + len(word) + 1 <= w:
                line = f"{line} {word}".lstrip()
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)
        return lines or [""]

    sep = "─" * width
    print(f"\n{'═' * width}")
    print(f"  PROMPT: {prompt[:width - 10]}")
    print(f"{'═' * width}")

    # Header
    h1 = f"  {r1.provider.upper()} ({r1.model})"
    h2 = f"  {r2.provider.upper()} ({r2.model})"
    print(f"{h1:<{col}} │ {h2}")
    print(sep)

    # Body — side-by-side
    lines1 = pad(r1.content, col - 2)
    lines2 = pad(r2.content, col - 2)
    for l1, l2 in zip(
            lines1 + [""] * max(0, len(lines2) - len(lines1)),
            lines2 + [""] * max(0, len(lines1) - len(lines2)),
    ):
        print(f"  {l1:<{col - 2}} │   {l2}")

    # Stats
    print(sep)
    s1 = (f"  🔢 tokens: {r1.total_tokens} ({r1.input_tokens}in/{r1.output_tokens}out) "
          f"cost: {r1.total_cost(r1_input_pricing, r1_output_pricing):.6f} "
          f"({r1.input_tokens * r1_input_pricing:.6f}in/{r1.output_tokens * r1_output_pricing:.6f}out) "
          f"{r1.latency_ms:.0f}ms")
    s2 = (f"  🔢 tokens: {r2.total_tokens} ({r2.input_tokens}in/{r2.output_tokens}out) "
          f"cost: {r2.total_cost(r2_input_pricing, r2_output_pricing):.6f} "
          f"({r2.input_tokens * r2_input_pricing:.6f}in/{r2.output_tokens * r2_output_pricing:.6f}out) "
          f"{r2.latency_ms:.0f}ms")
    print(f"{s1:<{col}} │ {s2}")


# ── Prompts ───────────────────────────────────────────────────────────────────
PROMPTS = [
    "Explain what an API is in one sentence, as if I'm 10 years old.",
    "What is the difference between supervised and unsupervised learning?",
    "Write a Python one-liner that reverses a string.",
    "Give me 3 habits that separate good engineers from great engineers.",
    "What should I learn after Python to become an AI engineer?",
]


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    print("\n🤖  LLM Comparison — GPT vs Claude")
    print(f"    OpenAI model   : {OPENAI_MODEL}")
    print(f"    Anthropic model: {ANTHROPIC_MODEL}")
    print(f"    Prompts        : {len(PROMPTS)}\n")

    total = {Provider.OPENAI: {"tokens": 0, "ms": 0}, Provider.ANTHROPIC: {"tokens": 0, "ms": 0}}

    for i, prompt in enumerate(PROMPTS, 1):
        print(f"\n[{i}/{len(PROMPTS)}] Calling both APIs...")
        r_openai = call_llm(Provider.OPENAI, prompt)
        r_anthropic = call_llm(Provider.ANTHROPIC, prompt)

        print_comparison(prompt,
                         r_openai, OPENAI_INPUT_PRICING, OPENAI_OUTPUT_PRICING,
                         r_anthropic, ANTHROPIC_INPUT_PRICING, ANTHROPIC_OUTPUT_PRICING)

        for r in (r_openai, r_anthropic):
            total[r.provider]["tokens"] += r.total_tokens
            total[r.provider]["ms"] += r.latency_ms

    # Summary
    print(f"\n{'═' * 100}")
    print("  SUMMARY")
    print(f"{'═' * 100}")
    for provider, stats in total.items():
        avg_ms = stats["ms"] / len(PROMPTS)
        print(f"  {provider.upper():12s} — total tokens: {stats['tokens']:>5}  |  avg latency: {avg_ms:.0f}ms")
    print(f"{'═' * 100}\n")


if __name__ == "__main__":
    main()
