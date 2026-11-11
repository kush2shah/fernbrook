"""Run the full Fernbrook experiment demo.

    python evals/run.py

0. Pushes the chatbot context to Context Hub (if missing).
1. Pushes evals/dataset.json to LangSmith as `fernbrook-support` (if missing).
2. Runs the 4 configs (2 models x 2 prompts) as experiments with the
   single-run evaluators.
3. Runs 2 pairwise comparisons with the `preferred_by_customer` judge:
     - prompt A vs B on the same model (isolates the prompt)
     - model X vs Y on the same prompt (isolates the model)
4. Prints a summary, including examples where the customer-preferred answer
   lost on the aggregate metrics.
"""

import json
import sys
import time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from langsmith import Client, evaluate  # noqa: E402
from langsmith.run_trees import get_cached_client  # noqa: E402

from app.chat import chat  # noqa: E402
from app.context import context_version, push_context  # noqa: E402
from app.config import ALL_CONFIGS, CHAT_EFFORT, ChatConfig  # noqa: E402
from evals.evaluators import (  # noqa: E402
    JUDGE_MODEL,
    SINGLE_RUN_EVALUATORS,
    preferred_by_customer,
)

DATASET_NAME = "fernbrook-support"
DATASET_PATH = ROOT / "evals" / "dataset.json"
MAX_CONCURRENCY = 4

# Which experiments to compare head-to-head.
PROMPT_COMPARISON_MODEL = "y"  # prompt A vs B, both on model Y
MODEL_COMPARISON_PROMPT = "concise"  # model X vs Y, both on prompt A


def ensure_dataset(client: Client) -> None:
    examples = json.loads(DATASET_PATH.read_text())
    if client.has_dataset(dataset_name=DATASET_NAME):
        dataset = client.read_dataset(dataset_name=DATASET_NAME)
        count = dataset.example_count
        print(f"Dataset '{DATASET_NAME}' already exists ({count} examples); reusing it.")
        if count is not None and count != len(examples):
            print(
                f"  Warning: {DATASET_PATH.name} has {len(examples)} examples but LangSmith has {count}. "
                "Delete the LangSmith dataset to re-push."
            )
        return

    dataset = client.create_dataset(
        dataset_name=DATASET_NAME,
        description="Fernbrook support chatbot questions with reference answers.",
    )
    client.create_examples(
        dataset_id=dataset.id,
        examples=[
            {
                "inputs": {"question": ex["question"]},
                "outputs": {"reference_answer": ex["reference_answer"]},
                "metadata": {"category": ex["category"]},
            }
            for ex in examples
        ],
    )
    print(f"Created dataset '{DATASET_NAME}' with {len(examples)} examples.")


def run_experiment(config: ChatConfig):
    def target(inputs: dict) -> dict:
        return {"answer": chat(inputs["question"], config)}

    print(f"\n=== Experiment: {config.name} ({config.model_id}) ===")
    return evaluate(
        target,
        data=DATASET_NAME,
        evaluators=SINGLE_RUN_EVALUATORS,
        experiment_prefix=config.name,
        description=f"model={config.model_id}, prompt={config.prompt}",
        metadata={
            "model_variant": config.model,
            "model": config.model_id,
            "prompt_variant": config.prompt,
            "context_commit": context_version(config.prompt),
            "effort": CHAT_EFFORT,
            "judge_model": JUDGE_MODEL,
        },
        max_concurrency=MAX_CONCURRENCY,
    )


def wait_for_runs(client: Client, experiment_names: list[str], expected: int, timeout: float = 180) -> None:
    """Pairwise evaluation reads runs back from LangSmith, so make sure they've all landed."""
    get_cached_client().flush()
    deadline = time.time() + timeout
    for name in experiment_names:
        while True:
            runs = list(client.list_runs(project_name=name, is_root=True))
            done = sum(1 for r in runs if r.outputs)
            if done >= expected:
                break
            if time.time() > deadline:
                print(f"  Warning: {name} has {done}/{expected} runs in LangSmith; continuing anyway.")
                break
            time.sleep(3)


def run_pairwise(label: str, results_a, results_b):
    print(f"\n=== Pairwise: {label} ===")
    print(f"    {results_a.experiment_name}  vs  {results_b.experiment_name}")
    return evaluate(
        (results_a.experiment_name, results_b.experiment_name),
        evaluators=[preferred_by_customer],
        randomize_order=True,
        experiment_prefix=f"pairwise__{label}",
        description=f"Which answer would a customer prefer? {label}",
        metadata={"judge_model": JUDGE_MODEL},
        max_concurrency=MAX_CONCURRENCY,
    )


# --------------------------------------------------------------------------- #
# Summary helpers
# --------------------------------------------------------------------------- #


def collect_scores(results) -> tuple[dict, dict]:
    """Return ({example_id: {metric: score}}, {run_id: example_id}) for one experiment."""
    by_example: dict = {}
    run_to_example: dict = {}
    for row in results:
        example_id = row["example"].id
        run_to_example[str(row["run"].id)] = example_id
        by_example[example_id] = {
            r.key: r.score for r in row["evaluation_results"]["results"] if r.score is not None
        }
        by_example[example_id]["_answer"] = (row["run"].outputs or {}).get("answer", "")
        by_example[example_id]["_question"] = row["example"].inputs["question"]
    return by_example, run_to_example


def print_experiment_table(scores_by_config: dict) -> None:
    metrics = ["correctness", "no_hallucination", "conciseness", "word_count"]
    print("\n" + "=" * 78)
    print(f"{'experiment':<32}" + "".join(f"{m:>12}" for m in metrics))
    for name, by_example in scores_by_config.items():
        cells = []
        for m in metrics:
            vals = [s[m] for s in by_example.values() if m in s]
            avg = sum(vals) / len(vals) if vals else float("nan")
            cells.append(f"{avg:>12.1f}" if m == "word_count" else f"{avg:>12.2f}")
        print(f"{name:<32}" + "".join(cells))


def summarize_pairwise(label, pairwise, name_a, name_b, scores_by_config, run_to_experiment):
    wins = defaultdict(int)
    preferred_by_example = {}
    for row in pairwise:
        result = row["evaluation_results"].get("feedback.preferred_by_customer")
        if result is None:
            continue
        winner = "tie"
        for run_id, score in result.scores.items():
            if score == 1:
                winner = run_to_experiment.get(str(run_id), "?")
        wins[winner] += 1
        preferred_by_example[row["example"].id] = winner

    print(f"\n--- {label} ---")
    print(f"  {name_a}: {wins[name_a]} wins | {name_b}: {wins[name_b]} wins | ties: {wins['tie']}")
    if pairwise.url:
        print(f"  Pairwise view: {pairwise.url}")

    # Examples where the customer-preferred answer did worse on the single-run metrics.
    disagreements = []
    for example_id, winner in preferred_by_example.items():
        if winner not in (name_a, name_b):
            continue
        loser = name_b if winner == name_a else name_a
        w, lo = scores_by_config[winner][example_id], scores_by_config[loser][example_id]
        worse_on = [
            m
            for m in ("correctness", "no_hallucination", "conciseness")
            if w.get(m) is not None and lo.get(m) is not None and w[m] < lo[m]
        ]
        if worse_on:
            disagreements.append((w["_question"], winner, worse_on))
    if disagreements:
        print("  Preferred by the customer judge, but scored lower on:")
        for question, winner, worse_on in disagreements[:5]:
            print(f"    - {question!r}\n      preferred {winner}, lower {', '.join(worse_on)}")


def main() -> None:
    client = Client()
    push_context()  # no-op if the Context Hub commits already exist
    ensure_dataset(client)

    results = {cfg: run_experiment(cfg) for cfg in ALL_CONFIGS}

    expected = len(json.loads(DATASET_PATH.read_text()))
    wait_for_runs(client, [r.experiment_name for r in results.values()], expected)

    by_cfg = {cfg.name: cfg for cfg in ALL_CONFIGS}
    prompt_a = by_cfg[f"model-{PROMPT_COMPARISON_MODEL}__prompt-concise"]
    prompt_b = by_cfg[f"model-{PROMPT_COMPARISON_MODEL}__prompt-friendly"]
    model_x = by_cfg[f"model-x__prompt-{MODEL_COMPARISON_PROMPT}"]
    model_y = by_cfg[f"model-y__prompt-{MODEL_COMPARISON_PROMPT}"]

    prompt_label = f"prompt-concise-vs-friendly__model-{PROMPT_COMPARISON_MODEL}"
    model_label = f"model-x-vs-y__prompt-{MODEL_COMPARISON_PROMPT}"
    prompt_pairwise = run_pairwise(prompt_label, results[prompt_a], results[prompt_b])
    model_pairwise = run_pairwise(model_label, results[model_x], results[model_y])

    # ---- Summary ----
    scores_by_config, run_to_experiment = {}, {}
    for cfg, res in results.items():
        by_example, run_to_example = collect_scores(res)
        scores_by_config[cfg.name] = by_example
        run_to_experiment.update({run_id: cfg.name for run_id in run_to_example})

    print_experiment_table(scores_by_config)
    summarize_pairwise(
        prompt_label, prompt_pairwise, prompt_a.name, prompt_b.name, scores_by_config, run_to_experiment
    )
    summarize_pairwise(
        model_label, model_pairwise, model_x.name, model_y.name, scores_by_config, run_to_experiment
    )
    print("\nExperiments:")
    for cfg, res in results.items():
        print(f"  {cfg.name}: {res.experiment_name}")


if __name__ == "__main__":
    main()
