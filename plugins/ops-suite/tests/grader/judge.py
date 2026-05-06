import json
import re
import anthropic

SONNET = "claude-sonnet-4-6"

_JUDGE_PROMPT = """You are evaluating an AI assistant's response to an infrastructure operations task.

Score the response 1–5 using this rubric:
{rubric}

Scoring guide:
5 — Perfectly follows the rubric, nothing missing
4 — Mostly follows, minor omissions
3 — Partially follows, some important elements missing
2 — Mostly fails, major elements missing
1 — Completely fails the rubric

Response to evaluate:
{response}

Reply with ONLY valid JSON: {{"score": <1-5>, "reasoning": "<one sentence>"}}"""


def run_judge(response: str, rubric: str) -> dict:
    client = anthropic.Anthropic()
    result = client.messages.create(
        model=SONNET,
        max_tokens=200,
        messages=[{
            "role": "user",
            "content": _JUDGE_PROMPT.format(rubric=rubric, response=response),
        }],
    )
    text = result.content[0].text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        score_match = re.search(r'\b([1-5])\b', text)
        score = int(score_match.group(1)) if score_match else 1
        return {"score": score, "reasoning": text[:150]}
