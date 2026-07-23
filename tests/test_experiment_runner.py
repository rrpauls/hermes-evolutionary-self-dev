import os
import json
import pytest
import tempfile
from pathlib import Path
from tools.experiment_runner import Experiment, ExperimentRunner

def test_experiment_model():
    # Test Experiment model initialization and dict conversion
    exp = Experiment(
        experiment_id="EXP-123",
        name="Test Experiment",
        hypothesis="Testing is good.",
        theme="testing",
        rollout_type="canary",
        value_alignment_justification="Aligned with quality.",
        value_alignment_score=0.90
    )
    assert exp.experiment_id == "EXP-123"
    assert exp.signed_off is True
    assert exp.status == "planned"

    d = exp.to_dict()
    assert d["experiment_id"] == "EXP-123"
    assert d["signed_off"] is True

    loaded_exp = Experiment.from_dict(d)
    assert loaded_exp.name == "Test Experiment"
    assert loaded_exp.value_alignment_score == 0.90
    assert loaded_exp.signed_off is True


def test_experiment_low_alignment_score():
    exp = Experiment(
        experiment_id="EXP-124",
        name="Low Aligned Experiment",
        hypothesis="Testing is bad.",
        theme="testing",
        rollout_type="canary",
        value_alignment_justification="Misaligned with quality.",
        value_alignment_score=0.50
    )
    assert exp.signed_off is False


def test_experiment_runner_lifecycle():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_home = Path(tmpdir)
        runner = ExperimentRunner(base_dir=tmp_home)

        # Check directories created securely
        assert runner.experiments_dir.exists()
        assert (os.stat(runner.experiments_dir).st_mode & 0o777) == 0o700

        # Create experiment
        exp = runner.create_experiment(
            name="Clarity Boost",
            hypothesis="Adding step-by-step reasoning improves clarity.",
            theme="reasoning_clarity",
            rollout_type="canary",
            value_alignment_justification="Aligned.",
            value_alignment_score=0.95
        )
        assert exp.experiment_id == "EXP-001"
        assert exp.signed_off is True

        # Check saved file and its permissions (0o600)
        exp_file = runner.experiments_dir / "EXP-001.json"
        assert exp_file.exists()
        assert (os.stat(exp_file).st_mode & 0o777) == 0o600

        # List experiments
        exps = runner.list_experiments()
        assert len(exps) == 1
        assert exps[0].experiment_id == "EXP-001"

        # Load experiment
        loaded = runner.load_experiment("EXP-001")
        assert loaded is not None
        assert loaded.name == "Clarity Boost"

        # Loading non-existent returns None
        assert runner.load_experiment("EXP-999") is None


def test_experiment_runner_blocked_run():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_home = Path(tmpdir)
        runner = ExperimentRunner(base_dir=tmp_home)

        # Create experiment with low score
        exp = runner.create_experiment(
            name="Unsafe Run",
            hypothesis="Run without checks",
            theme="testing",
            rollout_type="staged",
            value_alignment_justification="Unsafe.",
            value_alignment_score=0.40
        )

        results = runner.run_experiment("EXP-001")
        assert results.get("error") is not None
        assert "FAILED" in results["error"]

        reloaded = runner.load_experiment("EXP-001")
        assert reloaded.status == "aborted"


def test_experiment_runner_canary_success():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_home = Path(tmpdir)
        runner = ExperimentRunner(base_dir=tmp_home)

        # High safeguards so it passes easily
        exp = runner.create_experiment(
            name="Canary Success",
            hypothesis="Simple run",
            theme="testing",
            rollout_type="canary",
            value_alignment_justification="Aligned.",
            value_alignment_score=0.85,
            safeguards={"max_error_rate": 1.0, "max_latency_sec": 10.0}
        )

        results = runner.run_experiment("EXP-001")
        assert results["aborted"] is False
        assert "canary_pass" in results["stages_completed"]
        assert results["trials_run"] == 5
        assert "avg_accuracy" in results["metrics"]

        reloaded = runner.load_experiment("EXP-001")
        assert reloaded.status == "completed"


def test_experiment_runner_canary_failure():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_home = Path(tmpdir)
        runner = ExperimentRunner(base_dir=tmp_home)

        # Safeguards extremely low so it fails and triggers rollback
        exp = runner.create_experiment(
            name="Canary Failure",
            hypothesis="Failing run",
            theme="testing",
            rollout_type="canary",
            value_alignment_justification="Aligned.",
            value_alignment_score=0.85,
            safeguards={"max_error_rate": -0.01, "max_latency_sec": 0.01}, # Impossible to pass
            stressors=["latency"]
        )

        results = runner.run_experiment("EXP-001")
        assert results["aborted"] is True
        assert results["rollback_triggered"] is True
        assert "rollback_reason" in results
        assert results["trials_run"] == 1 # Aborted after first trial

        reloaded = runner.load_experiment("EXP-001")
        assert reloaded.status == "aborted"


def test_experiment_runner_staged_success():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_home = Path(tmpdir)
        runner = ExperimentRunner(base_dir=tmp_home)

        exp = runner.create_experiment(
            name="Staged Success",
            hypothesis="Testing staged",
            theme="testing",
            rollout_type="staged",
            value_alignment_justification="Aligned.",
            value_alignment_score=0.85,
            safeguards={"max_error_rate": 1.0, "max_latency_sec": 10.0}
        )

        results = runner.run_experiment("EXP-001", num_trials=5)
        assert results["aborted"] is False
        assert len(results["stages_completed"]) == 3
        assert "Stage 3 (100% exposure)" in results["stages_completed"]


def test_experiment_runner_staged_failure():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_home = Path(tmpdir)
        runner = ExperimentRunner(base_dir=tmp_home)

        exp = runner.create_experiment(
            name="Staged Failure",
            hypothesis="Testing staged fail",
            theme="testing",
            rollout_type="staged",
            value_alignment_justification="Aligned.",
            value_alignment_score=0.85,
            safeguards={"max_error_rate": -0.1, "max_latency_sec": -0.1}
        )

        results = runner.run_experiment("EXP-001", num_trials=5)
        assert results["aborted"] is True
        assert results["rollback_triggered"] is True


def test_experiment_runner_staged_partial_failure():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_home = Path(tmpdir)
        runner = ExperimentRunner(base_dir=tmp_home)

        exp = runner.create_experiment(
            name="Staged Partial Failure",
            hypothesis="Testing staged fail",
            theme="testing",
            rollout_type="staged",
            value_alignment_justification="Aligned.",
            value_alignment_score=0.85,
            safeguards={"max_error_rate": -0.1, "max_latency_sec": -0.1}
        )

        results = runner.run_experiment("EXP-001", num_trials=5)
        assert results["aborted"] is True
        assert results["rollback_triggered"] is True


def test_experiment_runner_ab_test():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_home = Path(tmpdir)
        runner = ExperimentRunner(base_dir=tmp_home)

        exp = runner.create_experiment(
            name="A/B Test",
            hypothesis="Compare control and treatment",
            theme="testing",
            rollout_type="ab_test",
            value_alignment_justification="Aligned.",
            value_alignment_score=0.85,
            safeguards={"max_error_rate": 1.0, "max_latency_sec": 10.0}
        )

        results = runner.run_experiment("EXP-001", num_trials=3)
        assert results["trials_run"] == 6 # 3 control, 3 treatment
        assert "winner" in results
        assert "recommendation" in results


def test_experiment_runner_stress_test():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_home = Path(tmpdir)
        runner = ExperimentRunner(base_dir=tmp_home)

        results = runner.run_antifragility_stress_test(stressors=["latency", "api_errors"], num_trials=3)
        assert results["trials_run"] == 3
        assert len(results["raw_scores"]) == 3
        metrics = results["resilience_metrics"]
        assert "avg_error_rate" in metrics
        assert "calculated_resilience_score" in metrics
        assert "adaptation_assessment" in metrics


def test_generate_markdown_report():
    exp = Experiment(
        experiment_id="EXP-001",
        name="Clarity Boost",
        hypothesis="Reasoning helps.",
        theme="reasoning_clarity",
        rollout_type="ab_test",
        value_alignment_justification="Aligned.",
        value_alignment_score=0.90,
        status="completed",
        results={
            "trials_run": 6,
            "stages_completed": ["ab_test_complete"],
            "aborted": False,
            "metrics": {
                "control": {"avg_error_rate": 0.02, "avg_latency_sec": 1.0, "avg_accuracy": 0.85},
                "treatment": {"avg_error_rate": 0.01, "avg_latency_sec": 0.8, "avg_accuracy": 0.95}
            },
            "winner": "treatment",
            "recommendation": "Promote treatment."
        }
    )

    report = ExperimentRunner.generate_markdown_report(exp)
    assert "# ESRA Value-Driven Experiment Report" in report
    assert "EXP-001" in report
    assert "Control (v1)" in report
    assert "Treatment (v2)" in report
    assert "winner" in report.lower()
    assert "treatment" in report.lower()


def test_generate_markdown_report_no_results():
    exp = Experiment(
        experiment_id="EXP-001",
        name="Clarity Boost",
        hypothesis="Reasoning helps.",
        theme="reasoning_clarity",
        rollout_type="ab_test",
        value_alignment_justification="Aligned.",
        value_alignment_score=0.90
    )
    report = ExperimentRunner.generate_markdown_report(exp)
    assert "No execution results available." in report


def test_cli_execution_create_and_list(monkeypatch, capsys):
    import sys
    from tools.experiment_runner import main

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_home = Path(tmpdir)
        # Mock Path.home() so ExperimentRunner uses the temp directory instead
        monkeypatch.setattr(Path, "home", lambda: tmp_home)

        # Test CLI create
        create_args = [
            "experiment_runner.py",
            "create",
            "--name", "Test CLI",
            "--hypothesis", "Hypo",
            "--theme", "reasoning",
            "--rollout-type", "staged",
            "--justification", "Justify",
            "--score", "0.85"
        ]
        monkeypatch.setattr(sys, "argv", create_args)

        main()
        captured = capsys.readouterr()
        assert "SUCCESS" in captured.out
        assert "EXP-001" in captured.out

        # Test CLI list
        list_args = ["experiment_runner.py", "list"]
        monkeypatch.setattr(sys, "argv", list_args)
        main()
        captured = capsys.readouterr()
        assert "ESRA Active Value-Driven Experiments" in captured.out
        assert "EXP-001" in captured.out


def test_cli_execution_run_and_report(monkeypatch, capsys):
    import sys
    from tools.experiment_runner import main

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_home = Path(tmpdir)
        monkeypatch.setattr(Path, "home", lambda: tmp_home)

        # Setup experiment
        create_args = [
            "experiment_runner.py", "create",
            "--name", "Test CLI Run",
            "--hypothesis", "Hypo",
            "--theme", "reasoning",
            "--rollout-type", "canary",
            "--justification", "Justify",
            "--score", "0.85"
        ]
        monkeypatch.setattr(sys, "argv", create_args)
        main()
        capsys.readouterr() # clear buffers

        # Test CLI run
        run_args = ["experiment_runner.py", "run", "--id", "EXP-001", "--trials", "3"]
        monkeypatch.setattr(sys, "argv", run_args)
        main()
        captured = capsys.readouterr()
        assert "COMPLETED SUCCESSFULY" in captured.out

        # Test CLI report
        report_args = ["experiment_runner.py", "report", "--id", "EXP-001"]
        monkeypatch.setattr(sys, "argv", report_args)
        main()
        captured = capsys.readouterr()
        assert "ESRA Value-Driven Experiment Report" in captured.out


def test_cli_execution_stress(monkeypatch, capsys):
    import sys
    from tools.experiment_runner import main

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_home = Path(tmpdir)
        monkeypatch.setattr(Path, "home", lambda: tmp_home)

        stress_args = ["experiment_runner.py", "stress", "--stressors", "latency,resource_limits", "--trials", "2"]
        monkeypatch.setattr(sys, "argv", stress_args)
        main()
        captured = capsys.readouterr()
        assert "Antifragility Stress Test Results" in captured.out
        assert "Resilience Score" in captured.out
