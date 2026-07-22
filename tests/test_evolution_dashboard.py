import os
import json
import pytest
import tempfile
import importlib
from pathlib import Path
from tools.esra_logger import ESRALogger

# Import module with dash in name
evolution_dashboard = importlib.import_module("tools.evolution-dashboard")
EvolutionDashboard = evolution_dashboard.EvolutionDashboard

def test_dashboard_aggregates():
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = ESRALogger(log_dir=tmpdir)

        # Log some cycle data
        # Cycle 1: Success with new skill
        logger.log_cycle(
            {"task_complexity": 8, "prior_success_rate": 1.0, "skills_available": ["parent-skill"]},
            {"skills_activated": ["parent-skill"], "meta_loop_stage": "ACT"},
            {"new_skills_created": ["child-skill"], "improvements_applied": ["parent-skill"], "success": True},
            {"duration_seconds": 2.0}
        )
        # Cycle 2: Failed cycle
        logger.log_cycle(
            {"task_complexity": 9, "prior_success_rate": 0.5, "skills_available": []},
            {"skills_activated": [], "meta_loop_stage": "DECIDE"},
            {"success": False, "anomalies": ["timeout"]},
            {"duration_seconds": 1.0}
        )

        dashboard = EvolutionDashboard(log_dir=tmpdir)
        logs = dashboard.load_logs()
        assert len(logs) == 2

        metrics = dashboard.calculate_metrics(logs)
        assert metrics["total_cycles"] == 2
        assert metrics["successful_cycles"] == 1
        assert metrics["success_rate"] == 50.0
        assert metrics["new_skills_created"] == 1
        assert metrics["improvements_applied"] == 1
        assert metrics["anomalies_count"] == 1

        # Verify genealogy mapping: parent-skill -> child-skill
        assert "child-skill" in metrics["skill_genealogy"]["parent-skill"]

def test_display_dashboard_empty(capsys):
    with tempfile.TemporaryDirectory() as tmpdir:
        dashboard = EvolutionDashboard(log_dir=tmpdir)
        dashboard.display_dashboard()
        captured = capsys.readouterr()
        assert "ESRA Evolution Dashboard" in captured.out
        assert "💡 No evolution cycles have been recorded yet." in captured.out
        assert "python tools/evolution-hook.py" in captured.out

def test_display_dashboard_populated(capsys):
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = ESRALogger(log_dir=tmpdir)
        logger.log_cycle(
            {"task_complexity": 5, "prior_success_rate": 1.0, "skills_available": []},
            {"skills_activated": [], "meta_loop_stage": "ACT"},
            {"success": True},
            {"duration_seconds": 1.0}
        )
        dashboard = EvolutionDashboard(log_dir=tmpdir)
        dashboard.display_dashboard()
        captured = capsys.readouterr()
        assert "ESRA Evolution Dashboard" in captured.out
        assert "Total Cycles:" in captured.out
        assert "Success Rate:" in captured.out
        assert "[████████████████████]" in captured.out  # 100% success rate bar
