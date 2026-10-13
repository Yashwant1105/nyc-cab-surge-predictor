"""
Tests for SparkLens integration and predictor pipeline.
"""

from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock

from analysis.spark_plan import generate_cab_surge_plan
from analysis.sparklens_runner import analyze_plan, _find_sparklens_command
from pipeline.cab_surge_pipeline import build_training_dataframe


def test_sparklens_command_resolution():
    cmd = _find_sparklens_command()
    assert isinstance(cmd, list)
    assert len(cmd) > 0


def test_generate_cab_surge_plan(tmp_path):
    output_file = tmp_path / "test_cab_plan.txt"
    plan_path = generate_cab_surge_plan(output_path=output_file)

    assert plan_path.exists()
    assert plan_path == output_file
    content = output_file.read_text(encoding="utf-8")
    assert "== Physical Plan ==" in content
    assert "BroadcastHashJoin" in content or "HashAggregate" in content


def test_analyze_plan_missing_file(tmp_path):
    missing_plan = tmp_path / "nonexistent.txt"
    out_dir = tmp_path / "out"

    with pytest.raises(FileNotFoundError):
        analyze_plan(plan_path=missing_plan, output_dir=out_dir)


def test_analyze_plan_deterministic(tmp_path):
    # Use real formatted plan from generated artifacts or sample plan
    repo_root = Path(__file__).resolve().parent.parent
    sample_plan = repo_root / "artifacts" / "cab_surge_plan.txt"
    if not sample_plan.exists():
        sample_plan = repo_root.parent.parent / "SparkLens" / "sample_plans" / "aggregation.txt"

    out_dir = tmp_path / "output"
    result = analyze_plan(plan_path=sample_plan, output_dir=out_dir)

    assert result["status"] == "success"
    assert Path(result["report_md"]).exists()
    assert Path(result["report_html"]).exists()
    assert Path(result["dag_png"]).exists()


def test_sparklens_page_import():
    import importlib
    mod = importlib.import_module("pages.1_⚡_SparkLens_Analysis")
    assert mod.SPARKLENS_AVAILABLE is True
    assert mod.DEFAULT_PLAN_PATH is not None


