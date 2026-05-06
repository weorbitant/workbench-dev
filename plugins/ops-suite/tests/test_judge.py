import sys
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
sys.path.insert(0, str(Path(__file__).parent))

from grader.judge import run_judge


def test_run_judge_returns_score_and_reasoning():
    mock_msg = MagicMock()
    mock_msg.content = [MagicMock(text='{"score": 4, "reasoning": "Shows pod health but omitted memory metrics."}')]

    with patch("grader.judge.anthropic.Anthropic") as MockAnthropic:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_msg
        MockAnthropic.return_value = mock_client

        result = run_judge(
            response="Pod is Running with 0 restarts. CPU: 12m.",
            rubric="Shows pod health, restarts, CPU and memory.",
        )

    assert result["score"] == 4
    assert "memory" in result["reasoning"]


def test_run_judge_handles_malformed_json():
    mock_msg = MagicMock()
    mock_msg.content = [MagicMock(text='score is 3, looks mostly correct')]

    with patch("grader.judge.anthropic.Anthropic") as MockAnthropic:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_msg
        MockAnthropic.return_value = mock_client

        result = run_judge(response="some response", rubric="some rubric")

    assert "score" in result
    assert "reasoning" in result
    assert isinstance(result["score"], int)
