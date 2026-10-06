"""Run GUIDE extension 6d without changing the three official conditions.

Usage from the repository root:
    python experiments/run_subagents_with_skills.py
"""

from __future__ import annotations

import argparse
from pathlib import Path

from lab.runner import CONDITIONS, run_task
from lab.tasks import list_tasks


CONDITION = "subagents-skills"
DEFAULT_RESULTS = Path("results") / "extension-6d"


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run extension 6d: subagents with frozen skills.")
    parser.add_argument("--results", default=str(DEFAULT_RESULTS))
    parser.add_argument("--recursion-limit", type=int, default=40)
    parser.add_argument("--tasks", nargs="+", default=["eval"])
    args = parser.parse_args(argv)

    # Register only for this process. The official CONDITIONS constant remains
    # exactly the three conditions required by the rubric in normal runs.
    CONDITIONS[CONDITION] = {"mode": "subagents", "skills_dir": "skills/auto"}

    if args.tasks == ["eval"]:
        task_ids = [task.id for task in list_tasks("eval")]
    else:
        task_ids = args.tasks

    for task_id in task_ids:
        record = run_task(
            task_id,
            CONDITION,
            results_dir=args.results,
            recursion_limit=args.recursion_limit,
        )
        suffix = f" ERROR={record['error']}" if record["error"] else ""
        print(
            f"{CONDITION:18s} {task_id:11s} "
            f"score={record['passed']}/{record['total']} "
            f"tokens={record['tokens']['total']} calls={record['tool_calls']} "
            f"subagents={record['subagent_calls']} {record['seconds']}s{suffix}",
            flush=True,
        )


if __name__ == "__main__":
    main()
