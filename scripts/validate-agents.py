#!/usr/bin/env python3
"""Validate the Huishouden cr reviewers.

Checks that every agent is structurally complete, declares values the runtime can
resolve, and is listed in the README. Run with no arguments from
the repository root; exits non-zero and prints every problem found.
"""
import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
AGENTS = ROOT / ".codereview" / "agents"
README = ROOT / "README.md"

# Tiers the runtime resolves to a model. A tier outside this set aborts the whole
# review pipeline at planning time, before any reviewer runs, so an unrecognised
# value takes down every review rather than degrading one agent.
ALLOWED_TIERS = {"small", "medium", "large"}
ALLOWED_EFFORT = {"low", "medium", "high"}

problems: list[str] = []


def load(path: pathlib.Path):
    try:
        return yaml.safe_load(path.read_text())
    except yaml.YAMLError as e:
        problems.append(f"{path.relative_to(ROOT)}: not parseable as YAML: {e}")
        return None


def main() -> int:
    if not AGENTS.is_dir():
        print(f"no agents directory at {AGENTS}", file=sys.stderr)
        return 1

    readme = README.read_text() if README.exists() else ""

    for group in sorted(p for p in AGENTS.iterdir() if p.is_dir()):
        group_index = group / "index.yaml"
        if not group_index.exists():
            problems.append(f"{group.relative_to(ROOT)}: group is missing index.yaml")
        else:
            data = load(group_index)
            if isinstance(data, dict) and not data.get("name"):
                problems.append(f"{group_index.relative_to(ROOT)}: missing 'name'")

        agent_dirs = sorted(p for p in group.iterdir() if p.is_dir())
        if not agent_dirs:
            problems.append(f"{group.relative_to(ROOT)}: group contains no agents")

        for agent in agent_dirs:
            rel = agent.relative_to(ROOT)
            index = agent / "index.yaml"
            prompt = agent / "prompt.md"

            if not prompt.exists():
                problems.append(f"{rel}: missing prompt.md")
            elif not prompt.read_text().strip():
                problems.append(f"{rel}: prompt.md is empty")

            if not index.exists():
                problems.append(f"{rel}: missing index.yaml")
                continue

            data = load(index)
            if not isinstance(data, dict):
                continue

            for key in ("name", "description", "model_tier", "file_globs"):
                if not data.get(key):
                    problems.append(f"{rel}/index.yaml: missing '{key}'")

            tier = data.get("model_tier")
            if tier is not None and tier not in ALLOWED_TIERS:
                problems.append(
                    f"{rel}/index.yaml: model_tier '{tier}' is not one of {sorted(ALLOWED_TIERS)}; "
                    "an unresolvable tier aborts every review, not just this agent"
                )

            effort = data.get("effort")
            if effort is not None and effort not in ALLOWED_EFFORT:
                problems.append(
                    f"{rel}/index.yaml: effort '{effort}' is not one of {sorted(ALLOWED_EFFORT)}"
                )

            if data.get("name") and data["name"] != agent.name:
                problems.append(
                    f"{rel}/index.yaml: name '{data['name']}' does not match its directory '{agent.name}'"
                )

            agent_id = f"{group.name}:{agent.name}"
            if agent_id not in readme:
                problems.append(f"{agent_id}: not listed in README.md")

    if problems:
        print("Reviewer validation failed:\n", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1

    print("Reviewers OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
