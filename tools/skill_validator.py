#!/usr/bin/env python3
"""
skill_validator.py

Automated checks for ESRA meta-skills:
- Syntax correctness (YAML frontmatter parsing)
- Required fields (name, description)
- Value alignment (no old branding, checks for safety/principles)
- Dependency mapping & genealogy (DAG check, cycle detection, loading order)
- Staging and Rollback mechanism
"""

import os
import sys
import argparse
import re
import shutil
import tempfile
import heapq
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional

# Try to import yaml, fallback to a basic parser if not available
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


class SkillValidator:
    def __init__(self, skills_dir: Path, verbose: bool = False):
        self.skills_dir = Path(skills_dir)
        self.verbose = verbose
        self.forbidden_patterns = [
            re.compile(r"Evolutionary Self-Development Architecture", re.IGNORECASE),
            re.compile(r"ESDA(?![R])", re.IGNORECASE),
            re.compile(r"Self-Development Architecture", re.IGNORECASE)
        ]

    def log(self, message: str):
        if self.verbose:
            print(message)

    def parse_frontmatter(self, file_path: Path) -> Tuple[Optional[Dict], Optional[str], Optional[str]]:
        """Parses frontmatter from a markdown file.
        Returns a tuple of (frontmatter_dict, error_message, raw_content).
        """
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            return None, f"Failed to read file: {e}", None

        # Search for frontmatter between triple-dash markers
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
        if not match:
            return None, "No YAML frontmatter found (missing --- boundary at start of file)", content

        yaml_content = match.group(1)

        if HAS_YAML:
            try:
                data = yaml.safe_load(yaml_content)
                if not isinstance(data, dict):
                    return None, "Frontmatter is not a valid YAML dictionary", content
                return data, None, content
            except Exception as e:
                return None, f"YAML parsing error: {e}", content
        else:
            # Fallback parser for basic key-value pairs
            data = {}
            lines = yaml_content.split("\n")
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if ":" not in line:
                    return None, f"Fallback parser error: Line {line_num} does not contain key-value separator ':'", content
                key, val = line.split(":", 1)
                key = key.strip()
                val = val.strip()
                # strip optional quotes
                if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                    val = val[1:-1]
                # Try simple list parsing for dependencies
                if key == "dependencies" and val.startswith("[") and val.endswith("]"):
                    val = [item.strip().strip("'").strip('"') for item in val[1:-1].split(",") if item.strip()]
                elif key == "dependencies":
                    # Simple single item list or comma-separated if not bracketed
                    val = [item.strip() for item in val.split(",") if item.strip()]
                data[key] = val
            return data, None, content

    def validate_skill_file(self, skill_dir: Path) -> Tuple[bool, List[str], Optional[Dict]]:
        """Validates a single skill directory and its SKILL.md file."""
        errors = []
        skill_file = skill_dir / "SKILL.md"

        if not skill_file.exists():
            errors.append(f"Missing SKILL.md in {skill_dir.name}")
            return False, errors, None

        frontmatter, err, file_content = self.parse_frontmatter(skill_file)
        if err:
            errors.append(f"Frontmatter error in {skill_dir.name}/SKILL.md: {err}")
            return False, errors, None

        # Verify required fields
        for field in ["name", "description"]:
            if field not in frontmatter or not frontmatter[field]:
                errors.append(f"Missing required field '{field}' in frontmatter of {skill_dir.name}/SKILL.md")

        # Verify value alignment (anti-branding checking)
        # ⚡ BOLT OPTIMIZATION: Reuse file_content from parse_frontmatter to prevent duplicate file reads
        try:
            if file_content:
                for pattern in self.forbidden_patterns:
                    if pattern.search(file_content):
                        errors.append(f"Found forbidden branding term in {skill_dir.name}/SKILL.md")
                        break
        except Exception as e:
            errors.append(f"Failed to process content for branding check: {e}")

        # Check for optional required inputs / output schema declarations
        if "required_inputs" in frontmatter and not isinstance(frontmatter["required_inputs"], list):
            errors.append(f"'required_inputs' must be a list in {skill_dir.name}/SKILL.md")
        if "output_schema" in frontmatter and not isinstance(frontmatter["output_schema"], (dict, str)):
            errors.append(f"'output_schema' must be a dict or a description string in {skill_dir.name}/SKILL.md")

        success = len(errors) == 0
        return success, errors, frontmatter

    def run_all_validation(self) -> Tuple[bool, Dict[str, List[str]], List[str]]:
        """Scans the skills directory, validates all skills, and checks dependencies."""
        validation_errors = {}
        all_skills = {}

        if not self.skills_dir.exists():
            return False, {"system": [f"Skills directory does not exist: {self.skills_dir}"]}, []

        # List all subdirectories
        for path in self.skills_dir.iterdir():
            if path.is_dir() and not path.name.startswith("."):
                is_valid, errors, frontmatter = self.validate_skill_file(path)
                if not is_valid:
                    validation_errors[path.name] = errors
                elif frontmatter:
                    all_skills[frontmatter["name"]] = {
                        "dir_name": path.name,
                        "dependencies": frontmatter.get("dependencies", []),
                        "frontmatter": frontmatter
                    }

        # Validate dependencies & trace loading order
        dep_errors = []
        loading_order = []
        if all_skills:
            dep_errors, loading_order = self.validate_dependencies(all_skills)
            if dep_errors:
                validation_errors["dependencies"] = dep_errors

        success = len(validation_errors) == 0
        return success, validation_errors, loading_order

    def validate_dependencies(self, all_skills: Dict[str, Dict]) -> Tuple[List[str], List[str]]:
        """Checks for unresolved dependencies and circular dependencies.
        Returns a list of errors and the topological loading order.
        """
        errors = []

        # Build dependency graph
        # Node -> Set of dependencies
        graph = {}
        for skill_name, info in all_skills.items():
            deps = info["dependencies"]
            if isinstance(deps, str):
                deps = [deps]
            elif not isinstance(deps, list):
                errors.append(f"Skill '{skill_name}' has invalid dependencies format")
                deps = []

            # Check for missing/unresolved dependencies
            valid_deps = []
            for dep in deps:
                if dep not in all_skills:
                    errors.append(f"Skill '{skill_name}' depends on unresolved skill '{dep}'")
                else:
                    valid_deps.append(dep)
            graph[skill_name] = set(valid_deps)

        import heapq

        # ⚡ BOLT OPTIMIZATION:
        # Replaced O(V²) nested loops with O(V + E) approach using adjacency lists
        # Kahn's algorithm for topological sorting of dependencies
        in_degree = {u: 0 for u in graph}
        dependents = {u: [] for u in graph}

        for u in graph:
            for v in graph[u]:
                if v in in_degree:
                    in_degree[u] += 1
                    dependents[v].append(u)

        queue = [u for u in graph if in_degree[u] == 0]
        heapq.heapify(queue)
        loading_order = []

        while queue:
            u = heapq.heappop(queue)
            loading_order.append(u)

            for v in dependents[u]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    heapq.heappush(queue, v)

        if len(loading_order) < len(graph):
            unresolved = set(graph.keys()) - set(loading_order)
            errors.append(f"Circular dependency detected among skills: {', '.join(sorted(unresolved))}")

        return errors, loading_order


def stage_and_promote(skills_src: Path, staging_dir: Path, prod_dir: Path, verbose: bool = False) -> bool:
    """Implements staging, verification, promotion, and rollback."""
    use_color = sys.stdout.isatty() and "NO_COLOR" not in os.environ
    CLR_RESET = "\033[0m" if use_color else ""
    CLR_BOLD = "\033[1m" if use_color else ""
    CLR_CYAN = "\033[36m" if use_color else ""
    CLR_GREEN = "\033[32m" if use_color else ""
    CLR_RED = "\033[31m" if use_color else ""

    print("=" * 60)
    print(f"  {CLR_CYAN}{CLR_BOLD}ESRA Staging and Promotion Engine{CLR_RESET}")
    print("=" * 60)

    skills_src = Path(skills_src)
    staging_dir = Path(staging_dir)
    prod_dir = Path(prod_dir)

    # 1. Clean staging directory and copy source files there
    if staging_dir.exists():
        shutil.rmtree(staging_dir)
    staging_dir.mkdir(parents=True, exist_ok=True)

    print(f"{CLR_BOLD}1. Copying skills from src '{skills_src}' to staging '{staging_dir}'...{CLR_RESET}")
    for item in skills_src.iterdir():
        if item.is_dir() and not item.name.startswith("."):
            shutil.copytree(item, staging_dir / item.name)
        elif item.is_file():
            shutil.copy2(item, staging_dir)

    # 2. Run validations on staging directory
    print(f"{CLR_BOLD}2. Running validation suite on staging directory...{CLR_RESET}")
    validator = SkillValidator(staging_dir, verbose=verbose)
    success, errors, order = validator.run_all_validation()

    if not success:
        print(f"❌ {CLR_RED}Validation FAILED in staging directory. Aborting promotion.{CLR_RESET}", file=sys.stderr)
        for skill_name, errs in errors.items():
            print(f"  [{skill_name}]:", file=sys.stderr)
            for err in errs:
                print(f"    - {err}", file=sys.stderr)
        shutil.rmtree(staging_dir)
        return False

    print(f"✅ {CLR_GREEN}Validation PASSED in staging directory.{CLR_RESET}")
    if order:
        print(f"   Dependency loading order: { ' -> '.join(order) }")

    # 3. Backup current production directory if it exists
    backup_dir = None
    if prod_dir.exists():
        backup_dir = Path(tempfile.mkdtemp(prefix="prod_skills_backup_"))
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        print(f"{CLR_BOLD}3. Backing up existing production directory to '{backup_dir}'...{CLR_RESET}")
        shutil.copytree(prod_dir, backup_dir)

    # 4. Promote from staging to production
    try:
        print(f"{CLR_BOLD}4. Promoting skills from staging to production directory '{prod_dir}'...{CLR_RESET}")
        if prod_dir.exists():
            shutil.rmtree(prod_dir)
        prod_dir.mkdir(parents=True, exist_ok=True)
        for item in staging_dir.iterdir():
            if item.is_dir():
                shutil.copytree(item, prod_dir / item.name)
            elif item.is_file():
                shutil.copy2(item, prod_dir)
        print(f"✅ {CLR_GREEN}Promotion completed successfully!{CLR_RESET}")

        shutil.rmtree(staging_dir)
        # Clean backup if everything succeeded
        if backup_dir and backup_dir.exists():
            shutil.rmtree(backup_dir)
        return True
    except Exception as e:
        print(f"❌ {CLR_RED}Critical error during promotion: {e}{CLR_RESET}", file=sys.stderr)
        if backup_dir and backup_dir.exists():
            print(f"🔄 {CLR_BOLD}Attempting rollback to previous production state...{CLR_RESET}")
            if prod_dir.exists():
                shutil.rmtree(prod_dir)
            shutil.copytree(backup_dir, prod_dir)
            shutil.rmtree(backup_dir)
            print(f"✅ {CLR_GREEN}Rollback successful.{CLR_RESET}")
        return False


def main():
    use_color = sys.stdout.isatty() and "NO_COLOR" not in os.environ
    CLR_RESET = "\033[0m" if use_color else ""
    CLR_GREEN = "\033[32m" if use_color else ""
    CLR_RED = "\033[31m" if use_color else ""

    parser = argparse.ArgumentParser(description="ESRA Skill Validation & Promotion Utility")
    parser.add_argument("--skills-dir", default="optional-skills/evolutionary-self-dev",
                        help="Path to development skills directory")
    parser.add_argument("--staging-dir", default="/tmp/esra_skills_staging",
                        help="Path to staging skills directory")
    parser.add_argument("--prod-dir", default=str(Path.home() / ".hermes" / "skills" / "evolutionary-self-dev"),
                        help="Path to production skills directory")
    parser.add_argument("--stage", action="store_true",
                        help="Perform staging validation and promotion/rollback")
    parser.add_argument("--verbose", action="store_true",
                        help="Enable verbose output")

    args = parser.parse_args()

    if args.stage:
        success = stage_and_promote(args.skills_dir, Path(args.staging_dir), Path(args.prod_dir), args.verbose)
        sys.exit(0 if success else 1)
    else:
        validator = SkillValidator(Path(args.skills_dir), verbose=args.verbose)
        success, errors, order = validator.run_all_validation()
        if success:
            print(f"✅ {CLR_GREEN}All skills are valid.{CLR_RESET}")
            if order:
                print(f"Dependency loading order: { ' -> '.join(order) }")
            sys.exit(0)
        else:
            print(f"❌ {CLR_RED}Skill validation failed:{CLR_RESET}", file=sys.stderr)
            for skill_name, errs in errors.items():
                print(f"  [{skill_name}]:", file=sys.stderr)
                for err in errs:
                    print(f"    - {err}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
