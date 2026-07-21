#!/usr/bin/env python3
import json
import argparse
from pathlib import Path
from collections import defaultdict

class EvolutionDashboard:
    def __init__(self, log_dir=None):
        if log_dir is None:
            self.log_dir = Path.home() / ".hermes" / "evolution-logs"
        else:
            self.log_dir = Path(log_dir)

    def load_logs(self):
        logs = []
        if not self.log_dir.exists():
            return logs

        for filepath in sorted(self.log_dir.glob("*.json")):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    logs.append(json.load(f))
            except Exception as e:
                print(f"Warning: Could not read {filepath}: {e}")
        return logs

    def calculate_metrics(self, logs):
        metrics = {
            "total_cycles": len(logs),
            "successful_cycles": 0,
            "success_rate": 0.0,
            "new_skills_created": 0,
            "improvements_applied": 0,
            "value_changes_count": 0,
            "anomalies_count": 0,
            "crisis_interventions_count": 0,
            "skill_genealogy": defaultdict(list),
        }

        if not logs:
            return metrics

        for log in logs:
            outputs = log.get("outputs", {})
            if outputs.get("success", False):
                metrics["successful_cycles"] += 1

            metrics["new_skills_created"] += len(outputs.get("new_skills_created", []))
            metrics["improvements_applied"] += len(outputs.get("improvements_applied", []))
            metrics["value_changes_count"] += len(outputs.get("value_changes", []))
            metrics["anomalies_count"] += len(outputs.get("anomalies", []))
            metrics["crisis_interventions_count"] += len(outputs.get("crisis_interventions", []))

            # Very basic skill genealogy mapping: "from" -> "to"
            # Assumes output "new_skills_created" or input "skills_activated" might have this relation.
            # In a real implementation this might be more structured.
            # Here we just track what skills were activated when a new skill was created.
            new_skills = outputs.get("new_skills_created", [])
            activated_skills = log.get("orchestrator_decisions", {}).get("skills_activated", [])

            for new_skill in new_skills:
                for activated in activated_skills:
                    if new_skill not in metrics["skill_genealogy"][activated]:
                        metrics["skill_genealogy"][activated].append(new_skill)

        if metrics["total_cycles"] > 0:
            metrics["success_rate"] = (metrics["successful_cycles"] / metrics["total_cycles"]) * 100

        return metrics

    def display_dashboard(self):
        logs = self.load_logs()
        metrics = self.calculate_metrics(logs)

        print("="*50)
        print(" " * 12 + "ESRA Evolution Dashboard")
        print("="*50)
        print(f"Total Cycles:           {metrics['total_cycles']}")
        print(f"Success Rate:           {metrics['success_rate']:.1f}% ({metrics['successful_cycles']} successful)")
        print("-"*50)
        print(f"New Skills Created:     {metrics['new_skills_created']}")
        print(f"Improvements Applied:   {metrics['improvements_applied']}")
        print(f"Value Stability:        {metrics['value_changes_count']} value changes detected")
        print(f"Anomalies Detected:     {metrics['anomalies_count']}")
        print(f"Crisis Interventions:   {metrics['crisis_interventions_count']}")
        print("-"*50)

        print("Skill Genealogy (Parent -> Child):")
        if not metrics["skill_genealogy"]:
            print("  No genealogy data available.")
        else:
            for parent, children in metrics["skill_genealogy"].items():
                print(f"  {parent} -> {', '.join(children)}")
        print("="*50)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ESRA Evolution Dashboard")
    parser.add_argument("--log-dir", help="Custom log directory path")
    args = parser.parse_args()

    dashboard = EvolutionDashboard(args.log_dir)
    dashboard.display_dashboard()
