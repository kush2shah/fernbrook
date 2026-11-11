# Fernbrook Support Chatbot: Experiment Demo Spec

A deliberately simple chatbot that exists to demo **LangSmith experiments** and **pairwise experiments**. It has no tools, no RAG, and no agent loop. One knowledge doc goes in the system prompt, and a couple of variables can be swapped.

> Check the current LangSmith SDK docs (docs MCP or docs.langchain.com) for `evaluate` and pairwise / comparative evaluation signatures before writing eval code. Don't rely on memory.

## 1. The chatbot

- **Company:** Fernbrook, a fictional B2B workflow / project management SaaS with Starter, Team, and Enterprise plans.
- **Knowledge:** a single `data/handbook.md` (~3–4k words) covering pricing, refunds, SLAs, integrations, security, account management, and common troubleshooting. It goes directly into the system prompt.
- **App:** a single function `chat(question, config) -> answer`. The config sets the variables below. Trace it with `@traceable` (or use a LangChain chat model) so every run shows up in LangSmith.

## 2. Variables

| Variable | Options |
| --- | --- |
| model | two models, set via env (e.g., a fast/cheap one vs a stronger one) |
| prompt | A, "concise": answer in 1–3 sentences and cite the handbook section. B, "friendly": warm and thorough, with suggested next steps. |

That gives 4 configs. Keep `temperature` fixed at 0 so differences come from the variables.

> **Implementation note:** current Claude models don't accept `temperature`, so the implementation holds reasoning `effort` fixed across all configs instead. See README.

## 3. Handbook facts (must appear in the handbook verbatim-consistent)

- **Refunds:** annual plans are refundable (prorated) within 30 days. After that, no refunds; service credits require VP of Customer Success approval.
- **Pricing:**
    - Starter: $10/seat/mo.
    - Team: bundles of 25 / 50 / 100 seats at $500 / $900 / $1,600 per month.
    - Enterprise: custom.
- **SLA:** Enterprise 99.9% uptime, P1 first response within 1 hour. Team gets business-hours support.
- **Integrations:** Salesforce, Slack, Jira, HubSpot. HubSpot is Team+ only.
- **Security:** SOC 2 Type II, SSO/SAML on Enterprise only, data retained 90 days after cancellation.
- **Seat changes:** seats can be added anytime. Downgrades take effect at renewal.

Add enough surrounding detail that the handbook reads like a real doc.

## 4. Dataset (~25 examples)

`evals/dataset.json` gets pushed to LangSmith as `fernbrook-support`. Each example has `question` and `reference_answer`. The mix:

- **Straight lookups (10):** "What's the refund policy for annual plans?"
- **Reasoning across facts (6):** "We're on Team with 60 people. What do we pay, and can we use SSO?" Answer: $1,600/mo for the 100 bundle; no SSO, that's Enterprise.
- **Edge cases (5):** "It's been 45 days, can I get a refund?" Answer: no refund; credits possible with VP CS approval.
- **Out of scope / unknown (4):** "Do you integrate with Asana?" Answer: not listed; don't invent it.

## 5. Evaluators

- **Single-run (every experiment):**
    - `correctness`: LLM-as-judge vs reference answer, 0/1.
    - `conciseness`: word count, plus a judge score for whether the answer is longer than needed.
    - `no_hallucination`: judge checks claims against the handbook.
- **Pairwise:**
    - `preferred_by_customer`: an LLM judge sees both answers for the same question and picks which a real customer would prefer.
    - Randomize A/B order to avoid position bias.

## 6. Experiment script

`evals/run.py`:

1. Push the dataset if it doesn't exist.
2. Run all 4 configs as separate experiments with the single-run evaluators, named like `model-x__prompt-concise`.
3. Run pairwise comparisons:
    - **Prompt A vs B** on the same model, to isolate the prompt.
    - **Model X vs Y** on the same prompt, to isolate the model.

## 7. Repo layout

```
fernbrook-chatbot/
├── SPEC.md
├── data/handbook.md
├── app/
│   ├── chat.py        # chat(question, config)
│   └── prompts.py     # prompt A and B
├── evals/
│   ├── dataset.json
│   ├── evaluators.py
│   └── run.py
├── .env.example
└── README.md          # setup + demo script
```

## 8. Demo story (5 minutes)

1. Show the chatbot answering one question, then the trace.
2. Show the dataset in LangSmith.
3. Open the 4-experiment comparison view: correctness is similar, conciseness differs by prompt.
4. Open the pairwise results. This answers "which one do customers actually prefer," which aggregate scores can't.
5. Point out one example where the two experiments disagree and walk through both answers.

**Definition of done:** `python evals/run.py` produces 4 experiments and 2 pairwise comparisons in LangSmith with no manual steps.
