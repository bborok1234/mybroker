# Investment Research Skill

Use this skill for MyBroker research, signal generation, and financial-domain analysis tasks.

## Operating Rules

- Keep the task research-only unless a human explicitly approves a broader scope.
- Run `PYTHONPATH=src python3 -m unittest` after code changes.
- Use `PYTHONPATH=src python3 -m mybroker policy --kind <kind>` before implementing account access, external publication, personalized recommendations, or order-related behavior.
- Every generated signal must include evidence, assumptions, and a non-actionable direction such as `positive_watch`, `negative_watch`, or `neutral_watch`.
- Do not add live brokerage credentials, order placement, or discretionary trade execution in this repo without a new explicit policy decision and review artifact.

## Run Artifacts

For substantial research work, create a run artifact under:

```text
reports/runs/YYYY-MM-DD-task-slug/
```
