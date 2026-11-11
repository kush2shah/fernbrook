# Fernbrook Support Chatbot

A deliberately simple support chatbot for a fictional SaaS company, Fernbrook. It exists to demo **LangSmith experiments** and **pairwise experiments**. There are no tools, no RAG, and no agent loop: the whole handbook goes into the system prompt, and two variables can be swapped. See [SPEC.md](SPEC.md) for the full spec.

The chatbot's context (instructions + handbook) is versioned in **LangSmith Context Hub** as the agent repo `fernbrook-support`. Prompt A and prompt B are two commits of that repo, and the chatbot pulls its context by commit hash at runtime. Every trace and experiment records the `context_commit` it ran with.

| Variable | Options |
| --- | --- |
| model | `x` = `MODEL_X` (default `claude-haiku-5-5`, fast and cheap), `y` = `MODEL_Y` (default `claude-sonnet-5-5`, stronger) |
| prompt | `concise` (A): 1–3 sentences with a handbook citation. `friendly` (B): warm and thorough, with suggested next steps. |

That makes four configs: `model-x__prompt-concise`, `model-x__prompt-friendly`, `model-y__prompt-concise`, `model-y__prompt-friendly`.

> **Why there's no `temperature=0`:** current Claude models don't accept sampling parameters (the Anthropic SDK no longer takes a `temperature` argument). Every config instead uses the same reasoning effort (`CHAT_EFFORT`, default `low`), so the model and the prompt are still the only things that vary.

## Setup

Requires Python 3.10+.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in LANGSMITH_API_KEY and ANTHROPIC_API_KEY
```

## Run it

Push the context to Context Hub (`run.py` also does this automatically if it's missing):

```bash
python -m app.context           # creates the concise + friendly commits, saves hashes to app/context_versions.json
python -m app.context --force   # after editing app/prompts.py or data/handbook.md, push new commits
```

Ask one question (traced to the `LANGSMITH_PROJECT` project):

```bash
python -m app.chat "We're on Team with 60 people. What do we pay, and can we use SSO?"
python -m app.chat --model y --prompt friendly "Do you integrate with Asana?"
```

Seed the tracing project with 60 realistic customer messages (Haiku + friendly prompt by default, tagged with plan, channel, and user ID), for demoing "build a dataset from real traffic":

```bash
python evals/seed_traffic.py
```

Run the full experiment suite:

```bash
python evals/run.py
```

This makes 4 experiments, then 2 pairwise comparisons, with no manual steps:

1. Pushes the context to Context Hub if it isn't there yet, then pushes `evals/dataset.json` (25 examples) to LangSmith as `fernbrook-support`, if it doesn't exist yet.
2. Runs the 4 configs as experiments named `model-<x|y>__prompt-<concise|friendly>-<suffix>`, scored by:
   - `correctness`: LLM judge vs the reference answer (0/1)
   - `word_count` and `conciseness`: raw length, plus an LLM judge for "longer than needed?" (0/1)
   - `no_hallucination`: LLM judge checks every claim against the handbook (0/1)
3. Runs 2 pairwise comparisons with the `preferred_by_customer` judge (A/B order randomized for each example):
   - `pairwise__prompt-concise-vs-friendly__model-y`: same model, isolates the prompt
   - `pairwise__model-x-vs-y__prompt-concise`: same prompt, isolates the model
4. Prints a score table, pairwise win counts, and examples where the customer-preferred answer scored *lower* on a single-run metric (useful for step 5 of the demo).

A full run makes 100 chatbot calls, 300 single-run judge calls, and 50 pairwise judge calls. It takes a few minutes. To change which experiments are compared, edit `PROMPT_COMPARISON_MODEL` and `MODEL_COMPARISON_PROMPT` at the top of `evals/run.py`. To re-push the dataset after editing `dataset.json`, delete `fernbrook-support` in LangSmith first.

## Repo layout

```
├── SPEC.md
├── data/handbook.md       # the knowledge doc (~3k words), source for Context Hub
├── app/
│   ├── chat.py            # chat(question, config), @traceable + wrapped Anthropic client
│   ├── config.py          # model/prompt variables, ChatConfig
│   ├── context.py         # push/pull the context to/from Context Hub
│   ├── context_versions.json  # Context Hub commit hash for each prompt
│   └── prompts.py         # source text: grounding rules + prompt A (concise) and B (friendly)
├── evals/
│   ├── dataset.json       # 10 lookups, 6 reasoning, 5 edge cases, 4 out-of-scope
│   ├── evaluators.py      # correctness, conciseness, no_hallucination, preferred_by_customer
│   ├── run.py             # the one-command experiment runner
│   ├── seed_traffic.py    # seeds the tracing project with realistic traffic
│   └── traffic.json       # 60 seeded customer messages
├── .env.example
└── requirements.txt
```

## Demo script (5 minutes)

**1. The chatbot and its trace (1 min).** Run `python -m app.chat "We're on Team with 60 people. What do we pay, and can we use SSO?"`. It should answer $1,600/month for the 100-seat bundle and say SSO is Enterprise-only, citing the handbook. Open the trace in the `fernbrook-support-chatbot` project: the `fernbrook_chat` run wraps the Anthropic call, so you can show the full system prompt (handbook included), token usage, latency, and the `model_variant` / `prompt_variant` metadata.

**2. The dataset (30 s).** Open **Datasets & Experiments → fernbrook-support**. Show the 25 examples, the `reference_answer` outputs, and the `category` metadata (lookup, reasoning, edge_case, out_of_scope). Mention that the out-of-scope questions (Asana, HIPAA, on-prem, nonprofit discounts) test whether the bot makes things up.

**3. Compare the 4 experiments (1.5 min).** On the dataset's **Experiments** tab, select all four `model-*__prompt-*` experiments and click **Compare**. Points to make (numbers from the first full run):
- `correctness` is similar across all four (0.92–1.00). Both models get the facts right from the handbook.
- `word_count` and `conciseness` split by **prompt**: concise answers average about 52 words and pass `conciseness` 92% of the time. Friendly answers average 250–285 words and never pass.
- `no_hallucination` drops sharply with the friendly prompt (0.56 on Haiku and 0.64–0.72 on Sonnet, vs 0.96 and 1.00 with the concise prompt). Click into a failing cell: the judge's comment almost always flags the "Suggested next steps" making up UI paths the handbook never mentions, such as "upgrade under Settings → Billing → Change plan". Asking for next steps pushes the model past what it knows.

**4. The pairwise results (1.5 min).** Open the dataset's **Pairwise Experiments** tab. The aggregate scores tell you which answer is shorter, not which one a customer would rather get. The pairwise judge answers that directly:
- `pairwise__prompt-concise-vs-friendly__model-y`: concise won 23–24 of 25 across two runs. The friendly tone didn't buy any customer preference.
- `pairwise__model-x-vs-y__prompt-concise`: roughly even (Haiku 9–11, Sonnet 10, 4–6 ties across two runs). With a good prompt, customers can't tell the cheap model from the stronger one, which is a cost argument aggregate scores alone wouldn't make.
Use the thumbs up/down header buttons to filter to the examples each side won.

**5. One disagreement, up close (30 s).** `run.py` ends by listing examples where the customer-preferred answer scored lower on a single-run metric. In the first run, the one friendly win was "We're on Starter and want to connect HubSpot. Can we?" The friendly answer was preferred even though it failed both `conciseness` and `no_hallucination`. Open it in the prompt pairwise view and read both answers side by side. The concise answer says "upgrade to Team" but never says what Team costs. The friendly answer includes the $500/month starting price, which is what the customer needs to decide. It also tells them to upgrade under "Settings → Billing → Change plan", which the handbook never says. Aggregate scores mark the friendly answer down twice. The customer judge still prefers it, because it answers the question the customer actually has. Each pairwise comment starts with `Preferred: <experiment>  (A = …, B = …)` so the randomized order stays readable.

Results vary a little from run to run, so check the numbers in `run.py`'s summary before presenting.
