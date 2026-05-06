# ops-suite Eval Framework

Implements the Anthropic Prompt Eval Workflow for all 9 ops-suite skills.

## Setup

```bash
cd plugins/ops-suite/tests
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-...
```

## Run evals

```bash
# Single skill
python runner.py --skill service-status

# All skills
python runner.py --all

# Compare with previous run
python runner.py --skill deploy --compare last
```

## Run unit tests (grader only, no API calls)

```bash
python -m pytest test_rules.py test_judge.py -v
```

## Success criteria

| Category | Target |
|----------|--------|
| Security rule checks (destructive skills) | 100% pass |
| Rule checks (read-only skills) | ≥90% pass |
| Judge average score | ≥3.5/5 |
| Full `--all` run duration | <5 minutes |

## Adding a new skill

1. Add a dataset at `datasets/<skill-name>.jsonl` (5–10 cases)
2. Add the skill to `SKILL_ADAPTER_KEY` in `runner.py`
3. Run `python runner.py --skill <skill-name>` to verify

## Dataset format

Each line is a JSON object:

```json
{
  "id": "ss-001",
  "user_message": "check if api is running in dev",
  "context": { "config": { "orchestrator": "kubernetes", ... } },
  "expected_behaviors": [
    { "type": "rule", "check": "uses_adapter", "value": "kubernetes" },
    { "type": "judge", "rubric": "Response describes pod health check..." }
  ]
}
```

Rule checks: `uses_adapter`, `no_destructive_auto_invoke`, `requests_confirmation`, `no_hallucinated_commands`, `suggests_next_skill`
