"""Seed the tracing project with realistic "production" traffic.

    python evals/seed_traffic.py                      # Haiku + friendly prompt
    python evals/seed_traffic.py --model y --prompt concise

Sends every message in evals/traffic.json through chat() as if it came from a
real customer, so the tracing project (LANGSMITH_PROJECT) has traffic to
filter, inspect, and turn into a dataset. Each trace is tagged with the
customer's plan, channel, and a fake user ID.

The default config (fast model + friendly prompt) is deliberately not the best
one, so some answers are imperfect, like real production traffic.
"""

import argparse
import json
import random
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from langsmith.run_trees import get_cached_client  # noqa: E402

from app.chat import chat  # noqa: E402
from app.config import ChatConfig  # noqa: E402

TRAFFIC_PATH = ROOT / "evals" / "traffic.json"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model", choices=["x", "y"], default="x")
    parser.add_argument("--prompt", choices=["concise", "friendly"], default="friendly")
    parser.add_argument("--concurrency", type=int, default=6)
    args = parser.parse_args()

    config = ChatConfig(model=args.model, prompt=args.prompt)
    traffic = json.loads(TRAFFIC_PATH.read_text())
    rng = random.Random(7)
    for item in traffic:
        item["user_id"] = f"user_{rng.randint(1000, 9999)}"

    def send(item: dict) -> str:
        chat(
            item["message"],
            config,
            langsmith_extra={
                "metadata": {"user_id": item["user_id"], "plan": item["plan"], "channel": item["channel"]},
                "tags": ["seeded-traffic", f"plan:{item['plan']}"],
            },
        )
        return item["message"]

    print(f"Sending {len(traffic)} messages with {config.name} ({config.model_id})...")
    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        for i, message in enumerate(pool.map(send, traffic), 1):
            print(f"  [{i:>2}/{len(traffic)}] {message[:70]}")

    get_cached_client().flush()
    print("Done.")


if __name__ == "__main__":
    main()
