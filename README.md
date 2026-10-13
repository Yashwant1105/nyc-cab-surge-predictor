# NYC Cab Surge Predictor

A real-time taxi demand and surge prediction application for New York City built with Streamlit and PySpark.

---

## Features

- **Surge Probability Estimation**: Predicts surge levels using trained ML models (Logistic Regression, Decision Tree, Random Forest).
- **Interactive Predictor UI**: Real-time sliders and toggles for pickup hour, trip demand, rain, events, weekend, and peak hours.
- **SparkLens Integration**: Generates and analyzes Apache Spark physical execution plans for the training and feature engineering pipeline.

---

## Setup & Installation

### Core Dashboard Dependencies

```bash
python -m venv venv
venv\Scripts\activate   # Windows (or source venv/bin/activate on macOS/Linux)
pip install -r requirements.txt
```

### Running the Dashboard

```bash
streamlit run app.py
```

---

## SparkLens Analysis

SparkLens provides deterministic and AI-assisted analysis of the PySpark physical execution plan behind NYC Cab Surge Predictor's feature engineering pipeline.

### Installation

Install the optional SparkLens dependencies:

```bash
pip install -r requirements-sparklens.txt
```

### Plan Generation & Analysis

Run the end-to-end analysis CLI command:

```bash
python scripts/analyze_cab_surge.py
```

Optional CLI flags:

- `--plan-output PATH`: Path to write the formatted Spark execution plan (default: `artifacts/cab_surge_plan.txt`).
- `--report-output PATH`: Output directory for generated reports and DAG visualization (default: `artifacts/sparklens`).
- `--ai`: Enable AI-assisted explanations using Google Gemini (requires `GEMINI_API_KEY`).

Example with AI analysis:

```bash
python scripts/analyze_cab_surge.py --ai
```

### Output Artifacts

Running the script produces:
- `artifacts/cab_surge_plan.txt`: The captured Spark physical execution plan.
- `artifacts/sparklens/dag.png`: Visual directed acyclic graph of the Spark operators.
- `artifacts/sparklens/report.md`: Markdown report detailing execution findings.
- `artifacts/sparklens/report.html`: Interactive HTML report with execution statistics and recommendations.

### Interactive Dashboard Analysis

You can also run SparkLens interactively within the Streamlit dashboard:

```bash
streamlit run app.py
```

Then switch to the **⚡ SparkLens Analysis** page from the sidebar to:
- Generate the Spark physical execution plan.
- Run deterministic and AI-powered performance analysis.
- Inspect the live execution DAG and structured findings.
- Download reports (`.md`, `.html`) and plan text files directly.

### Running Tests

```bash
pytest tests/
```


