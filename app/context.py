"""The chatbot's context (instructions + handbook), versioned in LangSmith Context Hub.

The Context Hub agent repo `fernbrook-support` holds two files:
    AGENTS.md    base instructions + one prompt style
    handbook.md  the Fernbrook support handbook

Each prompt variant is a commit of that repo:
    concise  (prompt A) - first commit, treat as "production"
    friendly (prompt B) - second commit, the candidate

`push_context()` creates those commits from the local source files
(app/prompts.py, data/handbook.md) and records the commit hashes in
app/context_versions.json. At runtime the chatbot pulls its context from the
Hub by commit hash, so every experiment runs against an exact, immutable
version of the context.

    python -m app.context            # push if not pushed yet
    python -m app.context --force    # push new commits from the local files
"""

import argparse
import json
from functools import lru_cache
from pathlib import Path

from langsmith import Client
from langsmith.schemas import FileEntry

from app.config import PROMPTS  # noqa: F401  (also loads .env)
from app.prompts import BASE_INSTRUCTIONS, PROMPT_STYLES, load_handbook

REPO = "fernbrook-support"
VERSIONS_PATH = Path(__file__).resolve().parent / "context_versions.json"


def _read_versions() -> dict:
    return json.loads(VERSIONS_PATH.read_text()) if VERSIONS_PATH.exists() else {}


def push_context(force: bool = False) -> dict:
    """Push one commit per prompt style and record the hashes. Returns {style: hash}."""
    client = Client()
    versions = _read_versions()
    if not force and versions and client.agent_exists(REPO):
        return versions

    handbook = load_handbook()
    versions = {}
    for style in ("concise", "friendly"):  # order matters: concise is the "production" commit
        client.push_agent(
            REPO,
            files={
                "AGENTS.md": FileEntry(content=f"{BASE_INSTRUCTIONS}\n\n{PROMPT_STYLES[style]}"),
                "handbook.md": FileEntry(content=handbook),
            },
            description="Fernbrook support chatbot: instructions and support handbook.",
            tags=["demo", "support"],
        )
        versions[style] = client.pull_agent(REPO).commit_hash
        print(f"Pushed {REPO} ({style}): {versions[style]}")

    VERSIONS_PATH.write_text(json.dumps(versions, indent=2) + "\n")
    load_context.cache_clear()
    return versions


def context_version(style: str) -> str:
    versions = _read_versions()
    if style not in versions:
        raise RuntimeError(f"No Context Hub commit for prompt {style!r}. Run `python -m app.context` first.")
    return versions[style]


@lru_cache(maxsize=None)
def load_context(style: str) -> tuple[str, str, str]:
    """Pull the pinned commit for a prompt style. Returns (commit_hash, instructions, handbook)."""
    ctx = Client().pull_agent(REPO, version=context_version(style))
    return ctx.commit_hash, ctx.files["AGENTS.md"].content, ctx.files["handbook.md"].content


def build_system_prompt(style: str) -> tuple[str, str]:
    """Returns (system_prompt, commit_hash) for a prompt style, pulled from Context Hub."""
    commit, instructions, handbook = load_context(style)
    return f"{instructions}\n\n<handbook>\n{handbook}\n</handbook>", commit


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Push the chatbot context to LangSmith Context Hub.")
    parser.add_argument("--force", action="store_true", help="push new commits even if already pushed")
    args = parser.parse_args()
    print(json.dumps(push_context(force=args.force), indent=2))
