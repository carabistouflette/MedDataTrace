"""Cross-platform development tasks for the research repository."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC_DIR = ROOT / "research" / "specs"
REFERENCE_DIR = SPEC_DIR / "reference_semantics"
GENERATION_DIR = SPEC_DIR / "reference_generation"
CODE_DIRS = (REFERENCE_DIR, GENERATION_DIR)
TASK_RUNNER = ROOT / "scripts" / "tasks.py"
TEMPLATES = (
    SPEC_DIR / "pilot_templates" / "effort_record.template.json",
    SPEC_DIR / "pilot_templates" / "operational_record.json",
    SPEC_DIR / "pilot_templates" / "artifact_reference.WITHHOLD.template.json",
    SPEC_DIR / "pilot_templates" / "reference_derivation.WITHHOLD.template.json",
    SPEC_DIR / "pilot_templates" / "study_record.template.json",
    SPEC_DIR / "pilot_templates" / "artifact_grounded.synthetic.json",
)


def run(*command: str, cwd: Path = ROOT, quiet: bool = False) -> None:
    subprocess.run(command, cwd=cwd, check=True, stdout=subprocess.DEVNULL if quiet else None)


def setup() -> None:
    run("uv", "sync", "--locked")


def test() -> None:
    for test_dir in (REFERENCE_DIR, GENERATION_DIR):
        run(
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-s",
            str(test_dir),
            "-v",
        )


def lint() -> None:
    run("ruff", "check", str(TASK_RUNNER), *(str(path) for path in CODE_DIRS))
    run(
        "ruff",
        "format",
        "--check",
        str(TASK_RUNNER),
        *(str(path) for path in CODE_DIRS),
    )


def typecheck() -> None:
    run("mypy", str(TASK_RUNNER))
    for code_dir in CODE_DIRS:
        run("mypy", ".", cwd=code_dir)


def format_code() -> None:
    run("ruff", "check", "--fix", str(TASK_RUNNER), *(str(path) for path in CODE_DIRS))
    run("ruff", "format", str(TASK_RUNNER), *(str(path) for path in CODE_DIRS))


def check_templates() -> None:
    for template in TEMPLATES:
        run(sys.executable, "-m", "json.tool", str(template), quiet=True)


def check() -> None:
    lint()
    typecheck()
    test()
    check_templates()


def spec() -> None:
    missing = [tool for tool in ("latexmk", "biber") if shutil.which(tool) is None]
    if missing:
        for tool in missing:
            print(f"Missing required TeX prerequisite: {tool}", file=sys.stderr)
        print("Install both latexmk and biber, then rerun the specification task.", file=sys.stderr)
        print(
            "Without local TeX packages, use the GitHub Actions Specification job to build the PDF.",
            file=sys.stderr,
        )
        raise SystemExit(1)
    run(
        "latexmk",
        "-pdf",
        "-interaction=nonstopmode",
        "-halt-on-error",
        "meddatatrace_specification.tex",
        cwd=SPEC_DIR,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "task",
        choices=(
            "setup",
            "test",
            "lint",
            "typecheck",
            "format",
            "check-templates",
            "check",
            "spec",
        ),
    )
    args = parser.parse_args()
    tasks = {
        "setup": setup,
        "test": test,
        "lint": lint,
        "typecheck": typecheck,
        "format": format_code,
        "check-templates": check_templates,
        "check": check,
        "spec": spec,
    }
    tasks[args.task]()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
