import os
import json
import pytest
import tempfile
from pathlib import Path
from tools.baseline_metrics import BaselineMetrics
from tools.esra_logger import ESRALogger

def test_kpi_definition():
    tracker = BaselineMetrics()
    kpis = tracker.define_kpis()
    assert "skill_quality" in kpis
    assert "evolutionary_pace" in kpis
    assert kpis["skill_quality"]["target_test_coverage_percent"] == 80

def test_calculate_metrics_and_snapshot():
    with tempfile.TemporaryDirectory() as tmpdir:
        logs_dir = Path(tmpdir) / "logs"
        snapshots_dir = Path(tmpdir) / "snapshots"

        # Create some logs first
        logger = ESRALogger(log_dir=logs_dir)
        logger.log_cycle(
            {"task_complexity": 8, "prior_success_rate": 0.9, "skills_available": []},
            {"skills_activated": [], "meta_loop_stage": "ACT"},
            {"success": True},
            {"duration_seconds": 1.2}
        )
        logger.log_cycle(
            {"task_complexity": 6, "prior_success_rate": 0.8, "skills_available": []},
            {"skills_activated": [], "meta_loop_stage": "ACT"},
            {"success": False},
            {"duration_seconds": 0.8}
        )

        tracker = BaselineMetrics(logs_dir=logs_dir, snapshots_dir=snapshots_dir)
        metrics = tracker.calculate_current_metrics()

        assert metrics["total_cycles_analyzed"] == 2
        assert metrics["tasks_succeeded"] == 1

        snapshot_file = tracker.take_monthly_snapshot()
        assert os.path.exists(snapshot_file)

        with open(snapshot_file, "r", encoding="utf-8") as f:
            snapshot_data = json.load(f)

        assert "timestamp" in snapshot_data
        assert "kpi_targets" in snapshot_data
        assert "current_metrics" in snapshot_data
        assert snapshot_data["current_metrics"]["total_cycles_analyzed"] == 2
