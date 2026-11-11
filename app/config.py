"""Experiment variables: which model and which prompt the chatbot uses."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

# The two models under test. "x" is the fast/cheap one, "y" the stronger one.
MODELS: dict[str, str] = {
    "x": os.getenv("MODEL_X", "claude-haiku-5-5"),
    "y": os.getenv("MODEL_Y", "claude-sonnet-5-5"),
}

# Current Claude models don't accept temperature, so we hold reasoning effort
# fixed instead. Every config uses the same effort, so differences between
# experiments come from the model and prompt only.
CHAT_EFFORT = os.getenv("CHAT_EFFORT", "low")
CHAT_MAX_TOKENS = 4000

PROMPTS = ("concise", "friendly")


@dataclass(frozen=True)
class ChatConfig:
    model: str = "x"  # "x" or "y"
    prompt: str = "concise"  # "concise" (A) or "friendly" (B)

    @property
    def model_id(self) -> str:
        return MODELS[self.model]

    @property
    def name(self) -> str:
        """Experiment name prefix, e.g. 'model-x__prompt-concise'."""
        return f"model-{self.model}__prompt-{self.prompt}"


ALL_CONFIGS = [ChatConfig(model=m, prompt=p) for m in MODELS for p in PROMPTS]
