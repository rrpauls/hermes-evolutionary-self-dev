import os
import json
import pytest
import tempfile
import importlib
from pathlib import Path

# Import module with dash in name
evolution_hook = importlib.import_module("tools.evolution-hook")
EvolutionHook = evolution_hook.EvolutionHook

def test_hook_history_permissions():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_home = Path(tmpdir)
        hook = EvolutionHook(hermes_home=tmp_home)

        # Verify history file was created and has 0o600 permissions
        assert hook.history_file.exists()
        mode = os.stat(hook.history_file).st_mode & 0o777
        assert mode == 0o600, f"Expected permissions 0o600, got {oct(mode)}"

def test_hook_should_trigger():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_home = Path(tmpdir)
        hook = EvolutionHook(hermes_home=tmp_home)

        # Test 1: Explicit request always triggers
        ctx_explicit = {"explicit_evolution_request": True}
        assert hook.should_trigger_orchestrator(ctx_explicit) is True

        # Test 2: New skill created always triggers
        ctx_new_skill = {"new_skill_created": True}
        assert hook.should_trigger_orchestrator(ctx_new_skill) is True

        # Test 3: High complexity triggers
        ctx_complexity = {"complexity": 8}
        assert hook.should_trigger_orchestrator(ctx_complexity) is True

        # Test 4: Low confidence triggers
        ctx_low_conf = {"confidence": 0.5}
        assert hook.should_trigger_orchestrator(ctx_low_conf) is True

        # Test 5: Standard simple task without triggers does not trigger
        ctx_simple = {"summary": "doing nothing", "complexity": 3, "confidence": 0.9}
        assert hook.should_trigger_orchestrator(ctx_simple) is False

def test_hook_rate_limiting_and_history():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_home = Path(tmpdir)
        hook = EvolutionHook(hermes_home=tmp_home)

        # Record 4 events that triggered
        for i in range(4):
            hook.record_evolution_event({
                "triggered": True,
                "task_context": {"keywords": ["esra", "test"]}
            })

        # Rate limit should trigger now and return False for general triggers (since >=3 recent triggers exist)
        ctx_simple = {"summary": "simple task", "complexity": 3, "confidence": 0.9}
        assert hook.should_trigger_orchestrator(ctx_simple) is False

        # But explicit requests or new skill creation still override rate limit!
        ctx_explicit = {"explicit_evolution_request": True}
        assert hook.should_trigger_orchestrator(ctx_explicit) is True

def test_hook_pattern_analysis():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_home = Path(tmpdir)
        hook = EvolutionHook(hermes_home=tmp_home)

        # Record events with keywords
        for i in range(3):
            hook.record_evolution_event({
                "triggered": True,
                "task_context": {"keywords": ["database", "indexing"]}
            })
        for i in range(2):
            hook.record_evolution_event({
                "triggered": True,
                "task_context": {"keywords": ["security"]}
            })

        analysis = hook.analyze_recent_patterns()
        assert analysis["status"] == "ok"
        assert analysis["triggered_count"] == 5
        assert analysis["same_area_repeated"] is True
