# analysis/sparklens_runner.py
"""
SparkLens Runner for NYC Cab Surge Predictor.

Analyzes a Spark physical execution plan using SparkLens (via Python API or CLI subprocess)
and places reports and visualizations into the specified output directory.
"""

import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any


def _find_sparklens_command() -> list[str]:
    """
    Determine how to execute SparkLens CLI on this system.
    Returns the command prefix as a list of strings.
    """
    # 1. Check if sparklens executable is in PATH
    sparklens_bin = shutil.which("sparklens")
    if sparklens_bin:
        return [sparklens_bin]

    # 2. Check sibling SparkLens checkout virtualenv or directory
    repo_root = Path(__file__).resolve().parent.parent
    sparklens_sibling = repo_root.parent.parent / "SparkLens"
    sibling_venv_python = sparklens_sibling / ".venv-demo" / "Scripts" / "python.exe"
    if sibling_venv_python.exists():
        return [str(sibling_venv_python), "-m", "cli.main"]

    sibling_venv_bin = sparklens_sibling / ".venv-demo" / "bin" / "python"
    if sibling_venv_bin.exists():
        return [str(sibling_venv_bin), "-m", "cli.main"]

    # 3. Fall back to current python running cli.main
    return [sys.executable, "-m", "cli.main"]


def analyze_plan(
    plan_path: str | Path,
    output_dir: str | Path,
    enable_ai: bool = False,
    sparklens_cwd: str | Path | None = None,
) -> dict[str, Any]:
    """
    Analyze a Spark physical plan with SparkLens.

    :param plan_path: Path to the formatted Spark physical plan text file
    :param output_dir: Directory where report.md, report.html, and dag.png will be placed
    :param enable_ai: Whether to enable AI explanation (requires GEMINI_API_KEY)
    :param sparklens_cwd: Working directory for SparkLens execution (optional)
    :return: Dictionary containing status, output artifact paths, and metadata
    """
    plan_p = Path(plan_path).resolve()
    if not plan_p.exists():
        raise FileNotFoundError(f"Plan file not found: {plan_p}")

    out_d = Path(output_dir).resolve()
    out_d.mkdir(parents=True, exist_ok=True)

    # First attempt: In-process direct API if sparklens is imported directly
    try:
        from analyzer.analyzer import SparkAnalyzer
        from report import ReportGenerator, MarkdownRenderer, HTMLRenderer
        from visualization import DAGVisualizer

        plan_content = plan_p.read_text(encoding="utf-8")
        analyzer = SparkAnalyzer()
        analysis = analyzer.analyze_plan(plan_content)

        explanation = None
        if enable_ai:
            from ai.gemini_provider import GeminiProvider
            from ai.prompt_builder import PromptBuilder
            provider = GeminiProvider()
            prompt = PromptBuilder().build(analysis)
            explanation = provider.explain(prompt)

        # Generate report
        report = ReportGenerator().generate(analysis, explanation)
        md_file = out_d / "report.md"
        html_file = out_d / "report.html"
        dag_file = out_d / "dag.png"

        MarkdownRenderer().save(report, str(md_file))
        HTMLRenderer().save(report, str(html_file))

        try:
            DAGVisualizer().visualize(analysis.dag, str(dag_file))
        except Exception:
            pass

        return {
            "status": "success",
            "plan_path": str(plan_p),
            "output_dir": str(out_d),
            "report_md": str(md_file) if md_file.exists() else None,
            "report_html": str(html_file) if html_file.exists() else None,
            "dag_png": str(dag_file) if dag_file.exists() else None,
            "findings_count": len(analysis.report.findings) if analysis.report else 0,
        }
    except ImportError:
        # Fallback to subprocess invocation
        pass

    # Subprocess path
    cmd_prefix = _find_sparklens_command()
    cmd = list(cmd_prefix) + ["analyze", str(plan_p)]
    if enable_ai:
        cmd.append("--ai")

    work_dir = Path(sparklens_cwd).resolve() if sparklens_cwd else out_d

    try:
        proc = subprocess.run(
            cmd,
            cwd=str(work_dir),
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError as err:
        raise RuntimeError(
            f"Failed to run SparkLens command '{' '.join(cmd)}': {err}. "
            "Please ensure SparkLens is installed or available."
        ) from err
    except subprocess.CalledProcessError as err:
        raise RuntimeError(
            f"SparkLens execution failed with exit code {err.returncode}.\n"
            f"STDOUT:\n{err.stdout}\nSTDERR:\n{err.stderr}"
        ) from err

    # If SparkLens produced dag.png / report.md / report.html in work_dir, move or copy them to out_d if distinct
    expected_files = ["report.md", "report.html", "dag.png"]
    for fname in expected_files:
        src = work_dir / fname
        dest = out_d / fname
        if src.exists() and src != dest:
            shutil.copy2(src, dest)

    md_file = out_d / "report.md"
    html_file = out_d / "report.html"
    dag_file = out_d / "dag.png"

    return {
        "status": "success",
        "plan_path": str(plan_p),
        "output_dir": str(out_d),
        "report_md": str(md_file) if md_file.exists() else None,
        "report_html": str(html_file) if html_file.exists() else None,
        "dag_png": str(dag_file) if dag_file.exists() else None,
        "stdout": proc.stdout,
    }

