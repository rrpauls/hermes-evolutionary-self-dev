import os
import shutil
import pytest
import tempfile
from pathlib import Path
from tools.skill_validator import SkillValidator, stage_and_promote

def test_valid_and_invalid_frontmatter():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_dir = Path(tmpdir)

        # 1. Create a valid skill
        valid_skill = tmp_dir / "valid_skill"
        valid_skill.mkdir()
        skill_file = valid_skill / "SKILL.md"
        skill_file.write_text("""---
name: valid-skill
description: A perfectly valid skill
dependencies: [another-skill]
---
# Valid Skill Guidelines
""", encoding="utf-8")

        # 2. Create an invalid skill (missing name)
        invalid_skill = tmp_dir / "invalid_skill"
        invalid_skill.mkdir()
        skill_file_invalid = invalid_skill / "SKILL.md"
        skill_file_invalid.write_text("""---
description: Missing the name field
---
# Invalid Skill
""", encoding="utf-8")

        # Run validation
        validator = SkillValidator(tmp_dir)

        # Check valid skill
        success, errors, fm = validator.validate_skill_file(valid_skill)
        assert success is True
        assert fm["name"] == "valid-skill"
        assert fm["dependencies"] == ["another-skill"]

        # Check invalid skill
        success, errors, fm = validator.validate_skill_file(invalid_skill)
        assert success is False
        assert any("Missing required field 'name'" in err for err in errors)

def test_branding_check():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_dir = Path(tmpdir)

        # Create skill with forbidden branding
        skill_dir = tmp_dir / "old_branding_skill"
        skill_dir.mkdir()
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text("""---
name: old-brand
description: Try to mention forbidden ESDA term
---
# Old brand
This is using the old Evolutionary Self-Development Architecture branding here.
""", encoding="utf-8")

        validator = SkillValidator(tmp_dir)
        success, errors, fm = validator.validate_skill_file(skill_dir)
        assert success is False
        assert any("Found forbidden branding term" in err for err in errors)

def test_dependency_dag_and_cycle_detection():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_dir = Path(tmpdir)

        # Create multiple skills
        # Skill A depends on B
        skill_a = tmp_dir / "skill_a"
        skill_a.mkdir()
        (skill_a / "SKILL.md").write_text("""---
name: Skill A
description: Skill A description
dependencies: [Skill B]
---
""", encoding="utf-8")

        # Skill B depends on C
        skill_b = tmp_dir / "skill_b"
        skill_b.mkdir()
        (skill_b / "SKILL.md").write_text("""---
name: Skill B
description: Skill B description
dependencies: [Skill C]
---
""", encoding="utf-8")

        # Skill C depends on nothing
        skill_c = tmp_dir / "skill_c"
        skill_c.mkdir()
        (skill_c / "SKILL.md").write_text("""---
name: Skill C
description: Skill C description
dependencies: []
---
""", encoding="utf-8")

        validator = SkillValidator(tmp_dir)
        success, errors, order = validator.run_all_validation()

        assert success is True, f"Validation failed with: {errors}"
        # Correct loading order: C has 0 dependencies, B depends on C, A depends on B.
        # So topological sort order: Skill C -> Skill B -> Skill A
        assert order == ["Skill C", "Skill B", "Skill A"]

def test_circular_dependency_detection():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_dir = Path(tmpdir)

        # Skill A depends on B
        skill_a = tmp_dir / "skill_a"
        skill_a.mkdir()
        (skill_a / "SKILL.md").write_text("""---
name: Skill A
description: Skill A description
dependencies: [Skill B]
---
""", encoding="utf-8")

        # Skill B depends on A (Cycle!)
        skill_b = tmp_dir / "skill_b"
        skill_b.mkdir()
        (skill_b / "SKILL.md").write_text("""---
name: Skill B
description: Skill B description
dependencies: [Skill A]
---
""", encoding="utf-8")

        validator = SkillValidator(tmp_dir)
        success, errors, order = validator.run_all_validation()

        assert success is False
        assert "dependencies" in errors
        assert any("Circular dependency detected" in err for err in errors["dependencies"])

def test_staging_and_rollback_flow():
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        src = base / "src"
        staging = base / "staging"
        prod = base / "prod"

        src.mkdir()
        prod.mkdir()

        # Put an existing skill in prod
        existing_skill = prod / "existing"
        existing_skill.mkdir()
        (existing_skill / "SKILL.md").write_text("---name: existing\ndescription: existing---", encoding="utf-8")

        # Put a valid skill in src
        valid_skill = src / "valid"
        valid_skill.mkdir()
        (valid_skill / "SKILL.md").write_text("""---
name: valid
description: valid
dependencies: []
---
""", encoding="utf-8")

        # Run stage and promote (should succeed)
        success = stage_and_promote(src, staging, prod)
        assert success is True
        assert (prod / "valid").exists()
        assert not (prod / "existing").exists() # prod was replaced by promoted src

        # Put an invalid skill in src
        invalid_skill = src / "invalid"
        invalid_skill.mkdir()
        (invalid_skill / "SKILL.md").write_text("""---
name: invalid
# missing description!
---
""", encoding="utf-8")

        # Run stage and promote (should fail and trigger rollback of prod directory to previous successful state)
        success_fail = stage_and_promote(src, staging, prod)
        assert success_fail is False
        assert (prod / "valid").exists() # prod was restored/untouched!
        assert not (prod / "invalid").exists() # invalid skill did not get promoted
