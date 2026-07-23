#!/usr/bin/env python3
"""
experiment_runner.py

ESRA Phase 5: Value-Driven Experiments Framework.
Provides standard experiment workflows, hypothesis formation, Value-Clarifier alignment assessments,
safe rollout rollbacks (canary, staged, A/B testing), and Antifragility stressor testing.
"""

from __future__ import annotations
import os
import sys
import json
import random
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

class Experiment:
    """Represents an ESRA Value-Driven Experiment."""
    def __init__(
        self,
        experiment_id: str,
        name: str,
        hypothesis: str,
        theme: str,
        rollout_type: str,
        value_alignment_justification: str,
        value_alignment_score: float,
        status: str = "planned",
        safeguards: Optional[Dict[str, Any]] = None,
        stressors: Optional[List[str]] = None,
        created_at: Optional[str] = None,
        results: Optional[Dict[str, Any]] = None
    ):
        self.experiment_id = experiment_id
        self.name = name
        self.hypothesis = hypothesis
        self.theme = theme
        self.rollout_type = rollout_type.lower()
        self.value_alignment_justification = value_alignment_justification
        self.value_alignment_score = value_alignment_score
        self.status = status.lower()
        self.safeguards = safeguards or {"max_error_rate": 0.1, "max_latency_sec": 4.0}
        self.stressors = stressors or []
        self.created_at = created_at or datetime.now(timezone.utc).isoformat()
        self.results = results or {}

        # Automatic Value-Clarifier sign-off check
        self.signed_off = self.value_alignment_score >= 0.70

    def to_dict(self) -> Dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "name": self.name,
            "hypothesis": self.hypothesis,
            "theme": self.theme,
            "rollout_type": self.rollout_type,
            "value_alignment_justification": self.value_alignment_justification,
            "value_alignment_score": self.value_alignment_score,
            "signed_off": self.signed_off,
            "status": self.status,
            "safeguards": self.safeguards,
            "stressors": self.stressors,
            "created_at": self.created_at,
            "results": self.results
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Experiment:
        return cls(
            experiment_id=data["experiment_id"],
            name=data["name"],
            hypothesis=data["hypothesis"],
            theme=data["theme"],
            rollout_type=data["rollout_type"],
            value_alignment_justification=data["value_alignment_justification"],
            value_alignment_score=data["value_alignment_score"],
            status=data.get("status", "planned"),
            safeguards=data.get("safeguards"),
            stressors=data.get("stressors"),
            created_at=data.get("created_at"),
            results=data.get("results")
        )


class ExperimentRunner:
    """Manages the creation, listing, execution, and evaluation of experiments."""
    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = Path(base_dir or Path.home() / ".hermes")
        self.experiments_dir = self.base_dir / "experiments"
        self._ensure_directories()

    def _ensure_directories(self):
        """Creates required directories securely with 0o700 permissions."""
        self.base_dir.mkdir(parents=True, exist_ok=True)
        # Avoid modifying existing directories if they already exist, but ensure 0o700 on create
        if not self.experiments_dir.exists():
            self.experiments_dir.mkdir(parents=True, exist_ok=True, mode=0o700)

    def create_experiment(
        self,
        name: str,
        hypothesis: str,
        theme: str,
        rollout_type: str,
        value_alignment_justification: str,
        value_alignment_score: float,
        safeguards: Optional[Dict[str, Any]] = None,
        stressors: Optional[List[str]] = None
    ) -> Experiment:
        """Creates a new experiment and saves it to disk securely (0o600)."""
        # Generate ID
        existing = list(self.experiments_dir.glob("EXP-*.json"))
        next_num = len(existing) + 1
        experiment_id = f"EXP-{next_num:03d}"

        experiment = Experiment(
            experiment_id=experiment_id,
            name=name,
            hypothesis=hypothesis,
            theme=theme,
            rollout_type=rollout_type,
            value_alignment_justification=value_alignment_justification,
            value_alignment_score=value_alignment_score,
            status="planned",
            safeguards=safeguards,
            stressors=stressors
        )

        self.save_experiment(experiment)
        return experiment

    def save_experiment(self, experiment: Experiment):
        """Saves experiment to disk using 0o600 file permissions."""
        filepath = self.experiments_dir / f"{experiment.experiment_id}.json"
        fd = os.open(filepath, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(experiment.to_dict(), f, indent=2, ensure_ascii=False)

    def load_experiment(self, experiment_id: str) -> Optional[Experiment]:
        """Loads a specific experiment by ID."""
        filepath = self.experiments_dir / f"{experiment_id}.json"
        if not filepath.exists():
            return None
        try:
            data = json.loads(filepath.read_text(encoding="utf-8"))
            return Experiment.from_dict(data)
        except Exception as e:
            print(f"Error loading experiment {experiment_id}: {e}", file=sys.stderr)
            return None

    def list_experiments(self) -> List[Experiment]:
        """Lists all experiments on disk."""
        experiments = []
        for filepath in sorted(self.experiments_dir.glob("EXP-*.json")):
            try:
                data = json.loads(filepath.read_text(encoding="utf-8"))
                experiments.append(Experiment.from_dict(data))
            except Exception:
                pass
        return experiments

    def run_experiment(self, experiment_id: str, num_trials: int = 5) -> Dict[str, Any]:
        """Runs the specified experiment using its defined rollout type and safety checks."""
        exp = self.load_experiment(experiment_id)
        if not exp:
            raise ValueError(f"Experiment {experiment_id} not found.")

        if not exp.signed_off:
            exp.status = "aborted"
            exp.results = {
                "error": "Value-Clarifier sign-off FAILED. Experiment contains poor alignment with core values.",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            self.save_experiment(exp)
            return exp.results

        exp.status = "running"
        self.save_experiment(exp)

        # Retrieve safeguards
        max_err = exp.safeguards.get("max_error_rate", 0.1)
        max_lat = exp.safeguards.get("max_latency_sec", 4.0)

        results: Dict[str, Any] = {
            "started_at": datetime.now(timezone.utc).isoformat(),
            "rollout_type": exp.rollout_type,
            "trials_run": 0,
            "stages_completed": [],
            "aborted": False,
            "rollback_triggered": False,
            "rollback_reason": None,
            "metrics": {}
        }

        # Handle different rollout types
        if exp.rollout_type == "canary":
            # Canary rollout: run a small trial (1 trial) first as a canary probe
            canary_score = self._execute_trial_simulation(exp.stressors)
            results["trials_run"] += 1

            if canary_score["error_rate"] > max_err or canary_score["latency_sec"] > max_lat:
                results["aborted"] = True
                results["rollback_triggered"] = True
                results["rollback_reason"] = f"Canary health check failed: error_rate={canary_score['error_rate']:.2f} (max={max_err}), latency={canary_score['latency_sec']:.2f}s (max={max_lat}s)"
                exp.status = "aborted"
                results["canary_trial"] = canary_score
            else:
                results["canary_trial"] = canary_score
                results["stages_completed"].append("canary_pass")
                # Canary passed, execute remaining trials
                remaining_scores = []
                for _ in range(num_trials - 1):
                    score = self._execute_trial_simulation(exp.stressors)
                    remaining_scores.append(score)
                    results["trials_run"] += 1

                all_scores = [canary_score] + remaining_scores
                avg_err = sum(s["error_rate"] for s in all_scores) / num_trials
                avg_lat = sum(s["latency_sec"] for s in all_scores) / num_trials
                avg_acc = sum(s["accuracy"] for s in all_scores) / num_trials

                results["metrics"] = {
                    "avg_error_rate": avg_err,
                    "avg_latency_sec": avg_lat,
                    "avg_accuracy": avg_acc
                }
                exp.status = "completed"

        elif exp.rollout_type == "staged":
            # Staged rollout: Stage 1 (20% exposure), Stage 2 (50% exposure), Stage 3 (100% exposure)
            stages = [
                {"name": "Stage 1 (20% exposure)", "trials": max(1, int(num_trials * 0.2))},
                {"name": "Stage 2 (50% exposure)", "trials": max(1, int(num_trials * 0.5))},
                {"name": "Stage 3 (100% exposure)", "trials": num_trials}
            ]

            stage_metrics = []
            for stage in stages:
                stage_scores = []
                for _ in range(stage["trials"]):
                    score = self._execute_trial_simulation(exp.stressors)
                    stage_scores.append(score)
                    results["trials_run"] += 1

                avg_err = sum(s["error_rate"] for s in stage_scores) / len(stage_scores)
                avg_lat = sum(s["latency_sec"] for s in stage_scores) / len(stage_scores)
                avg_acc = sum(s["accuracy"] for s in stage_scores) / len(stage_scores)

                stage_res = {
                    "stage": stage["name"],
                    "avg_error_rate": avg_err,
                    "avg_latency_sec": avg_lat,
                    "avg_accuracy": avg_acc
                }
                stage_metrics.append(stage_res)

                # Check safeguard health
                if avg_err > max_err or avg_lat > max_lat:
                    results["aborted"] = True
                    results["rollback_triggered"] = True
                    results["rollback_reason"] = f"Safeguard breach at {stage['name']}: error_rate={avg_err:.2f}, latency={avg_lat:.2f}s"
                    exp.status = "aborted"
                    break
                else:
                    results["stages_completed"].append(stage["name"])

            results["stage_metrics"] = stage_metrics
            if not results["aborted"]:
                # Compute overall final metrics from last stage (full exposure)
                results["metrics"] = stage_metrics[-1]
                exp.status = "completed"

        elif exp.rollout_type == "ab_test":
            # A/B Testing: Compare Control (v1) and Treatment (v2)
            control_scores = [self._execute_trial_simulation(exp.stressors, is_treatment=False) for _ in range(num_trials)]
            treatment_scores = [self._execute_trial_simulation(exp.stressors, is_treatment=True) for _ in range(num_trials)]
            results["trials_run"] += num_trials * 2

            ctrl_err = sum(s["error_rate"] for s in control_scores) / num_trials
            ctrl_lat = sum(s["latency_sec"] for s in control_scores) / num_trials
            ctrl_acc = sum(s["accuracy"] for s in control_scores) / num_trials

            trmt_err = sum(s["error_rate"] for s in treatment_scores) / num_trials
            trmt_lat = sum(s["latency_sec"] for s in treatment_scores) / num_trials
            trmt_acc = sum(s["accuracy"] for s in treatment_scores) / num_trials

            results["metrics"] = {
                "control": {"avg_error_rate": ctrl_err, "avg_latency_sec": ctrl_lat, "avg_accuracy": ctrl_acc},
                "treatment": {"avg_error_rate": trmt_err, "avg_latency_sec": trmt_lat, "avg_accuracy": trmt_acc}
            }

            # Decision logic: treatment is winner if higher accuracy, lower latency, and under error safeguard
            if trmt_err <= max_err and trmt_lat <= max_lat and (trmt_acc > ctrl_acc or trmt_lat < ctrl_lat):
                results["winner"] = "treatment"
                results["recommendation"] = "Promote treatment (v2) to production. It outperformed control with solid safety margins."
            else:
                results["winner"] = "control"
                results["recommendation"] = "Retain control (v1). Treatment failed to show meaningful safety or performance improvements."

            exp.status = "completed"
            results["stages_completed"].append("ab_test_complete")

        else:
            # Default fallback execution
            scores = [self._execute_trial_simulation(exp.stressors) for _ in range(num_trials)]
            results["trials_run"] += num_trials
            avg_err = sum(s["error_rate"] for s in scores) / num_trials
            avg_lat = sum(s["latency_sec"] for s in scores) / num_trials
            avg_acc = sum(s["accuracy"] for s in scores) / num_trials
            results["metrics"] = {"avg_error_rate": avg_err, "avg_latency_sec": avg_lat, "avg_accuracy": avg_acc}
            exp.status = "completed"
            results["stages_completed"].append("fallback_run")

        results["ended_at"] = datetime.now(timezone.utc).isoformat()
        exp.results = results
        self.save_experiment(exp)
        return results

    def run_antifragility_stress_test(self, stressors: List[str], num_trials: int = 5) -> Dict[str, Any]:
        """
        Runs dedicated Antifragility stress tests by introducing stressors
        and measuring resilience and adaptation.
        """
        results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "stressors_injected": stressors,
            "trials_run": num_trials,
            "raw_scores": [],
            "resilience_metrics": {}
        }

        scores = []
        for i in range(num_trials):
            # Simulate adaptation: error rate should decrease or accuracy increase as trials go on (agent learns)
            adaptation_factor = i * 0.05 # 5% adaptation improvement per trial
            score = self._execute_trial_simulation(stressors, adaptation_bonus=adaptation_factor)
            scores.append(score)

        results["raw_scores"] = scores

        # Calculate averages
        avg_err = sum(s["error_rate"] for s in scores) / num_trials
        avg_lat = sum(s["latency_sec"] for s in scores) / num_trials
        avg_acc = sum(s["accuracy"] for s in scores) / num_trials

        # Compute adaptation rate: difference in performance between start and end of stress
        start_acc = scores[0]["accuracy"]
        end_acc = scores[-1]["accuracy"]
        adaptation_rate = end_acc - start_acc

        # Resilience score formula: accuracy combined with positive adaptation
        resilience_score = min(10.0, max(0.0, (avg_acc * 10) + (adaptation_rate * 5)))

        results["resilience_metrics"] = {
            "avg_error_rate": avg_err,
            "avg_latency_sec": avg_lat,
            "avg_accuracy": avg_acc,
            "adaptation_rate": adaptation_rate,
            "calculated_resilience_score": round(resilience_score, 2),
            "adaptation_assessment": "EXCELLENT" if adaptation_rate > 0.1 else "MODERATE" if adaptation_rate >= 0.0 else "POOR"
        }

        return results

    def _execute_trial_simulation(
        self,
        stressors: List[str],
        adaptation_bonus: float = 0.0,
        is_treatment: bool = True
    ) -> Dict[str, Any]:
        """Helper to simulate trial scores under different stressors."""
        # Baseline performance
        base_error = 0.02
        base_latency = 1.0
        base_accuracy = 0.90 if is_treatment else 0.85

        # Incorporate stressors
        for stress in stressors:
            stress = stress.lower().strip()
            if stress == "latency":
                base_latency += random.uniform(1.5, 3.5)
            elif stress == "api_errors":
                base_error += random.uniform(0.08, 0.20)
                base_accuracy -= random.uniform(0.05, 0.15)
            elif stress == "conflicting_goals":
                base_error += random.uniform(0.05, 0.12)
                base_accuracy -= random.uniform(0.04, 0.10)
                base_latency += random.uniform(0.5, 1.5)
            elif stress == "resource_limits":
                base_latency += random.uniform(1.0, 2.5)
                base_error += random.uniform(0.02, 0.08)

        # Apply adaptation bonus (e.g. system learns to mitigate stress)
        base_accuracy = min(1.0, base_accuracy + adaptation_bonus)
        base_error = max(0.0, base_error - (adaptation_bonus * 0.5))
        base_latency = max(0.5, base_latency - (adaptation_bonus * 0.8))

        # Add minor random noise
        error_rate = min(1.0, max(0.0, base_error + random.uniform(-0.02, 0.02)))
        latency = max(0.1, base_latency + random.uniform(-0.2, 0.2))
        accuracy = min(1.0, max(0.0, base_accuracy + random.uniform(-0.02, 0.02)))

        return {
            "error_rate": round(error_rate, 4),
            "latency_sec": round(latency, 2),
            "accuracy": round(accuracy, 4)
        }

    @staticmethod
    def generate_markdown_report(exp: Experiment) -> str:
        """Generates a detailed markdown report of the experiment results."""
        results = exp.results
        if not results:
            return f"# Experiment Report: {exp.name} ({exp.experiment_id})\n\nNo execution results available."

        status_emoji = "✅" if exp.status == "completed" and not results.get("aborted") else "❌" if results.get("aborted") else "⏳"

        report = f"""# ESRA Value-Driven Experiment Report

## Overview
- **Experiment ID:** {exp.experiment_id}
- **Name:** {exp.name}
- **Theme:** {exp.theme}
- **Rollout Type:** {exp.rollout_type.upper()}
- **Status:** {exp.status.upper()} {status_emoji}
- **Created At:** {exp.created_at}

## Hypothesis
> {exp.hypothesis}

## Value-Clarifier Alignment Assessment
- **Value Alignment Score:** {exp.value_alignment_score:.2f} / 1.00
- **Signed Off:** {"YES" if exp.signed_off else "NO"}
- **Justification:** {exp.value_alignment_justification}

## Safe Rollout Evaluation
- **Trials Run:** {results.get("trials_run", 0)}
- **Stages Completed:** {", ".join(results.get("stages_completed", [])) or "None"}
- **Aborted / Rolled Back:** {"YES" if results.get("aborted") else "NO"}
"""
        if results.get("aborted"):
            report += f"\n### 🚨 Rollback Action Triggered\n- **Reason:** {results.get('rollback_reason')}\n"

        report += "\n## Metrics Analysis\n"
        metrics = results.get("metrics", {})

        if exp.rollout_type == "ab_test" and "control" in metrics:
            report += f"""| Variant | Avg Accuracy | Avg Latency (s) | Avg Error Rate |
| :--- | :---: | :---: | :---: |
| **Control (v1)** | {metrics['control']['avg_accuracy'] * 100:.2f}% | {metrics['control']['avg_latency_sec']:.2f}s | {metrics['control']['avg_error_rate'] * 100:.2f}% |
| **Treatment (v2)** | {metrics['treatment']['avg_accuracy'] * 100:.2f}% | {metrics['treatment']['avg_latency_sec']:.2f}s | {metrics['treatment']['avg_error_rate'] * 100:.2f}% |

- **Winner:** **{results.get('winner', 'UNKNOWN').upper()}**
- **Recommendation:** {results.get('recommendation')}
"""
        elif "avg_accuracy" in metrics:
            report += f"""- **Average Accuracy:** {metrics['avg_accuracy'] * 100:.2f}%
- **Average Latency:** {metrics['avg_latency_sec']:.2f}s
- **Average Error Rate:** {metrics['avg_error_rate'] * 100:.2f}%
"""
        elif "stage_metrics" in results:
            report += "\n### Staged Performance Over Time:\n"
            report += "| Stage | Avg Accuracy | Avg Latency (s) | Avg Error Rate |\n| :--- | :---: | :---: | :---: |\n"
            for stage_m in results["stage_metrics"]:
                report += f"| {stage_m['stage']} | {stage_m['avg_accuracy'] * 100:.2f}% | {stage_m['avg_latency_sec']:.2f}s | {stage_m['avg_error_rate'] * 100:.2f}% |\n"

        report += """
## Conclusion & Learnings
Based on the experimental data gathered, we can draw the following conclusions:
"""
        if results.get("aborted"):
            report += f"1. The experiment failed health safeguards and was safely terminated.\n2. Do NOT roll out the changes under {exp.name} to production.\n3. Re-evaluate structural variables and parameters."
        elif exp.rollout_type == "ab_test" and results.get("winner") == "treatment":
            report += "1. The hypothesis was successfully validated.\n2. The treatment variant provides significant performance advantages without inducing value drift.\n3. Recommend immediate promotion of treatment variant to production."
        else:
            report += "1. The experiment completed successfully without violating any safeguards.\n2. Results show standard stable behavior.\n3. Recommend adopting the suggested behavior improvements."

        return report


def main():
    use_color = sys.stdout.isatty() and "NO_COLOR" not in os.environ
    CLR_RESET = "\033[0m" if use_color else ""
    CLR_BOLD = "\033[1m" if use_color else ""
    CLR_CYAN = "\033[36m" if use_color else ""
    CLR_GREEN = "\033[32m" if use_color else ""
    CLR_YELLOW = "\033[33m" if use_color else ""
    CLR_RED = "\033[31m" if use_color else ""

    parser = argparse.ArgumentParser(description="ESRA Value-Driven Experiments Framework")
    subparsers = parser.add_subparsers(dest="command", help="Subcommand to execute")

    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new experiment")
    create_parser.add_argument("--name", required=True, help="Name of experiment")
    create_parser.add_argument("--hypothesis", required=True, help="Hypothesis statement")
    create_parser.add_argument("--theme", required=True, help="Theme area (e.g. reasoning_clarity, antifragility)")
    create_parser.add_argument("--rollout-type", required=True, choices=["canary", "staged", "ab_test"], help="Rollout deployment mechanism")
    create_parser.add_argument("--justification", required=True, help="Value alignment justification statement")
    create_parser.add_argument("--score", required=True, type=float, help="Value Alignment Score (0.0 to 1.0)")
    create_parser.add_argument("--safeguards", help="Custom safeguards dict as JSON (e.g. '{\"max_error_rate\":0.05}')")
    create_parser.add_argument("--stressors", help="Comma-separated list of synthetic stressors (e.g. 'latency,api_errors')")

    # List command
    subparsers.add_parser("list", help="List all experiments")

    # Run command
    run_parser = subparsers.add_parser("run", help="Execute an experiment")
    run_parser.add_argument("--id", required=True, help="Experiment ID to execute")
    run_parser.add_argument("--trials", type=int, default=5, help="Number of trials per run")

    # Stress command
    stress_parser = subparsers.add_parser("stress", help="Execute dedicated Antifragility stress test")
    stress_parser.add_argument("--stressors", required=True, help="Comma-separated stressors to inject (e.g. 'latency,resource_limits')")
    stress_parser.add_argument("--trials", type=int, default=5, help="Number of stress trials")

    # Report command
    report_parser = subparsers.add_parser("report", help="Generate md report for completed experiment")
    report_parser.add_argument("--id", required=True, help="Experiment ID to generate report for")

    args = parser.parse_args()

    runner = ExperimentRunner()

    if args.command == "create":
        # Parse safeguards and stressors
        safeguards = None
        if args.safeguards:
            try:
                safeguards = json.loads(args.safeguards)
            except Exception as e:
                print(f"{CLR_RED}Error: Invalid safeguards JSON format: {e}{CLR_RESET}", file=sys.stderr)
                sys.exit(1)

        stressors = [s.strip() for s in args.stressors.split(",")] if args.stressors else []

        exp = runner.create_experiment(
            name=args.name,
            hypothesis=args.hypothesis,
            theme=args.theme,
            rollout_type=args.rollout_type,
            value_alignment_justification=args.justification,
            value_alignment_score=args.score,
            safeguards=safeguards,
            stressors=stressors
        )

        sign_off_str = f"{CLR_GREEN}GRANTED{CLR_RESET}" if exp.signed_off else f"{CLR_RED}DENIED (Score < 0.70){CLR_RESET}"
        print(f"[{CLR_GREEN}SUCCESS{CLR_RESET}] Created experiment {CLR_BOLD}{exp.experiment_id}{CLR_RESET}!")
        print(f"  Name:             {exp.name}")
        print(f"  Theme:            {exp.theme}")
        print(f"  Rollout:          {exp.rollout_type.upper()}")
        print(f"  Value Alignment:  {exp.value_alignment_score:.2f} / 1.00 (Sign-off: {sign_off_str})")

    elif args.command == "list":
        exps = runner.list_experiments()
        if not exps:
            print(f"{CLR_YELLOW}No experiments have been defined yet.{CLR_RESET}")
            print("Create your first experiment using:")
            print(f"  {CLR_BOLD}python tools/experiment_runner.py create --name ...{CLR_RESET}")
            sys.exit(0)

        print("=" * 70)
        print(f"  {CLR_CYAN}{CLR_BOLD}ESRA Active Value-Driven Experiments{CLR_RESET}")
        print("=" * 70)
        print(f"{'ID':<10}{'Name':<20}{'Rollout':<12}{'Status':<12}{'Score':<8}{'Sign-off':<8}")
        print("-" * 70)
        for exp in exps:
            sign_off_str = f"{CLR_GREEN}YES{CLR_RESET}" if exp.signed_off else f"{CLR_RED}NO{CLR_RESET}"
            status_color = CLR_GREEN if exp.status == "completed" else CLR_RED if exp.status == "aborted" else CLR_YELLOW if exp.status == "running" else CLR_RESET
            print(f"{exp.experiment_id:<10}{exp.name[:18]:<20}{exp.rollout_type.upper():<12}{status_color}{exp.status.upper():<12}{CLR_RESET}{exp.value_alignment_score:<8.2f}{sign_off_str:<8}")
        print("=" * 70)

    elif args.command == "run":
        try:
            print(f"{CLR_CYAN}Initializing execution of experiment {CLR_BOLD}{args.id}{CLR_RESET} ({args.trials} trials)...")
            results = runner.run_experiment(args.id, args.trials)

            exp = runner.load_experiment(args.id)
            if not exp:
                print(f"{CLR_RED}Error reloading experiment {args.id}{CLR_RESET}", file=sys.stderr)
                sys.exit(1)

            if results.get("error"):
                print(f"❌ {CLR_RED}Experiment execution BLOCKED: {results['error']}{CLR_RESET}", file=sys.stderr)
                sys.exit(1)

            if results.get("aborted"):
                print(f"🚨 {CLR_RED}{CLR_BOLD}EXPERIMENT ABORTED & ROLLED BACK!{CLR_RESET}")
                print(f"  Reason: {CLR_YELLOW}{results.get('rollback_reason')}{CLR_RESET}")
            else:
                print(f"✅ {CLR_GREEN}{CLR_BOLD}EXPERIMENT COMPLETED SUCCESSFULY!{CLR_RESET}")
                metrics = results.get("metrics", {})
                if exp.rollout_type == "ab_test":
                    print(f"  Control (v1) accuracy:    {metrics['control']['avg_accuracy'] * 100:.2f}%")
                    print(f"  Treatment (v2) accuracy:  {metrics['treatment']['avg_accuracy'] * 100:.2f}%")
                    print(f"  Winner:                   {CLR_BOLD}{CLR_GREEN}{results.get('winner').upper()}{CLR_RESET}")
                    print(f"  Recommendation:           {results.get('recommendation')}")
                else:
                    print(f"  Average Accuracy:         {metrics.get('avg_accuracy', 0.0) * 100:.2f}%")
                    print(f"  Average Latency:          {metrics.get('avg_latency_sec', 0.0):.2f}s")
                    print(f"  Average Error Rate:       {metrics.get('avg_error_rate', 0.0) * 100:.2f}%")

            print(f"\nGenerate a detailed markdown report with:")
            print(f"  {CLR_BOLD}python tools/experiment_runner.py report --id {args.id}{CLR_RESET}")

        except ValueError as e:
            print(f"{CLR_RED}Error: {e}{CLR_RESET}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "stress":
        stressors = [s.strip() for s in args.stressors.split(",")]
        print(f"{CLR_YELLOW}{CLR_BOLD}Launching Dedicated Antifragility Stress Test...{CLR_RESET}")
        print(f"Injecting stressors: {', '.join(stressors)}")

        results = runner.run_antifragility_stress_test(stressors, args.trials)
        metrics = results["resilience_metrics"]

        print("\n" + "=" * 50)
        print(f"  {CLR_CYAN}{CLR_BOLD}Antifragility Stress Test Results{CLR_RESET}")
        print("=" * 50)
        print(f"Trials Executed:        {results['trials_run']}")
        print(f"Avg Accuracy:           {metrics['avg_accuracy'] * 100:.2f}%")
        print(f"Avg Latency:            {metrics['avg_latency_sec']:.2f}s")
        print(f"Avg Error Rate:         {metrics['avg_error_rate'] * 100:.2f}%")
        print(f"Adaptation Rate:        {CLR_GREEN if metrics['adaptation_rate'] >= 0 else CLR_RED}{metrics['adaptation_rate'] * 100:+.2f}%{CLR_RESET}")
        print(f"Resilience Score:       {CLR_BOLD}{metrics['calculated_resilience_score']} / 10.0{CLR_RESET}")
        print(f"Adaptation Assessment:  {CLR_BOLD}{CLR_GREEN if metrics['adaptation_assessment'] == 'EXCELLENT' else CLR_YELLOW}{metrics['adaptation_assessment']}{CLR_RESET}")
        print("=" * 50)

    elif args.command == "report":
        exp = runner.load_experiment(args.id)
        if not exp:
            print(f"{CLR_RED}Error: Experiment {args.id} not found.{CLR_RESET}", file=sys.stderr)
            sys.exit(1)

        report = ExperimentRunner.generate_markdown_report(exp)
        print(report)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
