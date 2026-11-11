"""The Fernbrook support chatbot: one traced function, no tools, no retrieval.

Usage:
    python -m app.chat "What's the refund policy for annual plans?"
    python -m app.chat --model y --prompt friendly "Can we use SSO on Team?"
"""

import argparse

import anthropic
from langsmith import traceable
from langsmith.wrappers import wrap_anthropic

from app.config import CHAT_EFFORT, CHAT_MAX_TOKENS, ChatConfig
from app.prompts import build_system_prompt

# wrap_anthropic logs each API call as a child LLM run under the chat() trace.
client = wrap_anthropic(anthropic.Anthropic())


@traceable(name="fernbrook_chat", run_type="chain")
def chat(question: str, config: ChatConfig | None = None) -> str:
    config = config or ChatConfig()
    response = client.messages.create(
        model=config.model_id,
        max_tokens=CHAT_MAX_TOKENS,
        system=build_system_prompt(config.prompt),
        messages=[{"role": "user", "content": question}],
        output_config={"effort": CHAT_EFFORT},
        # The handbook is identical across calls, so cache the prompt prefix.
        cache_control={"type": "ephemeral"},
        langsmith_extra={
            "metadata": {
                "model_variant": config.model,
                "prompt_variant": config.prompt,
            }
        },
    )
    if response.stop_reason == "refusal":
        return "Sorry, I can't help with that request. Please contact support@fernbrook.io."
    return "".join(block.text for block in response.content if block.type == "text").strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask the Fernbrook support chatbot a question.")
    parser.add_argument("question")
    parser.add_argument("--model", choices=["x", "y"], default="x")
    parser.add_argument("--prompt", choices=["concise", "friendly"], default="concise")
    args = parser.parse_args()
    print(chat(args.question, ChatConfig(model=args.model, prompt=args.prompt)))


if __name__ == "__main__":
    main()
