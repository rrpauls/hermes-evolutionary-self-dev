import os
import time
import pytest
import tempfile
import importlib
from pathlib import Path
from tools.esra_logger import ESRALogger
from tools.baseline_metrics import BaselineMetrics

# Import hook with importlib
evolution_hook = importlib.import_module("tools.evolution-hook")
EvolutionHook = evolution_hook.EvolutionHook

def test_stress_consecutive_cycles():
    """Simulates 60 rapid consecutive ESRA loops to stress test performance and logging limits."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        logger = ESRALogger(log_dir=tmp_path / "logs")

        # Log 60 times in rapid succession
        start_time = time.time()
        for i in range(60):
            logger.log_cycle(
                {"task_complexity": 7 + (i % 3), "prior_success_rate": 0.95, "skills_available": ["test"]},
                {"skills_activated": ["self-observer", "self-improver"], "meta_loop_stage": "ACT"},
                {"new_skills_created": [f"skill-{i}"], "success": True},
                {"duration_seconds": 0.05}
            )
        end_time = time.time()

        # Verify 60 log files exist
        log_files = list((tmp_path / "logs").glob("*.json"))
        assert len(log_files) == 60

        # Ensure all files were written with correct permissions (0o600)
        for f in log_files:
            assert (os.stat(f).st_mode & 0o777) == 0o600

        print(f"Stress test complete: wrote 60 files in {end_time - start_time:.4f} seconds.")

def test_stress_retention_and_rotation():
    """Stress tests the retention policy with a mixture of many old and new log files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        logger = ESRALogger(log_dir=tmp_path)

        # Create 100 mock files
        # 40 old files (>30 days), 60 new files
        old_time = time.time() - (32 * 24 * 60 * 60)
        new_time = time.time() - (2 * 24 * 60 * 60)

        for i in range(100):
            f = tmp_path / f"esra_cycle_stress_{i}.json"
            f.write_text("{}", encoding="utf-8")
            if i < 40:
                os.utime(f, (old_time, old_time))
            else:
                os.utime(f, (new_time, new_time))

        # Run cleanup
        logger.clean_old_logs()

        remaining_files = list(tmp_path.glob("*.json"))
        # Only the 60 new files should remain!
        assert len(remaining_files) == 60
        for f in remaining_files:
            assert "stress_" in f.name

def test_scenario_sequence_execution():
    """Simulates a complete 5-task evolutionary context sequence via the hook and metric calculator."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_home = Path(tmpdir)
        hook = EvolutionHook(hermes_home=tmp_home)
        logger = ESRALogger(log_dir=tmp_home / "evolution-logs")
        tracker = BaselineMetrics(logs_dir=tmp_home / "evolution-logs", snapshots_dir=tmp_home / "snapshots")

        # Scenario:
        # Task 1: High complexity task -> Triggers orchestrator
        task_1 = {"summary": "Implement secure auth module", "complexity": 9, "new_skill_created": True}
        res_1 = hook.trigger_orchestrator(task_1)
        assert res_1["trigger_decision"] is True
        # Log this cycle
        logger.log_cycle(
            {"task_complexity": 9, "prior_success_rate": 0.8, "skills_available": []},
            {"skills_activated": ["hermes-codebase-engineer"], "meta_loop_stage": "ACT"},
            {"new_skills_created": ["secure-auth"], "success": True},
            {"duration_seconds": 2.5}
        )

        # Task 2: Simple low-complexity task -> Does not trigger
        task_2 = {"summary": "Fix typo in doc", "complexity": 2}
        res_2 = hook.trigger_orchestrator(task_2)
        assert res_2["trigger_decision"] is False

        # Task 3: Another complex task -> Triggers orchestrator
        task_3 = {"summary": "Refactor database migrations", "complexity": 8}
        res_3 = hook.trigger_orchestrator(task_3)
        assert res_3["trigger_decision"] is True
        logger.log_cycle(
            {"task_complexity": 8, "prior_success_rate": 0.85, "skills_available": ["secure-auth"]},
            {"skills_activated": ["hermes-codebase-engineer"], "meta_loop_stage": "ACT"},
            {"new_skills_created": ["db-migrations"], "success": True},
            {"duration_seconds": 1.8}
        )

        # Task 4: Explicit request -> Triggers orchestrator
        task_4 = {"summary": "Review the loop performance", "explicit_evolution_request": True}
        res_4 = hook.trigger_orchestrator(task_4)
        assert res_4["trigger_decision"] is True
        logger.log_cycle(
            {"task_complexity": 5, "prior_success_rate": 0.9, "skills_available": ["db-migrations", "secure-auth"]},
            {"skills_activated": ["loop-auditor"], "meta_loop_stage": "ACT"},
            {"improvements_applied": ["loop-performance"], "success": True},
            {"duration_seconds": 3.0}
        )

        # Calculate current metrics and verify
        metrics = tracker.calculate_current_metrics()
        assert metrics["total_cycles_analyzed"] == 3
        assert metrics["tasks_succeeded"] == 3
