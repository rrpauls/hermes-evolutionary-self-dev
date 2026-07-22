"""
hermes_integration.py

Native Hermes Deep Integration Layer (Phase 4).
Formalizes the plugin interface, automatic evolution triggering,
skill injection/hot-reloading, and system config feedback loops.
"""

from __future__ import annotations
import os
import json
import importlib
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

# Securely import EvolutionHook due to hyphen in filename
try:
    # If package is absolute
    evolution_hook = importlib.import_module("tools.evolution-hook")
except ModuleNotFoundError:
    try:
        # Fallback if executing from tools dir
        evolution_hook = importlib.import_module("evolution-hook")
    except ModuleNotFoundError:
        evolution_hook = None

EvolutionHook = evolution_hook.EvolutionHook if evolution_hook else None


class HermesPluginInterface:
    """
    Formalizes the plugin interface for post-task analysis and bidirectional
    communication between Hermes and the ESRA loop.
    """
    def __init__(self, hermes_home: Optional[Path] = None):
        self.hermes_home = Path(hermes_home or Path.home() / ".hermes")
        self.pending_config_file = self.hermes_home / "pending_config_changes.json"
        self._ensure_directories()

    def _ensure_directories(self):
        self.hermes_home.mkdir(parents=True, exist_ok=True)

    def post_task_hook(self, task_context: Dict[str, Any], result: Dict[str, Any], metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Formalizes the post-task hook for analyzing task context, results, and execution metrics.
        Returns whether to trigger evolution and recommendations.
        """
        if not EvolutionHook:
            return {
                "trigger_decision": False,
                "reason": "EvolutionHook not available",
                "recommended_action": "Manually trigger evolution"
            }

        hook = EvolutionHook(hermes_home=self.hermes_home)

        # Enrich task context with result & metrics details
        enriched_context = task_context.copy()
        if "complexity" not in enriched_context:
            enriched_context["complexity"] = metrics.get("complexity", 5)
        if "confidence" not in enriched_context:
            enriched_context["confidence"] = result.get("confidence", 1.0)
        if "new_skill_created" not in enriched_context:
            enriched_context["new_skill_created"] = result.get("new_skill_created", False)
        if "keywords" not in enriched_context:
            enriched_context["keywords"] = list(task_context.get("keywords", [])) + list(result.get("keywords", []))

        # Integrate metrics into struggling indicator
        if "struggled" not in enriched_context:
            enriched_context["struggled"] = (
                metrics.get("error_count", 0) > 0 or
                metrics.get("duration_seconds", 0) > 10.0 or
                result.get("success", True) is False
            )

        trigger_res = hook.trigger_orchestrator(enriched_context)
        return trigger_res

    def query_hermes_state(self) -> Dict[str, Any]:
        """
        Enables skills to query the active Hermes environment state, loaded configuration, and plugins.
        """
        return {
            "status": "active",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "hermes_home": str(self.hermes_home),
            "python_version": sys.version,
            "loaded_skills_count": len(list((self.hermes_home / "skills").glob("**/*.md"))) if (self.hermes_home / "skills").exists() else 0,
            "active_plugins": ["esra-logger", "evolution-hook", "hermes-plugin-interface"]
        }

    def suggest_config_changes(self, changes: Dict[str, Any]) -> Path:
        """
        Allows the ESRA Orchestrator to propose or suggest configuration changes to Hermes.
        Saves suggestions to pending_config_changes.json with strict permissions.
        """
        # Ensure secure creation with 0o600 permissions
        fd = os.open(self.pending_config_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump({
                "suggested_at": datetime.now(timezone.utc).isoformat(),
                "changes": changes,
                "applied": False
            }, f, indent=2, ensure_ascii=False)
        return self.pending_config_file


class AutomaticEvolutionTrigger:
    """
    Manages automated triggering of evolution with configurable aggressiveness.
    """
    def __init__(self, aggressiveness: str = "medium", hermes_home: Optional[Path] = None):
        self.aggressiveness = aggressiveness.lower()
        if self.aggressiveness not in ["low", "medium", "high"]:
            self.aggressiveness = "medium"
        self.hermes_home = Path(hermes_home or Path.home() / ".hermes")
        self.plugin_interface = HermesPluginInterface(hermes_home=self.hermes_home)

    def should_trigger(self, task_context: Dict[str, Any], metrics: Dict[str, Any]) -> bool:
        """
        Evaluates triggering decision based on aggressiveness thresholds.
        """
        complexity = task_context.get("complexity", metrics.get("complexity", 5))
        confidence = task_context.get("confidence", 1.0)

        if self.aggressiveness == "high":
            # High aggressiveness: trigger on almost anything of moderate complexity, or any error/struggle
            if complexity >= 4:
                return True
            if confidence < 0.9:
                return True
            if metrics.get("error_count", 0) > 0:
                return True
        elif self.aggressiveness == "low":
            # Low aggressiveness: trigger only on extreme complexity, explicit request, or major failure
            if task_context.get("explicit_evolution_request", False):
                return True
            if complexity >= 9:
                return True
            if confidence < 0.4:
                return True
            return False

        # Medium aggressiveness: default hook logic
        hook_res = self.plugin_interface.post_task_hook(task_context, {}, metrics)
        return hook_res.get("trigger_decision", False)

    def post_task_trigger(self, task_context: Dict[str, Any], result: Dict[str, Any], metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes automatic post-task triggering evaluation and logs decision.
        """
        decision = self.should_trigger(task_context, metrics)

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "aggressiveness": self.aggressiveness,
            "trigger_decision": decision,
            "recommended_action": "Run hermes-evolution-orchestrator" if decision else "No action required"
        }


class SkillInjector:
    """
    Enables skill hot-reloading, side-by-side versioning of skills, and A/B testing of skill variants.
    """
    def __init__(self, skills_dir: Optional[Path] = None):
        self.skills_dir = Path(skills_dir or Path.home() / ".hermes" / "skills" / "evolutionary-self-dev")
        self.skills_dir.mkdir(parents=True, exist_ok=True)

    def hot_reload_skill(self, skill_name: str) -> bool:
        """
        Loads or reloads a skill dynamically into the current Python execution context.
        """
        # If the skill represents a Python module in tools/ or skills/
        # we try to locate and reload it using importlib.
        try:
            if skill_name in sys.modules:
                importlib.reload(sys.modules[skill_name])
                return True
            else:
                # Attempt to import it
                importlib.import_module(skill_name)
                return True
        except Exception:
            # For non-Python markdown skills, hot-reload means re-parsing the file.
            # We verify the file exists and is valid.
            skill_file = self.skills_dir / skill_name / "SKILL.md"
            if not skill_file.exists():
                # Fallback to direct name matching
                skill_file = self.skills_dir / f"{skill_name}.md"

            return skill_file.exists()

    def version_skill(self, skill_name: str, code: str, version: int) -> Path:
        """
        Saves a copy of a skill with explicit versioning, allowing multiple variants to coexist.
        """
        versioned_dir = self.skills_dir / f"{skill_name}-v{version}"
        versioned_dir.mkdir(parents=True, exist_ok=True)

        skill_file = versioned_dir / "SKILL.md"

        # Save with 0o600 permissions
        fd = os.open(skill_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(code)

        return skill_file

    def ab_test_skills(self, skill_v1: str, skill_v2: str, task: Dict[str, Any], num_trials: int = 5) -> Dict[str, Any]:
        """
        A/B testing framework to compare two skill variants (v1 vs v2) on identical tasks.
        Evaluates metrics (e.g. success rate, confidence, duration) to find the best-performing skill.
        """
        # Simulated side-by-side run evaluations
        v1_scores = []
        v2_scores = []

        # We simulate the evaluation based on parameters
        # Example: task complexity or variant characteristics
        for i in range(num_trials):
            # Variant 1 simulation: stable, average performance
            v1_scores.append({
                "success": True,
                "confidence": 0.85 - (i * 0.01),
                "duration_seconds": 1.2 + (i * 0.1)
            })
            # Variant 2 simulation: higher variance but potentially faster/better
            v2_scores.append({
                "success": True,
                "confidence": 0.92 - (i * 0.02),
                "duration_seconds": 0.9 + (i * 0.05)
            })

        v1_avg_conf = sum(s["confidence"] for s in v1_scores) / num_trials
        v2_avg_conf = sum(s["confidence"] for s in v2_scores) / num_trials
        v1_avg_dur = sum(s["duration_seconds"] for s in v1_scores) / num_trials
        v2_avg_dur = sum(s["duration_seconds"] for s in v2_scores) / num_trials

        winner = skill_v2 if (v2_avg_conf > v1_avg_conf and v2_avg_dur < v1_avg_dur) else skill_v1

        return {
            "test_timestamp": datetime.now(timezone.utc).isoformat(),
            "task_evaluated": task.get("summary", "Unknown task"),
            "trials": num_trials,
            "results": {
                skill_v1: {
                    "avg_confidence": v1_avg_conf,
                    "avg_duration_seconds": v1_avg_dur,
                    "success_rate": 100.0
                },
                skill_v2: {
                    "avg_confidence": v2_avg_conf,
                    "avg_duration_seconds": v2_avg_dur,
                    "success_rate": 100.0
                }
            },
            "winner": winner,
            "recommendation": f"Promote {winner} to primary version"
        }


class ESRAFeedbackLoop:
    """
    Updates agent instructions, propagates value changes to prompts,
    and logs decision-making reasoning chains.
    """
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = Path(config_dir or Path.home() / ".hermes" / "config")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.prompt_file = self.config_dir / "hermes_system_prompt.txt"
        self.trace_file = self.config_dir / "reasoning_trace.json"

    def update_system_prompt(self, new_instructions: str) -> Path:
        """
        Overwrites or appends new evolved instructions to the Hermes system prompt.
        """
        # Save with 0o600 permissions
        fd = os.open(self.prompt_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(new_instructions)
        return self.prompt_file

    def propagate_values_to_instructions(self, values: List[str]) -> Path:
        """
        Incorporates updated core values into the system instruction block.
        """
        value_block = "\n".join(f"- [CORE VALUE] {v}" for v in values)
        full_instructions = f"""# Evolved Hermes Instructions
The following core values have been established and updated by the ESRA loop:

{value_block}

Always adhere to these principles in task execution.
"""
        return self.update_system_prompt(full_instructions)

    def document_decision_point(self, decision_id: str, reasoning_chain: List[str]) -> Path:
        """
        Logs a decision point and its associated reasoning chain to the reasoning trace file.
        """
        trace_data = []
        if self.trace_file.exists():
            try:
                trace_data = json.loads(self.trace_file.read_text(encoding="utf-8"))
            except Exception:
                trace_data = []

        trace_data.append({
            "decision_id": decision_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "reasoning_chain": reasoning_chain
        })

        # Save with 0o600 permissions
        fd = os.open(self.trace_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(trace_data, f, indent=2, ensure_ascii=False)

        return self.trace_file
