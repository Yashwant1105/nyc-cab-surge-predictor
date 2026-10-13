# scripts/analyze_cab_surge.py
"""
Command-line entry point to generate the cab-surge Spark plan and analyze it with SparkLens.

Usage:
    python scripts/analyze_cab_surge.py
    python scripts/analyze_cab_surge.py --ai
    python scripts/analyze_cab_surge.py --plan-output artifacts/cab_surge_plan.txt --report-output artifacts/sparklens
"""

import argparse
from pathlib import Path
import sys

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from analysis.spark_plan import generate_cab_surge_plan
from analysis.sparklens_runner import analyze_plan


def main():
    parser = argparse.ArgumentParser(
        description="Generate NYC cab-surge Spark physical plan and analyze with SparkLens."
    )
    parser.add_argument(
        "--plan-output",
        type=Path,
        default=REPO_ROOT / "artifacts" / "cab_surge_plan.txt",
        help="Path where the generated Spark physical plan will be saved (default: artifacts/cab_surge_plan.txt)",
    )
    parser.add_argument(
        "--report-output",
        type=Path,
        default=REPO_ROOT / "artifacts" / "sparklens",
        help="Directory where SparkLens reports and DAG will be saved (default: artifacts/sparklens)",
    )
    parser.add_argument(
        "--ai",
        action="store_true",
        help="Enable AI explanations using Gemini (requires GEMINI_API_KEY)",
    )
    parser.add_argument(
        "--keep-plan",
        action="store_true",
        default=True,
        help="Retain the generated plan file (default: True)",
    )

    args = parser.parse_args()

    print("\n[1/2] Generating Spark physical execution plan...")
    plan_path = generate_cab_surge_plan(output_path=args.plan_output)
    print(f"Generated Spark plan:\n{plan_path}")

    print("\n[2/2] Running SparkLens analysis...")
    result = analyze_plan(
        plan_path=plan_path,
        output_dir=args.report_output,
        enable_ai=args.ai,
    )

    print("\nAnalysis complete! Generated SparkLens artifacts:")
    if result.get("report_md"):
        print(f"  Markdown report : {result['report_md']}")
    if result.get("report_html"):
        print(f"  HTML report     : {result['report_html']}")
    if result.get("dag_png"):
        print(f"  Execution DAG   : {result['dag_png']}")

    if not args.keep_plan and plan_path.exists():
        plan_path.unlink()


if __name__ == "__main__":
    main()

