import os
import pytest
import tempfile
from pathlib import Path
from tools.human_oversight import HumanOversight

def test_branch_naming_convention():
    assert HumanOversight.format_pr_branch_name("Self Observer", version=1) == "evolve/self-observer-v1"
    assert HumanOversight.format_pr_branch_name("hermes codebase engineer", version=3) == "evolve/hermes-codebase-engineer-v3"

def test_issue_template_generation():
    with tempfile.TemporaryDirectory() as tmpdir:
        oversight = HumanOversight(output_dir=tmpdir)

        # Test crisis template
        crisis_details = {
            "severity": "CRITICAL",
            "reason": "Goal drift in self-improver",
            "task_context": "Refactoring core planning",
            "suggested_action": "Halt execution and seek feedback"
        }
        crisis_path = oversight.generate_crisis_issue_template(crisis_details)
        assert os.path.exists(crisis_path)

        content_crisis = Path(crisis_path).read_text(encoding="utf-8")
        assert "Goal drift in self-improver" in content_crisis
        assert "CRITICAL" in content_crisis

        # Test weekly report template
        metrics = {
            "total_cycles": 14,
            "success_rate": 92.8,
            "new_skills_created": 3,
            "improvements_applied": 7,
            "value_changes_count": 0,
            "anomalies_count": 1
        }
        report_path = oversight.generate_weekly_report_issue(metrics)
        assert os.path.exists(report_path)

        content_report = Path(report_path).read_text(encoding="utf-8")
        assert "92.8" in content_report
        assert "Total Cycles this week: 14" in content_report
