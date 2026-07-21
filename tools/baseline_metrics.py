#!/usr/bin/env python3
"""
baseline_metrics.py

Defines and tracks key performance indicators (KPIs) for the Hermes ESRA loop.
Allows calculating current metrics and saving monthly historical snapshots.
"""

import json
from pathlib import Path
from datetime import datetime
import os

class BaselineMetrics:
    def __init__(self, logs_dir=None, snapshots_dir=None):
        self.logs_dir = Path(logs_dir or Path.home() / ".hermes" / "evolution-logs")
        self.snapshots_dir = Path(snapshots_dir or Path.home() / ".hermes" / "metrics-snapshots")
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)

    def define_kpis(self):
        """
        Returns a dictionary representing the target KPIs defined in the ROADMAP.
        These act as baselines/targets for tracking evolution quality.
        """
        return {
            "skill_quality": {
                "min_confidence": 0.8,
                "target_test_coverage_percent": 80,
                "reusability_score_target": 7.0 # Arbitrary 1-10 scale
            },
            "evolutionary_pace": {
                "target_cycles_per_day": 5.0,
                "target_new_skills_per_week": 2.0
            },
            "value_coherence": {
                "max_drift_allowed": 0.05 # 5% drift from core principles
            },
            "hermes_task_success_rate": {
                "target_with_evolved_skills": 0.95,
                "target_without_evolved_skills": 0.85
            }
        }

    def calculate_current_metrics(self):
        """
        Parses logs and attempts to extract real values to compare against KPIs.
        Since we have limited log data in this sandbox, this is a simplified calculation.
        """
        metrics = {
            "total_cycles_analyzed": 0,
            "avg_skill_confidence": 0.0,
            "estimated_cycles_per_day": 0.0,
            "value_drift_events": 0,
            "tasks_succeeded": 0
        }

        if not self.logs_dir.exists():
            return metrics

        logs = []
        for filepath in self.logs_dir.glob("*.json"):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    logs.append(json.load(f))
            except Exception:
                pass

        metrics["total_cycles_analyzed"] = len(logs)

        if logs:
            # Dummy logic for calculation based on what we can find in logs
            # In a real system, these would tie into complex evaluation skills.
            successes = sum(1 for log in logs if log.get("outputs", {}).get("success", False))
            metrics["tasks_succeeded"] = successes

            # Simple assumption: 1 cycle per day if we only have a few logs
            metrics["estimated_cycles_per_day"] = len(logs) / 1.0

        return metrics

    def take_monthly_snapshot(self):
        """
        Calculates current metrics and saves them to a monthly snapshot JSON file.
        """
        current_metrics = self.calculate_current_metrics()
        kpis = self.define_kpis()

        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "kpi_targets": kpis,
            "current_metrics": current_metrics
        }

        month_str = datetime.now().strftime("%Y-%m")
        filename = f"metrics_snapshot_{month_str}.json"
        filepath = self.snapshots_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=2, ensure_ascii=False)

        return str(filepath)

if __name__ == "__main__":
    tracker = BaselineMetrics()

    print("Defined KPIs:")
    print(json.dumps(tracker.define_kpis(), indent=2))

    print("\nTaking monthly snapshot...")
    snapshot_path = tracker.take_monthly_snapshot()
    print(f"Snapshot saved to: {snapshot_path}")
