import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path

class ESRALogger:
    """
    Handles structured JSON logging for all ESRA orchestrator invocations.
    Ensures logs are saved to ~/.hermes/evolution-logs/ and maintains a 30-day retention policy.
    """
    def __init__(self, log_dir=None):
        if log_dir is None:
            self.log_dir = Path.home() / ".hermes" / "evolution-logs"
        else:
            self.log_dir = Path(log_dir)

        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.clean_old_logs()

    def log_cycle(self, input_state, decisions, outputs, duration_resources):
        """
        Logs a single ESRA cycle to a JSON file.
        """
        timestamp = datetime.utcnow().isoformat()

        # Log schema matching ROADMAP requirements
        log_entry = {
            "timestamp": timestamp,
            "input_state": {
                "task_complexity": input_state.get("task_complexity"),
                "prior_success_rate": input_state.get("prior_success_rate"),
                "skills_available": input_state.get("skills_available", [])
            },
            "orchestrator_decisions": {
                "skills_activated": decisions.get("skills_activated", []),
                "meta_loop_stage": decisions.get("meta_loop_stage")
            },
            "outputs": {
                "new_skills_created": outputs.get("new_skills_created", []),
                "improvements_applied": outputs.get("improvements_applied", []),
                "value_changes": outputs.get("value_changes", []),
                "success": outputs.get("success", True),
                "anomalies": outputs.get("anomalies", []),
                "crisis_interventions": outputs.get("crisis_interventions", [])
            },
            "duration_and_resources": {
                "duration_seconds": duration_resources.get("duration_seconds"),
                "resource_consumption": duration_resources.get("resource_consumption", {})
            }
        }

        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"esra_cycle_{safe_timestamp}.json"
        filepath = self.log_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(log_entry, f, indent=2, ensure_ascii=False)

        return str(filepath)

    def clean_old_logs(self):
        """
        Implements retention policy (30-day rolling history).
        Deletes log files older than 30 days.
        """
        cutoff = time.time() - (30 * 24 * 60 * 60)
        for filepath in self.log_dir.glob("*.json"):
            if filepath.is_file():
                if filepath.stat().st_mtime < cutoff:
                    try:
                        filepath.unlink()
                    except Exception as e:
                        print(f"Warning: Failed to delete old log {filepath}: {e}")
