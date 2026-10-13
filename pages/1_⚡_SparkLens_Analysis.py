"""
Streamlit Page: SparkLens Execution Plan Analysis.

Interactive analysis of the NYC Cab Surge Predictor's PySpark physical execution plan:
- Plan generation from the feature engineering pipeline
- Deterministic performance findings, warnings, and operator diagnostics
- Execution DAG visualization
- Live Markdown & HTML reports with download capabilities
- Optional Google Gemini AI explanations
"""

import os
from pathlib import Path
import streamlit as st

# =============================
# ⚙️ CONFIG
# =============================
st.set_page_config(
    page_title="SparkLens · Plan Analysis",
    page_icon="⚡",
    layout="wide",
)

# =============================
# 💅 CUSTOM CSS — Dark Glassmorphism
# =============================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');

:root {
    --bg:        #070b14;
    --surface:   rgba(255,255,255,0.04);
    --glass:     rgba(255,255,255,0.07);
    --glass-hi:  rgba(255,255,255,0.12);
    --border:    rgba(255,255,255,0.09);
    --accent:    #00d4ff;
    --accent2:   #7b5ea7;
    --green:     #00e5a0;
    --orange:    #ffa94d;
    --red:       #ff6b6b;
    --text:      #e8ecf4;
    --muted:     rgba(232,236,244,0.50);
}

.stApp {
    background: var(--bg) !important;
    background-image:
        radial-gradient(ellipse 80% 50% at 20% 0%, rgba(0,212,255,0.08) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 85% 80%, rgba(123,94,167,0.10) 0%, transparent 55%) !important;
    font-family: 'Syne', sans-serif;
    color: var(--text);
}

.page-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.3rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: var(--text);
    margin-bottom: 0.2rem;
}
.page-title span { color: var(--accent); }

.page-sub {
    font-family: 'DM Mono', monospace;
    font-size: 0.8rem;
    letter-spacing: 0.08em;
    color: var(--muted);
    margin-bottom: 1.5rem;
}

.stat-box {
    background: var(--glass);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.1rem 1.4rem;
    text-align: left;
}
.stat-box .label {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    text-transform: uppercase;
    color: var(--muted);
}
.stat-box .val {
    font-family: 'Syne', sans-serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--text);
    margin-top: 0.2rem;
}

.finding-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
}
.finding-card.severity-high { border-left: 4px solid var(--red); }
.finding-card.severity-medium { border-left: 4px solid var(--orange); }
.finding-card.severity-low { border-left: 4px solid var(--accent); }

[data-testid="stExpander"] {
    background: var(--glass) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
}

[data-testid="stButton"] > button {
    background: linear-gradient(135deg, var(--accent) 0%, #0090b8 100%) !important;
    color: #070b14 !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
}
</style>
""", unsafe_allow_html=True)

# =============================
# 🛡️ DEPENDENCY GUARD
# =============================
try:
    from analysis.spark_plan import generate_cab_surge_plan
    from analysis.sparklens_runner import analyze_plan
    SPARKLENS_AVAILABLE = True
    IMPORT_ERROR = None
except Exception as e:
    SPARKLENS_AVAILABLE = False
    IMPORT_ERROR = str(e)

# Paths
REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PLAN_PATH = REPO_ROOT / "artifacts" / "cab_surge_plan.txt"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "artifacts" / "sparklens"

# =============================
# 🧭 HEADER
# =============================
st.markdown('<div class="page-title">SparkLens <span>Analysis</span></div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-sub">APACHE SPARK PHYSICAL PLAN DIAGNOSTICS & OPTIMIZATION INSIGHTS</div>',
    unsafe_allow_html=True,
)

if not SPARKLENS_AVAILABLE:
    st.error(
        f"**SparkLens or PySpark integration is unavailable in this environment.**\n\n"
        f"Details: `{IMPORT_ERROR}`\n\n"
        "To enable plan generation and analysis, please install optional dependencies:\n"
        "```bash\npip install -r requirements-sparklens.txt\n```"
    )
    st.stop()

# =============================
# ⚙️ SIDEBAR SETTINGS
# =============================
with st.sidebar:
    st.markdown("### ⚡ SparkLens Settings")
    st.markdown(
        "<span style='font-size:0.78rem; color:var(--muted); font-family:\"DM Mono\",monospace;'>"
        "Deterministic analysis runs completely offline. AI mode generates natural language explanations."
        "</span>",
        unsafe_allow_html=True,
    )
    st.divider()

    # Detect API Key from environment or allow entering
    env_api_key = os.getenv("GEMINI_API_KEY", "")
    has_api_key = bool(env_api_key.strip())

    enable_ai = st.toggle(
        "Enable AI Explanations",
        value=has_api_key,
        help="Requires GEMINI_API_KEY. Generates executive summary and root-cause explanations with Gemini.",
    )

    if enable_ai:
        if not has_api_key:
            user_key = st.text_input(
                "Gemini API Key",
                type="password",
                help="Set GEMINI_API_KEY in your local .env or system environment so you never need to re-enter it.",
            )
            if user_key:
                os.environ["GEMINI_API_KEY"] = user_key
                has_api_key = True
            else:
                st.warning("Please provide a Gemini API key or set it in `.env` to enable AI mode.")
        else:
            st.caption("✅ GEMINI_API_KEY detected in environment.")

    st.divider()
    st.markdown("### 📁 Artifact Locations")
    st.caption(f"**Plan File:** `{DEFAULT_PLAN_PATH.name}`")
    st.caption(f"**Reports:** `{DEFAULT_OUTPUT_DIR.name}/`")

# =============================
# 🚀 ACTION BUTTONS
# =============================
col_btn1, col_btn2, _ = st.columns([1.2, 1.2, 2.6])

with col_btn1:
    gen_plan_clicked = st.button("🔨 1. Generate Spark Plan", use_container_width=True)

with col_btn2:
    analyze_clicked = st.button("🔍 2. Run SparkLens Analysis", use_container_width=True)

# Action 1: Generate Plan
if gen_plan_clicked:
    with st.spinner("Generating Spark physical plan from feature engineering pipeline..."):
        try:
            plan_path = generate_cab_surge_plan(output_path=DEFAULT_PLAN_PATH)
            st.session_state["plan_path"] = str(plan_path)
            st.session_state["plan_content"] = plan_path.read_text(encoding="utf-8")
            st.success(f"Spark physical plan generated successfully! ({len(st.session_state['plan_content'])} chars)")
        except Exception as err:
            st.error(f"Failed to generate Spark plan: {err}")

# Action 2: Run Analysis
if analyze_clicked:
    target_plan = st.session_state.get("plan_path") or (str(DEFAULT_PLAN_PATH) if DEFAULT_PLAN_PATH.exists() else None)
    if not target_plan or not Path(target_plan).exists():
        st.warning("Spark physical plan not found. Please click **Generate Spark Plan** first.")
    else:
        with st.spinner("Running SparkLens analyzer & generating visual DAG..."):
            try:
                ai_mode = enable_ai and bool(os.getenv("GEMINI_API_KEY", "").strip())
                result = analyze_plan(
                    plan_path=target_plan,
                    output_dir=DEFAULT_OUTPUT_DIR,
                    enable_ai=ai_mode,
                )
                st.session_state["analysis_result"] = result
                st.success("SparkLens analysis completed successfully!")
            except Exception as err:
                st.error(f"SparkLens analysis failed: {err}")

st.markdown("<br>", unsafe_allow_html=True)

# Load existing files if present
plan_exists = DEFAULT_PLAN_PATH.exists()
report_md_exists = (DEFAULT_OUTPUT_DIR / "report.md").exists()
report_html_exists = (DEFAULT_OUTPUT_DIR / "report.html").exists()
dag_png_exists = (DEFAULT_OUTPUT_DIR / "dag.png").exists()

# =============================
# 📊 METRICS & ARTIFACT VIEW
# =============================
if report_md_exists:
    md_content = (DEFAULT_OUTPUT_DIR / "report.md").read_text(encoding="utf-8", errors="replace")

    # Quick metric derivations from report content
    broadcast_count = md_content.count("Broadcast Hash Join Detected")
    shuffle_count = md_content.count("Shuffle Detected")
    agg_count = md_content.count("Aggregation")
    stages_line = [line for line in md_content.splitlines() if "stages" in line.lower()]

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            '<div class="stat-box"><div class="label">Broadcast Joins</div>'
            f'<div class="val" style="color:var(--accent);">{broadcast_count}</div></div>',
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            '<div class="stat-box"><div class="label">Shuffle Exchanges</div>'
            f'<div class="val" style="color:var(--orange);">{shuffle_count}</div></div>',
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            '<div class="stat-box"><div class="label">Aggregations</div>'
            f'<div class="val" style="color:var(--green);">{agg_count}</div></div>',
            unsafe_allow_html=True,
        )
    with m4:
        stage_num = "3" if not stages_line else "".join(filter(str.isdigit, stages_line[0])) or "3"
        st.markdown(
            '<div class="stat-box"><div class="label">Estimated Stages</div>'
            f'<div class="val">{stage_num}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Tabs for DAG, Report, and Raw Plan
    tab_dag, tab_report, tab_plan, tab_downloads = st.tabs([
        "📈 Execution DAG",
        "📄 SparkLens Report",
        "🔍 Spark Physical Plan",
        "💾 Download Artifacts",
    ])

    with tab_dag:
        if dag_png_exists:
            st.image(str(DEFAULT_OUTPUT_DIR / "dag.png"), caption="Spark Execution Plan DAG", use_container_width=True)
        else:
            st.info("Execution DAG image has not been generated yet. Click 'Run SparkLens Analysis' to generate it.")

    with tab_report:
        st.markdown(md_content)

    with tab_plan:
        if plan_exists:
            plan_text = DEFAULT_PLAN_PATH.read_text(encoding="utf-8", errors="replace")
            st.code(plan_text, language="text")
        else:
            st.info("No plan file found. Click 'Generate Spark Plan' to create one.")

    with tab_downloads:
        st.markdown("### Download Analysis Artifacts")
        d_col1, d_col2, d_col3 = st.columns(3)

        if plan_exists:
            with d_col1:
                st.download_button(
                    label="📥 Download Spark Plan (.txt)",
                    data=DEFAULT_PLAN_PATH.read_bytes(),
                    file_name="cab_surge_plan.txt",
                    mime="text/plain",
                    use_container_width=True,
                )
        if report_md_exists:
            with d_col2:
                st.download_button(
                    label="📥 Download Report (.md)",
                    data=(DEFAULT_OUTPUT_DIR / "report.md").read_bytes(),
                    file_name="sparklens_report.md",
                    mime="text/markdown",
                    use_container_width=True,
                )
        if report_html_exists:
            with d_col3:
                st.download_button(
                    label="📥 Download Report (.html)",
                    data=(DEFAULT_OUTPUT_DIR / "report.html").read_bytes(),
                    file_name="sparklens_report.html",
                    mime="text/html",
                    use_container_width=True,
                )

elif plan_exists:
    st.info("Spark physical plan is ready. Click **Run SparkLens Analysis** above to analyze it.")
    with st.expander("Preview Spark Physical Plan", expanded=True):
        st.code(DEFAULT_PLAN_PATH.read_text(encoding="utf-8", errors="replace"), language="text")
else:
    st.info(
        "👋 Welcome to SparkLens Analysis! Click **Generate Spark Plan** above to extract the "
        "physical execution plan from the NYC Cab Surge feature pipeline and run diagnostic analysis."
    )

