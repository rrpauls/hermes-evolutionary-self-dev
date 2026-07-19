#!/usr/bin/env python3
"""
evolution-hook.py

Smart trigger for the ESRA (Evolutionary Self-Recursive Architecture) process inside Hermes.

Purpose:
- Automatically detect when Hermes has completed a complex task
  or created/improved a skill.
- Decide whether to trigger `hermes-evolution-orchestrator`.
- Provide a clean foundation for future deeper integration
  (native Hermes tool, sub-agent, or post-processing hook).

This script is designed to be called after significant work.
It can also serve as a reference for native Hermes event hooks.

Usage:
- Manual: python tools/evolution-hook.py
- From AGENTS.md / post-task instructions
- Future: as a native Hermes tool or background watcher

Author: ESRA / hermes-evolutionary-self-dev
"""

from __future__ import annotations
import os
import json
from pathlib import Path
from typing import Any, Dict, Optional, List
from datetime import datetime
from collections import Counter


class EvolutionHook:
    """
    Decides when and how to trigger the ESRA orchestrator
    after Hermes activity.
    """

    def __init__(self, hermes_home: Optional[Path] = None):
        self.hermes_home = hermes_home or Path.home() / ".hermes"
        self.skills_dir = self.hermes_home / "skills"
        self.memory_dir = self.hermes_home / "memory"
        self.history_file = self.hermes_home / "evolution_history.json"
        self._ensure_history_file()

    def _ensure_history_file(self):
        """Create history file if it does not exist."""
        if not self.history_file.exists():
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            self.history_file.write_text("[]", encoding="utf-8")

    def load_history(self, limit: int = 10) -> list:
        """Load recent evolution events."""
        try:
            data = json.loads(self.history_file.read_text(encoding="utf-8"))
            return data[-limit:] if isinstance(data, list) else []
        except Exception:
            return []

    def record_evolution_event(self, event: Dict[str, Any]):
        """Save an evolution event to history (keeps last 50)."""
        try:
            history = json.loads(self.history_file.read_text(encoding="utf-8"))
            if not isinstance(history, list):
                history = []
            history.append(event)
            if len(history) > 50:
                history = history[-50:]
            self.history_file.write_text(
                json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8"
            )
        except Exception as e:
            print(f"Warning: Could not save evolution history: {e}")

    def analyze_recent_patterns(self, limit: int = 10) -> Dict[str, Any]:
        """Analyze recent history for patterns (repeated focus areas, frequency)."""
        history = self.load_history(limit=limit)
        if not history:
            return {"status": "no_history"}

        triggered_events = [e for e in history if e.get("triggered", False)]

        recent_keywords: List[str] = []
        for event in triggered_events[-5:]:
            ctx = event.get("task_context", {})
            recent_keywords.extend(ctx.get("keywords", []))

        keyword_counts = Counter(recent_keywords)
        most_common = keyword_counts.most_common(3)

        same_area_repeated = bool(most_common and most_common[0][1] >= 3)

        return {
            "status": "ok",
            "total_recent_events": len(history),
            "triggered_count": len(triggered_events),
            "most_common_keywords": most_common,
            "same_area_repeated": same_area_repeated,
        }

    def should_trigger_orchestrator(self, task_context: Dict[str, Any]) -> bool:
        """
        Decide whether to trigger hermes-evolution-orchestrator.

        Heuristics:
        - Explicit request
        - New skill created
        - High complexity
        - Evolution-related keywords
        - Low confidence or signs of struggle
        - Multi-step work
        - Rate limiting via recent history
        """
        complexity = task_context.get("complexity", 0)
        new_skill_created = task_context.get("new_skill_created", False)
        explicit_request = task_context.get("explicit_evolution_request", False)
        keywords = [k.lower() for k in task_context.get("keywords", [])]
        confidence = task_context.get("confidence", 1.0)
        multi_step = task_context.get("multi_step", False)
        struggled = task_context.get("struggled", False)

        evolution_keywords = {
            "orchestrate", "evolution", "self-improvement", "esra",
            "self-development", "audit", "reflect", "improve cycle",
            "meta", "antifragile", "loop-auditor"
        }

        # Rate limiting
        recent_history = self.load_history(limit=5)
        recent_triggers = [e for e in recent_history if e.get("triggered", False)]
        triggered_recently = len(recent_triggers) >= 3

        if explicit_request:
            return True
        if new_skill_created:
            return True
        if complexity >= 7:
            return True
        if any(kw in evolution_keywords for kw in keywords):
            return True
        if confidence < 0.6:
            return True
        if multi_step or struggled:
            return True
        if triggered_recently:
            return False

        return False

    def build_orchestrator_prompt(self, task_context: Dict[str, Any]) -> str:
        """Generate a clean prompt for hermes-evolution-orchestrator."""
        task_summary = task_context.get("summary", "Unknown task")
        complexity = task_context.get("complexity", "unknown")

        prompt = f"""After completing the following task:

Task: {task_summary}
Complexity: {complexity}

Run hermes-evolution-orchestrator (or say "orchestrate evolution" / "run full ESRA cycle").

Analyze the result, update mental models, and engage other meta-skills as needed
(self-improver, value-clarifier, experimenter, loop-auditor, antifragility-builder, etc.).

Save important insights to persistent memory.
"""
        return prompt.strip()

    def trigger_orchestrator(self, task_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point.
        Returns a structured decision + recommended prompt.
        In a full native integration this would call Hermes tools / sub-agents.
        """
        decision = self.should_trigger_orchestrator(task_context)

        result = {
            "timestamp": datetime.now().isoformat(),
            "trigger_decision": decision,
            "task_context": task_context,
            "triggered": decision,
        }

        if decision:
            result["orchestrator_prompt"] = self.build_orchestrator_prompt(task_context)
            result["recommended_action"] = (
                "Run hermes-evolution-orchestrator with the provided prompt"
            )
            self.record_evolution_event(result)
        else:
            result["recommended_action"] = "Orchestration not required"
            self.record_evolution_event(result)

        return result

    # ------------------------------------------------------------------
    # Future extension points
    # ------------------------------------------------------------------

    def watch_skills_directory(self):
        """Placeholder for a file watcher on ~/.hermes/skills/."""
        print("Skills directory watching is not yet implemented.")
        print("Possible implementations: watchdog, inotify, or polling.")

    def integrate_as_hermes_tool(self):
        """Placeholder for native Hermes tool / sub-agent registration."""
        print("Native Hermes tool/sub-agent integration is planned but not implemented yet.")


# ----------------------------------------------------------------------
# Example usage / testing
# ----------------------------------------------------------------------

if __name__ == "__main__":
    hook = EvolutionHook()

    # Example 1: Complex task that created a new skill
    example_task_1 = {
        "summary": "Implemented a complex multi-step integration between Hermes and an external API",
        "complexity": 8,
        "new_skill_created": True,
        "explicit_evolution_request": False,
        "keywords": ["integration", "api", "multi-step"],
        "multi_step": True,
        "confidence": 0.75,
    }

    print("=== Example 1: High complexity + new skill ===")
    result_1 = hook.trigger_orchestrator(example_task_1)
    print(json.dumps(result_1, indent=2, ensure_ascii=False))

    # Example 2: Low confidence / struggle
    example_task_2 = {
        "summary": "Attempted to solve a non-standard problem with uncertain outcome",
        "complexity": 6,
        "new_skill_created": False,
        "struggled": True,
        "confidence": 0.45,
        "keywords": ["uncertain", "difficult"],
    }

    print("\n=== Example 2: Low confidence ===")
    result_2 = hook.trigger_orchestrator(example_task_2)
    print(json.dumps(result_2, indent=2, ensure_ascii=False))

    # Pattern analysis demo
    print("\n=== Recent pattern analysis ===")
    patterns = hook.analyze_recent_patterns(limit=10)
    print(json.dumps(patterns, indent=2, ensure_ascii=False))
