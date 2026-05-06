#!/usr/bin/env python3
"""ops-suite eval runner — implements the Anthropic Prompt Eval Workflow."""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import anthropic

TESTS_DIR = Path(__file__).parent
SKILLS_DIR = TESTS_DIR.parent / "skills"
DATASETS_DIR = TESTS_DIR / "datasets"
RESULTS_DIR = TESTS_DIR / "results"

HAIKU = "claude-haiku-4-5-20251001"

SKILL_ADAPTER_KEY = {
    "service-status": "orchestrator",
    "service-logs": "orchestrator",
    "queue-status": "message_broker",
    "deploy-status": "orchestrator",
    "db-query": "database",
    "queue-triage": "message_broker",
    "deploy": None,
    "db-migrate": None,
    "queue-reprocess": "message_broker",
}


def _adapter_technology(skill_name: str, config: dict) -> str:
    key = SKILL_ADAPTER_KEY.get(skill_name)
    if key is None:
        if skill_name == "deploy":
            return config.get("deploy", {}).get("ci_provider", "github-actions")
        if skill_name == "db-migrate":
            return config.get("deploy", {}).get("migration_tool", "mikro-orm")
        return ""
    return config.get(key, "")


def load_skill_content(skill_name: str) -> str:
    path = SKILLS_DIR / skill_name / "SKILL.md"
    if not path.exists():
        raise FileNotFoundError(f"SKILL.md not found: {path}")
    return path.read_text()


def load_adapter_content(skill_name: str, technology: str) -> str:
    for subdir in ("adapters", "references"):
        path = SKILLS_DIR / skill_name / subdir / f"{technology}.md"
        if path.exists():
            return path.read_text()
    return ""


def build_system_prompt(skill_content: str, config: dict) -> str:
    config_json = json.dumps(config, indent=2)
    return (
        f"{skill_content}\n\n"
        "---\n"
        "## Active session config (use this instead of reading config files)\n"
        f"```json\n{config_json}\n```"
    )


def call_claude(system_prompt: str, user_message: str) -> str:
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=HAIKU,
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    return response.content[0].text


def load_dataset(skill_name: str) -> list:
    path = DATASETS_DIR / f"{skill_name}.jsonl"
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")
    cases = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                cases.append(json.loads(line))
    return cases


def grade_case(case: dict, response: str, adapter_content: str) -> dict:
    from grader.rules import run_rule_check
    from grader.judge import run_judge

    rule_results = []
    judge_result = None

    for behavior in case["expected_behaviors"]:
        if behavior["type"] == "rule":
            passed = run_rule_check(
                check=behavior["check"],
                response=response,
                behavior=behavior,
                adapter_content=adapter_content,
            )
            rule_results.append({"check": behavior["check"], "passed": passed})
        elif behavior["type"] == "judge":
            judge_result = run_judge(response=response, rubric=behavior["rubric"])

    all_rules_pass = all(r["passed"] for r in rule_results)
    judge_pass = judge_result is None or judge_result["score"] >= 3
    passed = all_rules_pass and judge_pass

    return {
        "id": case["id"],
        "passed": passed,
        "rule_results": rule_results,
        "judge_result": judge_result,
        "claude_response": response,
    }


def run_skill_eval(skill_name: str) -> dict:
    skill_content = load_skill_content(skill_name)
    cases = load_dataset(skill_name)
    case_results = []

    for case in cases:
        config = case.get("context", {}).get("config", {})
        technology = _adapter_technology(skill_name, config)
        adapter_content = load_adapter_content(skill_name, technology) if technology else ""
        system_prompt = build_system_prompt(skill_content, config)
        response = call_claude(system_prompt, case["user_message"])
        result = grade_case(case, response, adapter_content)
        case_results.append(result)
        status = "✓" if result["passed"] else "✗"
        print(f"  {status} {result['id']}")

    passed_count = sum(1 for r in case_results if r["passed"])
    return {
        "skill": skill_name,
        "total": len(case_results),
        "passed": passed_count,
        "cases": case_results,
    }


def save_results(skill_name: str, result: dict) -> Path:
    RESULTS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
    path = RESULTS_DIR / f"{timestamp}-{skill_name}.json"
    path.write_text(json.dumps(result, indent=2))
    return path


def load_last_result(skill_name: str) -> Optional[dict]:
    files = sorted(RESULTS_DIR.glob(f"*-{skill_name}.json"))
    if len(files) < 2:
        return None
    return json.loads(files[-2].read_text())


def print_comparison(current: dict, previous: dict) -> None:
    delta = current["passed"] - previous["passed"]
    sign = "+" if delta >= 0 else ""
    print(f"  vs previous: {previous['passed']}/{previous['total']} ({sign}{delta})")


def print_report(results: list, compare: bool) -> None:
    print(f"\n=== ops-suite eval run — {datetime.now().strftime('%Y-%m-%d %H:%M')} ===\n")
    total_passed = 0
    total_cases = 0
    for r in results:
        pct = int(r["passed"] / r["total"] * 100) if r["total"] else 0
        print(f"{r['skill']:20s}  {r['passed']}/{r['total']} passed ({pct}%)")
        if compare:
            prev = load_last_result(r["skill"])
            if prev:
                print_comparison(r, prev)
        total_passed += r["passed"]
        total_cases += r["total"]

    overall_pct = int(total_passed / total_cases * 100) if total_cases else 0
    print(f"\nOverall: {total_passed}/{total_cases} passed ({overall_pct}%)")


def available_skills() -> list:
    return [p.stem for p in DATASETS_DIR.glob("*.jsonl") if p.is_file()]


def main() -> None:
    parser = argparse.ArgumentParser(description="ops-suite eval runner")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--skill", help="Run evals for a single skill")
    group.add_argument("--all", action="store_true", help="Run evals for all skills")
    parser.add_argument("--compare", metavar="WHEN", choices=["last"],
                        help="Compare results against a previous run (use: last)")
    args = parser.parse_args()

    sys.path.insert(0, str(TESTS_DIR))

    skills_to_run = available_skills() if args.all else [args.skill]
    all_results = []

    for skill_name in skills_to_run:
        print(f"\n{skill_name}:")
        try:
            result = run_skill_eval(skill_name)
            path = save_results(skill_name, result)
            print(f"  → saved to {path.name}")
            all_results.append(result)
        except FileNotFoundError as e:
            print(f"  ✗ skipped: {e}")

    print_report(all_results, compare=args.compare == "last")


if __name__ == "__main__":
    main()
