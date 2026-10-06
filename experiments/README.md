# Extension 6d: subagents with skills

This extension exposes the frozen `/skills/` library to every specialised
subagent when both subagents and skills are enabled. It leaves the three
official conditions and `results/` table unchanged.

Run from the repository root:

```text
python experiments/run_subagents_with_skills.py
python experiments/summarize_extension_6d.py
```

Results are written under `results/extension-6d/subagents-skills/`. The
`skills_read` field only observes the main trace; Deep Agents does not expose
the subagent's internal tool calls in `trace.md`, so subagent skill use must
also be assessed from the returned report and behavior.
