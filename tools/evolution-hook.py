#!/usr/bin/env python3
"""
evolution-hook.py

Starter template for deeper automation of Evolutionary Self-Development in Hermes.

Purpose:
- Automatically detect when Hermes has completed a complex task
  or created/improved a skill.
- Decide whether to trigger `hermes-evolution-orchestrator`.
- Provide a foundation for future integration (via sub-agents, tools,
  or post-processing hooks).

This is currently a **skeleton / design document in code form**.
Real integration will depend on Hermes internals (tool system, sub-agents,
event hooks, or Skills Hub).

Usage ideas:
- Run as a background watcher (monitor ~/.hermes/skills/ for new files)
- Integrate as a custom Hermes tool
- Use as a post-task hook in AGENTS.md / workspace instructions
- Extend into a full sub-agent

Author: Evolutionary Self-Development Architecture
"""

from __future__ import annotations
import os
import json
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime


class EvolutionHook:
    """
    Main class responsible for deciding when and how to trigger
    evolutionary self-development after Hermes activity.
    """

    def __init__(self, hermes_home: Optional[Path] = None):
        self.hermes_home = hermes_home or Path.home() / ".hermes"
        self.skills_dir = self.hermes_home / "skills"
        self.memory_dir = self.hermes_home / "memory"  # placeholder
        self.history_file = self.hermes_home / "evolution_history.json"
        self._ensure_history_file()

    def _ensure_history_file(self):
        """Create history file if it doesn't exist."""
        if not self.history_file.exists():
            self.history_file.write_text("[]", encoding="utf-8")

    def load_history(self, limit: int = 10) -> list:
        """Load recent evolution events."""
        try:
            data = json.loads(self.history_file.read_text(encoding="utf-8"))
            return data[-limit:] if isinstance(data, list) else []
        except Exception:
            return []

    def record_evolution_event(self, event: Dict[str, Any]):
        """Save an evolution event to history."""
        try:
            history = json.loads(self.history_file.read_text(encoding="utf-8"))
            if not isinstance(history, list):
                history = []
            history.append(event)
            # Keep only last 50 events
            if len(history) > 50:
                history = history[-50:]
            self.history_file.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception as e:
            print(f"Warning: Could not save evolution history: {e}")

    def analyze_recent_patterns(self, limit: int = 10) -> Dict[str, Any]:
        """
        Analyze recent evolution history for patterns.
        Returns insights like repeated focus areas, frequency, etc.
        """
        history = self.load_history(limit=limit)
        if not history:
            return {"status": "no_history"}

        triggered_events = [e for e in history if e.get("triggered", False)]

        # Simple pattern: check if many recent triggers were about similar keywords
        recent_keywords = []
        for event in triggered_events[-5:]:
            ctx = event.get("task_context", {})
            recent_keywords.extend(ctx.get("keywords", []))

        from collections import Counter
        keyword_counts = Counter(recent_keywords)
        most_common = keyword_counts.most_common(3)

        same_area_repeated = False
        if most_common and most_common[0][1] >= 3:
            same_area_repeated = True

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

        Heuristics (can be extended):
        - High complexity score
        - New skill was created or significantly changed
        - Explicit evolution request from user or model
        - Keywords indicating need for reflection/improvement
        - Low confidence or signs of struggle in the task result
        - Task involved multiple steps or sub-agents
        - Not triggered too recently (rate limiting via history)
        """
        complexity = task_context.get("complexity", 0)
        new_skill_created = task_context.get("new_skill_created", False)
        explicit_request = task_context.get("explicit_evolution_request", False)
        keywords = task_context.get("keywords", [])
        confidence = task_context.get("confidence", 1.0)
        multi_step = task_context.get("multi_step", False)
        struggled = task_context.get("struggled", False)

        evolution_keywords = {
            "orchestrate", "evolution", "self-improvement", "улучши цикл",
            "рефлексия", "аудит", "улучшить", "эволюция"
        }

        # Simple rate limiting using history
        recent_history = self.load_history(limit=5)
        recent_triggers = [e for e in recent_history if e.get("triggered", False)]
        triggered_recently = len(recent_triggers) >= 3

        if explicit_request:
            return True
        if new_skill_created:
            return True
        if complexity >= 7:
            return True
        if any(kw.lower() in evolution_keywords for kw in keywords):
            return True
        if confidence < 0.6:
            return True
        if multi_step or struggled:
            return True
        if triggered_recently:
            return False

        # Simple pattern detection from history
        patterns = self.analyze_recent_patterns(limit=8)
        if patterns.get("same_area_repeated", False):
            # If we've been improving the same area a lot, still allow trigger
            # but the orchestrator can decide on deeper work
            pass

        return False

    def build_orchestrator_prompt(self, task_context: Dict[str, Any]) -> str:
        """
        Generate the prompt/instruction to send to hermes-evolution-orchestrator.
        """
        task_summary = task_context.get("summary", "Неизвестная задача")
        complexity = task_context.get("complexity", "неизвестно")

        prompt = f"""После выполнения задачи:

Задача: {task_summary}
Сложность: {complexity}

Запусти hermes-evolution-orchestrator.
Проанализируй результат, обнови ментальные модели и при необходимости
задействуй другие мета-навыки (ooda-framework, self-improver, loop-auditor и др.).

Сохрани важные insights в persistent memory.
"""
        return prompt.strip()

    def trigger_orchestrator(self, task_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point. In a real integration this would:
        - Call Hermes tool/sub-agent system
        - Or print instructions for the model to follow
        - Or write to a queue / trigger file

        Currently returns a structured decision + prompt.
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
                "Запустить hermes-evolution-orchestrator с предоставленным промптом"
            )
            # Record successful trigger in history
            self.record_evolution_event(result)
        else:
            result["recommended_action"] = "Оркестрация не требуется"
            # Still record the decision (for rate limiting)
            self.record_evolution_event(result)

        return result

    # ------------------------------------------------------------------
    # Future extension points
    # ------------------------------------------------------------------

    def watch_skills_directory(self):
        """
        Placeholder for a file watcher that monitors ~/.hermes/skills/
        for new or modified skills and triggers the hook.
        """
        print("Watching skills directory is not yet implemented.")
        print("This could use watchdog, inotify, or polling.")

    def integrate_as_hermes_tool(self):
        """
        Placeholder for registering this hook as a native Hermes tool
        or sub-agent.
        """
        print("Integration as Hermes tool/sub-agent is planned but not implemented yet.")


# ----------------------------------------------------------------------
# Example usage / testing
# ----------------------------------------------------------------------

if __name__ == "__main__":
    hook = EvolutionHook()

    # Пример 1: Сложная задача с созданием навыка
    example_task_1 = {
        "summary": "Реализовал сложную интеграцию между Hermes и внешним API с несколькими шагами",
        "complexity": 8,
        "new_skill_created": True,
        "explicit_evolution_request": False,
        "keywords": ["integration", "api", "multi-step"],
        "multi_step": True,
        "confidence": 0.75,
    }

    print("=== Пример 1 ===")
    result_1 = hook.trigger_orchestrator(example_task_1)
    print(json.dumps(result_1, indent=2, ensure_ascii=False))

    # Пример 2: Задача с низкой уверенностью
    example_task_2 = {
        "summary": "Попытался решить нестандартную проблему, но результат неуверенный",
        "complexity": 6,
        "new_skill_created": False,
        "struggled": True,
        "confidence": 0.45,
    }

    print("\n=== Пример 2 ===")
    result_2 = hook.trigger_orchestrator(example_task_2)
    print(json.dumps(result_2, indent=2, ensure_ascii=False))

    # Демонстрация анализа паттернов
    print("\n=== Анализ паттернов в истории ===")
    patterns = hook.analyze_recent_patterns(limit=10)
    print(json.dumps(patterns, indent=2, ensure_ascii=False))
