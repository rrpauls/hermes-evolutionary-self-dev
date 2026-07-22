#!/usr/bin/env python3
import os
import sys
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

        use_color = sys.stdout.isatty() and "NO_COLOR" not in os.environ

        # Standard ANSI escape codes
        CLR_RESET = "\033[0m" if use_color else ""
        CLR_BOLD = "\033[1m" if use_color else ""
        CLR_CYAN = "\033[36m" if use_color else ""
        CLR_GREEN = "\033[32m" if use_color else ""
        CLR_YELLOW = "\033[33m" if use_color else ""
        CLR_RED = "\033[31m" if use_color else ""

        if metrics["total_cycles"] == 0:
            print("="*50)
            print(" " * 12 + f"{CLR_BOLD}ESRA Evolution Dashboard{CLR_RESET}")
            print("="*50)
            print(f"\n{CLR_YELLOW}💡 No evolution cycles have been recorded yet.{CLR_RESET}")
            print("To run your first ESRA cycle and see evolution metrics, execute:")
            print(f"  {CLR_BOLD}python tools/evolution-hook.py{CLR_RESET}\n")
            print("="*50)
            return

        # Determine success rate and color
        success_rate = metrics["success_rate"]
        if success_rate >= 80.0:
            rate_color = CLR_GREEN
        elif success_rate >= 50.0:
            rate_color = CLR_YELLOW
        else:
            rate_color = CLR_RED

        # Progress bar construction
        bar_width = 20
        filled_len = int(round(bar_width * success_rate / 100))
        bar = "█" * filled_len + "░" * (bar_width - filled_len)
        progress_bar = f"{rate_color}[{bar}]{CLR_RESET} {CLR_BOLD}{success_rate:.1f}%{CLR_RESET}"

        # Anomaly and crisis intervention formatting
        anomaly_str = f"{CLR_YELLOW}{metrics['anomalies_count']}{CLR_RESET}" if metrics["anomalies_count"] > 0 else f"{metrics['anomalies_count']}"
        crisis_str = f"{CLR_RED}{metrics['crisis_interventions_count']}{CLR_RESET}" if metrics["crisis_interventions_count"] > 0 else f"{metrics['crisis_interventions_count']}"
        skills_str = f"{CLR_GREEN}{metrics['new_skills_created']}{CLR_RESET}" if metrics["new_skills_created"] > 0 else f"{metrics['new_skills_created']}"
        improvements_str = f"{CLR_GREEN}{metrics['improvements_applied']}{CLR_RESET}" if metrics["improvements_applied"] > 0 else f"{metrics['improvements_applied']}"

        print("="*50)
        print(" " * 12 + f"{CLR_CYAN}{CLR_BOLD}ESRA Evolution Dashboard{CLR_RESET}")
        print("="*50)
        print(f"Total Cycles:           {CLR_BOLD}{metrics['total_cycles']}{CLR_RESET}")
        print(f"Success Rate:           {progress_bar} ({metrics['successful_cycles']} successful)")
        print("-"*50)
        print(f"New Skills Created:     {skills_str}")
        print(f"Improvements Applied:   {improvements_str}")
        print(f"Value Stability:        {metrics['value_changes_count']} value changes detected")
        print(f"Anomalies Detected:     {anomaly_str}")
        print(f"Crisis Interventions:   {crisis_str}")
        print("-"*50)

        print(f"{CLR_BOLD}Skill Genealogy (Parent -> Child):{CLR_RESET}")
        if not metrics["skill_genealogy"]:
            print("  No genealogy data available.")
        else:
            for parent, children in metrics["skill_genealogy"].items():
                print(f"  {CLR_CYAN}{parent}{CLR_RESET} -> {', '.join(children)}")
        print("="*50)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ESRA Evolution Dashboard")
    parser.add_argument("--log-dir", help="Custom log directory path")
    args = parser.parse_args()

    dashboard = EvolutionDashboard(args.log_dir)
    dashboard.display_dashboard()
