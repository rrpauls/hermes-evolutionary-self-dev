import os
import json
import pytest
import tempfile
from pathlib import Path
from tools.hermes_integration import (
    HermesPluginInterface,
    AutomaticEvolutionTrigger,
    SkillInjector,
    ESRAFeedbackLoop
)


def test_hermes_plugin_interface():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_home = Path(tmpdir)
        interface = HermesPluginInterface(hermes_home=tmp_home)

        # Test query_hermes_state
        state = interface.query_hermes_state()
        assert state["status"] == "active"
        assert "loaded_skills_count" in state
        assert "active_plugins" in state

        # Test suggest_config_changes
        changes = {"model": "gpt-4o", "temperature": 0.2}
        config_path = interface.suggest_config_changes(changes)

        assert config_path.exists()
        assert (os.stat(config_path).st_mode & 0o777) == 0o600

        data = json.loads(config_path.read_text(encoding="utf-8"))
        assert data["changes"] == changes
        assert data["applied"] is False


def test_hermes_plugin_post_task_hook():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_home = Path(tmpdir)
        interface = HermesPluginInterface(hermes_home=tmp_home)

        # High complexity task
        task_context = {"summary": "Advanced security refactoring"}
        result = {"success": True, "confidence": 0.95}
        metrics = {"complexity": 9, "duration_seconds": 3.4}

        res = interface.post_task_hook(task_context, result, metrics)
        assert "trigger_decision" in res
        assert res["trigger_decision"] is True


def test_automatic_evolution_trigger_aggressiveness():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_home = Path(tmpdir)

        # 1. High aggressiveness
        trigger_high = AutomaticEvolutionTrigger(aggressiveness="high", hermes_home=tmp_home)
        # Moderate complexity, no errors -> should trigger in high aggressiveness
        task_context = {"summary": "test task"}
        metrics = {"complexity": 4, "error_count": 0}
        assert trigger_high.should_trigger(task_context, metrics) is True

        # 2. Low aggressiveness
        trigger_low = AutomaticEvolutionTrigger(aggressiveness="low", hermes_home=tmp_home)
        # Moderate complexity -> should not trigger in low aggressiveness
        assert trigger_low.should_trigger(task_context, metrics) is False

        # High complexity (9) -> should trigger in low aggressiveness
        task_high_comp = {"complexity": 9}
        assert trigger_low.should_trigger(task_high_comp, metrics) is True

        # 3. Post task trigger output
        post_res = trigger_high.post_task_trigger(task_context, {}, metrics)
        assert post_res["trigger_decision"] is True
        assert "aggressiveness" in post_res
        assert post_res["aggressiveness"] == "high"


def test_skill_injector():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_skills = Path(tmpdir)
        injector = SkillInjector(skills_dir=tmp_skills)

        # Test hot_reload_skill (checks file existence fallback for non-loaded modules)
        assert injector.hot_reload_skill("non-existent-skill") is False

        # Test version_skill
        code = "---\nname: test-skill\ndescription: test\n---\n# Test"
        skill_path = injector.version_skill("test-skill", code, version=3)
        assert skill_path.exists()
        assert (os.stat(skill_path).st_mode & 0o777) == 0o600
        assert skill_path.read_text(encoding="utf-8") == code

        # Now hot_reload_skill should find it
        assert injector.hot_reload_skill("test-skill-v3") is True

        # Test A/B testing
        ab_res = injector.ab_test_skills(
            skill_v1="test-skill-v1",
            skill_v2="test-skill-v2",
            task={"summary": "Evaluate refactoring"},
            num_trials=3
        )
        assert "winner" in ab_res
        assert ab_res["trials"] == 3
        assert "avg_confidence" in ab_res["results"]["test-skill-v1"]


def test_esra_feedback_loop():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_config = Path(tmpdir)
        feedback = ESRAFeedbackLoop(config_dir=tmp_config)

        # Test update_system_prompt
        prompt_path = feedback.update_system_prompt("New System Instruction Set")
        assert prompt_path.exists()
        assert (os.stat(prompt_path).st_mode & 0o777) == 0o600
        assert prompt_path.read_text(encoding="utf-8") == "New System Instruction Set"

        # Test propagate_values_to_instructions
        values = ["Honesty", "Safety", "Antifragility"]
        prompt_path = feedback.propagate_values_to_instructions(values)
        content = prompt_path.read_text(encoding="utf-8")
        assert "[CORE VALUE] Honesty" in content
        assert "[CORE VALUE] Safety" in content
        assert "[CORE VALUE] Antifragility" in content

        # Test document_decision_point (multiple writes append)
        trace_path = feedback.document_decision_point("D-01", ["Step 1: OODA", "Step 2: Act"])
        assert trace_path.exists()
        assert (os.stat(trace_path).st_mode & 0o777) == 0o600

        # Append another
        feedback.document_decision_point("D-02", ["Step 1: Reflect"])
        traces = json.loads(trace_path.read_text(encoding="utf-8"))
        assert len(traces) == 2
        assert traces[0]["decision_id"] == "D-01"
        assert traces[1]["decision_id"] == "D-02"
