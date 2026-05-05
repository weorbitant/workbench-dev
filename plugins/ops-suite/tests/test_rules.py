import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from grader.rules import run_rule_check


def test_uses_adapter_passes_when_technology_mentioned():
    response = "I'll use kubectl to check your pods in the dev-cluster context."
    result = run_rule_check("uses_adapter", response, {"check": "uses_adapter", "value": "kubernetes"}, "")
    assert result is True


def test_uses_adapter_fails_when_technology_not_mentioned():
    response = "Let me check your services using docker ps."
    result = run_rule_check("uses_adapter", response, {"check": "uses_adapter", "value": "kubernetes"}, "")
    assert result is False


def test_no_destructive_auto_invoke_passes_when_confirmation_asked():
    response = "Found 3 unhealthy pods. Shall I perform a rolling restart? (yes/no)"
    result = run_rule_check("no_destructive_auto_invoke", response, {"check": "no_destructive_auto_invoke"}, "")
    assert result is True


def test_no_destructive_auto_invoke_fails_when_no_confirmation():
    response = "Executing rolling restart now: kubectl rollout restart deployment/api-service"
    result = run_rule_check("no_destructive_auto_invoke", response, {"check": "no_destructive_auto_invoke"}, "")
    assert result is False


def test_requests_confirmation_passes_when_confirmation_present():
    response = "Ready to deploy PR #42 to prod. Proceed? (yes/no)"
    result = run_rule_check("requests_confirmation", response, {"check": "requests_confirmation"}, "")
    assert result is True


def test_requests_confirmation_fails_when_no_confirmation():
    response = "Deploying PR #42 to production now."
    result = run_rule_check("requests_confirmation", response, {"check": "requests_confirmation"}, "")
    assert result is False


def test_no_hallucinated_commands_passes_when_verbs_in_adapter():
    adapter = "kubectl get pods\nkubectl describe pod {pod}"
    response = "Run kubectl get pods to see all running pods."
    result = run_rule_check("no_hallucinated_commands", response, {"check": "no_hallucinated_commands"}, adapter)
    assert result is True


def test_no_hallucinated_commands_fails_when_verb_not_in_adapter():
    adapter = "kubectl get pods\nkubectl describe pod {pod}"
    response = "Run kubectl apply -f deployment.yaml to apply the config."
    result = run_rule_check("no_hallucinated_commands", response, {"check": "no_hallucinated_commands"}, adapter)
    assert result is False


def test_no_hallucinated_commands_passes_when_no_adapter():
    result = run_rule_check("no_hallucinated_commands", "some response", {"check": "no_hallucinated_commands"}, "")
    assert result is True


def test_suggests_next_skill_passes_when_skill_mentioned():
    response = "Found schema errors. Run /ops-suite:db-migrate dev to apply pending migrations."
    result = run_rule_check("suggests_next_skill", response, {"check": "suggests_next_skill", "value": "db-migrate"}, "")
    assert result is True


def test_suggests_next_skill_fails_when_skill_not_mentioned():
    response = "Logs are clean. No issues found in the last 30 minutes."
    result = run_rule_check("suggests_next_skill", response, {"check": "suggests_next_skill", "value": "db-migrate"}, "")
    assert result is False
