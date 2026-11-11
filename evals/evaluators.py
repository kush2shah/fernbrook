"""Evaluators for the Fernbrook support chatbot.

Single-run evaluators (attached to every experiment):
    correctness       LLM judge vs the reference answer, 0/1
    conciseness       word_count (raw number) + LLM judge "is it longer than needed", 0/1
    no_hallucination  LLM judge checks every claim against the handbook, 0/1

Pairwise evaluator (compares two existing experiments):
    preferred_by_customer  LLM judge picks the answer a real customer would prefer
"""

import json
import os
from functools import lru_cache

import anthropic
from langsmith import Client
from langsmith.schemas import Run
from langsmith.wrappers import wrap_anthropic

from app.context import load_context

JUDGE_MODEL = os.getenv("JUDGE_MODEL", "claude-opus-5-5")
JUDGE_EFFORT = os.getenv("JUDGE_EFFORT", "medium")

_client = wrap_anthropic(anthropic.Anthropic())


def _judge(system: str, user: str, properties: dict, required: list[str]) -> dict:
    """Call the judge model and return its structured JSON verdict."""
    response = _client.messages.create(
        model=JUDGE_MODEL,
        max_tokens=8000,
        system=system,
        messages=[{"role": "user", "content": user}],
        output_config={
            "effort": JUDGE_EFFORT,
            "format": {
                "type": "json_schema",
                "schema": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                    "additionalProperties": False,
                },
            },
        },
    )
    if response.stop_reason != "end_turn":
        raise RuntimeError(f"Judge stopped with stop_reason={response.stop_reason!r}")
    text = next(block.text for block in response.content if block.type == "text")
    return json.loads(text)


_REASONING = {"type": "string", "description": "Brief explanation of the verdict, written before the verdict."}


# --------------------------------------------------------------------------- #
# Single-run evaluators
# --------------------------------------------------------------------------- #

CORRECTNESS_SYSTEM = """You grade answers from a customer support chatbot for Fernbrook, a project management SaaS company.

You get a customer question, a reference answer written by the support team, and the chatbot's answer. Decide whether the chatbot's answer is correct.

An answer is correct when:
- It states the key facts in the reference answer (numbers, plan names, yes/no conclusions, conditions).
- It does not contradict the reference answer.
Extra detail, a different tone, or different wording is fine as long as it doesn't contradict the reference.

When the reference answer says the information isn't available or that the assistant should not invent something, the answer is correct if it declines to make a claim and doesn't invent one. It is incorrect if it asserts the feature, policy, or price exists."""


def correctness(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
    verdict = _judge(
        CORRECTNESS_SYSTEM,
        f"<question>\n{inputs['question']}\n</question>\n\n"
        f"<reference_answer>\n{reference_outputs['reference_answer']}\n</reference_answer>\n\n"
        f"<chatbot_answer>\n{outputs['answer']}\n</chatbot_answer>",
        properties={"reasoning": _REASONING, "correct": {"type": "boolean"}},
        required=["reasoning", "correct"],
    )
    return {"key": "correctness", "score": int(verdict["correct"]), "comment": verdict["reasoning"]}


CONCISENESS_SYSTEM = """You judge whether a customer support answer is longer than it needs to be.

You get the customer's question, a reference answer showing the information the customer needs, and the chatbot's answer.

The answer is concise if a busy customer gets what they need without wading through extra material. Mark it NOT concise if it includes padding that doesn't help the customer act on this question: greetings or sign-offs, restating the question, repeating the same point, background the customer didn't ask for, or long lists of next steps when a sentence would do. Do not judge correctness; only judge length relative to what was needed."""


def conciseness(inputs: dict, outputs: dict, reference_outputs: dict) -> list[dict]:
    answer = outputs["answer"]
    verdict = _judge(
        CONCISENESS_SYSTEM,
        f"<question>\n{inputs['question']}\n</question>\n\n"
        f"<reference_answer>\n{reference_outputs['reference_answer']}\n</reference_answer>\n\n"
        f"<chatbot_answer>\n{answer}\n</chatbot_answer>",
        properties={"reasoning": _REASONING, "concise": {"type": "boolean"}},
        required=["reasoning", "concise"],
    )
    return [
        {"key": "word_count", "score": len(answer.split())},
        {"key": "conciseness", "score": int(verdict["concise"]), "comment": verdict["reasoning"]},
    ]


NO_HALLUCINATION_SYSTEM = """You check a customer support chatbot's answer for hallucinations against the company handbook.

The chatbot was told to use only facts from the Fernbrook Customer Support Handbook. Go through every factual claim in the answer (prices, limits, plan features, policies, timelines, integrations, certifications, settings locations, contacts) and check it against the handbook below.

- A claim is supported if the handbook states it or it follows directly from handbook facts (for example, simple arithmetic on listed prices).
- A claim is unsupported if the handbook doesn't say it or says something different.
- Saying the handbook doesn't cover something, offering to check with a team, or general courtesy is not a factual claim.

Score 1 if every factual claim is supported, 0 if any claim is unsupported.

<handbook>
{handbook}
</handbook>"""


def no_hallucination(inputs: dict, outputs: dict) -> dict:
    verdict = _judge(
        NO_HALLUCINATION_SYSTEM.format(handbook=load_context("concise")[2]),
        f"<question>\n{inputs['question']}\n</question>\n\n<chatbot_answer>\n{outputs['answer']}\n</chatbot_answer>",
        properties={
            "unsupported_claims": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Each claim in the answer that the handbook does not support. Empty if none.",
            },
            "reasoning": _REASONING,
        },
        required=["unsupported_claims", "reasoning"],
    )
    claims = verdict["unsupported_claims"]
    comment = verdict["reasoning"]
    if claims:
        comment += "\nUnsupported claims:\n" + "\n".join(f"- {c}" for c in claims)
    return {"key": "no_hallucination", "score": int(not claims), "comment": comment}


SINGLE_RUN_EVALUATORS = [correctness, conciseness, no_hallucination]


# --------------------------------------------------------------------------- #
# Pairwise evaluator
# --------------------------------------------------------------------------- #

PREFERENCE_SYSTEM = """You are a customer of Fernbrook, a project management SaaS company. You asked the support chatbot a question and were shown two possible answers. Pick the one you would rather receive.

Think like a real B2B customer (an admin or team lead who is busy and wants their problem solved):
- Accuracy matters most. Verified facts from the support team are provided; an answer that gets these wrong, or invents things, is worse no matter how pleasant it is.
- Then: does it answer your actual question clearly, and does it tell you what to do next if you need to act?
- Tone and length matter only as far as they help or waste your time.

The answers are labeled A and B in random order. The label and position say nothing about quality, so don't let them influence you. Choose "tie" only if you genuinely have no preference."""


@lru_cache(maxsize=None)
def _experiment_name(session_id) -> str:
    try:
        return Client().read_project(project_id=session_id).name
    except Exception:
        return str(session_id)


def preferred_by_customer(inputs: dict, runs: list[Run], reference_outputs: dict) -> dict:
    answer_a = (runs[0].outputs or {}).get("answer", "")
    answer_b = (runs[1].outputs or {}).get("answer", "")
    verdict = _judge(
        PREFERENCE_SYSTEM,
        f"<question>\n{inputs['question']}\n</question>\n\n"
        f"<verified_facts>\n{reference_outputs['reference_answer']}\n</verified_facts>\n\n"
        f"<answer_A>\n{answer_a}\n</answer_A>\n\n"
        f"<answer_B>\n{answer_b}\n</answer_B>",
        properties={"reasoning": _REASONING, "preferred": {"type": "string", "enum": ["A", "B", "tie"]}},
        required=["reasoning", "preferred"],
    )
    preferred = verdict["preferred"]
    name_a, name_b = _experiment_name(runs[0].session_id), _experiment_name(runs[1].session_id)
    winner = {"A": name_a, "B": name_b, "tie": "tie"}[preferred]
    comment = f"Preferred: {winner}  (A = {name_a}, B = {name_b})\n\n{verdict['reasoning']}"
    scores = {
        runs[0].id: 1 if preferred == "A" else 0,
        runs[1].id: 1 if preferred == "B" else 0,
    }
    return {"key": "preferred_by_customer", "scores": scores, "comment": comment}
