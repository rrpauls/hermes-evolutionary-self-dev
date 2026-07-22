import os
import json
import pytest
import shutil
import tempfile
import time
from pathlib import Path
from tools.esra_logger import ESRALogger

def test_logger_creation_and_logging():
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = ESRALogger(log_dir=tmpdir)

        # Mock inputs, decisions, outputs, resources
        inputs = {"task_complexity": 8, "prior_success_rate": 0.9, "skills_available": ["self-observer"]}
        decisions = {"skills_activated": ["self-improver"], "meta_loop_stage": "ACT"}
        outputs = {"new_skills_created": ["new-skill"], "improvements_applied": [], "success": True}
        resources = {"duration_seconds": 1.5, "resource_consumption": {"tokens": 1000}}

        filepath = logger.log_cycle(inputs, decisions, outputs, resources)

        assert os.path.exists(filepath)

        # Verify file permissions are strictly 0o600 (owner read/write only)
        mode = os.stat(filepath).st_mode & 0o777
        assert mode == 0o600, f"Expected permissions 0o600, got {oct(mode)}"

        # Verify contents
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["input_state"]["task_complexity"] == 8
        assert data["orchestrator_decisions"]["skills_activated"] == ["self-improver"]
        assert data["outputs"]["new_skills_created"] == ["new-skill"]
        assert data["duration_and_resources"]["duration_seconds"] == 1.5

def test_logger_retention_policy():
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = ESRALogger(log_dir=tmpdir)

        # Create a file that is 31 days old
        old_file = Path(tmpdir) / "esra_cycle_old.json"
        old_file.write_text("{}", encoding="utf-8")
        # Change access and modification times to 31 days ago
        old_time = time.time() - (31 * 24 * 60 * 60)
        os.utime(old_file, (old_time, old_time))

        # Create a file that is 1 day old
        new_file = Path(tmpdir) / "esra_cycle_new.json"
        new_file.write_text("{}", encoding="utf-8")
        new_time = time.time() - (1 * 24 * 60 * 60)
        os.utime(new_file, (new_time, new_time))

        # Run retention cleanup
        logger.clean_old_logs()

        assert not old_file.exists(), "Old log file should have been deleted by retention policy"
        assert new_file.exists(), "New log file should not be deleted"
