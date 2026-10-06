"""Summarize extension 6d against the two closest official conditions."""

from __future__ import annotations

import json
from pathlib import Path


SOURCES = {
    "subagents": Path("results/subagents"),
    "skills-auto": Path("results/skills-auto"),
    "subagents-skills": Path("results/extension-6d/subagents-skills"),
}


def load_eval_runs(root: Path) -> dict[str, dict]:
    runs = {}
    for path in sorted(root.glob("*-eval/run.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        runs[record["task"]] = record
    return runs


def main() -> None:
    data = {name: load_eval_runs(root) for name, root in SOURCES.items()}
    conditions = list(SOURCES)
    tasks = sorted({task for runs in data.values() for task in runs})

    print("| Task | " + " | ".join(conditions) + " |")
    print("|---|" + "---|" * len(conditions))
    for task in tasks:
        cells = []
        for condition in conditions:
            record = data[condition].get(task)
            cells.append(f"{record['passed']}/{record['total']}" if record else "-")
        print(f"| {task} | " + " | ".join(cells) + " |")

    print("\n| Metric | " + " | ".join(conditions) + " |")
    print("|---|" + "---|" * len(conditions))
    metrics = {}
    for condition in conditions:
        runs = list(data[condition].values())
        metrics[condition] = {
            "mean_score": sum(record["score"] for record in runs) / len(runs),
            "mean_tokens": sum(record["tokens"]["total"] for record in runs) / len(runs),
            "subagent_calls": sum(record["subagent_calls"] for record in runs),
            "main_trace_skills_read": sum(record["skills_read"] for record in runs),
        }
    for key, label, formatter in (
        ("mean_score", "Mean eval score", lambda value: f"{value:.2f}"),
        ("mean_tokens", "Mean tokens/run", lambda value: f"{value:,.1f}"),
        ("subagent_calls", "Subagent calls", str),
        ("main_trace_skills_read", "Skill reads visible in main trace", str),
    ):
        print("| " + label + " | " + " | ".join(formatter(metrics[c][key]) for c in conditions) + " |")


if __name__ == "__main__":
    main()
