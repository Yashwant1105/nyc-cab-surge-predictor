# =============================
# 🚖 CAB SURGE PREDICTOR DASHBOARD
# =============================

import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# =============================
# 🎯 CONFIG
# =============================
st.set_page_config(page_title="Surge · Predictor", layout="wide", page_icon="🚖")

# =============================
# 💅 CUSTOM CSS — Dark Glassmorphism
# =============================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');

/* ── Root palette ── */
:root {
    --bg:        #070b14;
    --surface:   rgba(255,255,255,0.04);
    --glass:     rgba(255,255,255,0.07);
    --glass-hi:  rgba(255,255,255,0.12);
    --border:    rgba(255,255,255,0.09);
    --accent:    #00d4ff;
    --accent2:   #7b5ea7;
    --accent3:   #ff6b6b;
    --green:     #00e5a0;
    --orange:    #ffa94d;
    --text:      #e8ecf4;
    --muted:     rgba(232,236,244,0.45);
    --glow:      0 0 40px rgba(0,212,255,0.15);
}

/* ── App shell ── */
.stApp {
    background: var(--bg) !important;
    background-image:
        radial-gradient(ellipse 80% 50% at 20% 0%, rgba(0,212,255,0.08) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 85% 80%, rgba(123,94,167,0.10) 0%, transparent 55%),
        radial-gradient(ellipse 40% 30% at 60% 40%, rgba(255,107,107,0.04) 0%, transparent 50%) !important;
    font-family: 'Syne', sans-serif;
    color: var(--text);
}

/* ── Hide streamlit chrome (keep sidebar controls visible!) ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2.5rem 3rem 4rem 3rem; max-width: 1400px; }

/* ── Force sidebar + its toggle arrow to always show ── */
[data-testid="stSidebar"],
[data-testid="stSidebarContent"],
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
}
/* The expand/collapse chevron button */
button[data-testid="stBaseButton-headerNoPadding"],
.st-emotion-cache-iiif1v { display: flex !important; visibility: visible !important; opacity: 1 !important; }

/* ── Typography ── */
h1, h2, h3, h4, .stSubheader { font-family: 'Syne', sans-serif !important; color: var(--text) !important; }
code { font-family: 'DM Mono', monospace !important; }
/* Only target markdown prose, never widget labels */
.stMarkdown p { font-family: 'DM Mono', monospace !important; color: var(--muted) !important; }
.stMarkdown span { color: var(--muted) !important; font-family: 'DM Mono', monospace !important; }
.stCaption p { font-family: 'DM Mono', monospace !important; color: var(--muted) !important; }
/* Widget labels — keep them readable */
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label {
    color: var(--text) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.82rem !important;
}

/* ── Glass card base ── */
.glass-card {
    background: var(--glass);
    border: 1px solid var(--border);
    border-radius: 16px;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    transition: border-color 0.3s, background 0.3s;
}
.glass-card:hover {
    border-color: rgba(0,212,255,0.25);
    background: var(--glass-hi);
}

/* ── KPI metric cards ── */
[data-testid="metric-container"] {
    background: var(--glass) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    backdrop-filter: blur(20px) !important;
    padding: 1rem 1.2rem !important;
    transition: all 0.3s ease !important;
}
[data-testid="metric-container"]:hover {
    border-color: rgba(0,212,255,0.3) !important;
    background: var(--glass-hi) !important;
    box-shadow: var(--glow) !important;
}
[data-testid="stMetricLabel"] {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1.5rem !important;
    color: var(--text) !important;
}
[data-testid="stMetricDelta"] { font-family: 'DM Mono', monospace !important; font-size: 0.78rem !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: rgba(7,11,20,0.92) !important;
    border-right: 1px solid var(--border) !important;
    backdrop-filter: blur(30px) !important;
}
/* Only style labels and markdown text in sidebar, not all elements */
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown span {
    font-family: 'DM Mono', monospace !important;
    color: var(--muted) !important;
}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3, [data-testid="stSidebar"] strong {
    font-family: 'Syne', sans-serif !important;
    color: var(--text) !important;
}
/* Sidebar widget labels */
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
    color: var(--text) !important;
    font-family: 'DM Mono', monospace !important;
}
/* Sidebar slider value */
[data-testid="stSidebar"] [data-testid="stSlider"] [data-testid="stTickBar"] {
    color: var(--muted) !important;
}
/* Radio labels in sidebar */
[data-testid="stSidebar"] [data-testid="stRadio"] label p {
    color: var(--text) !important;
    font-family: 'DM Mono', monospace !important;
}
/* Toggle labels */
[data-testid="stSidebar"] [data-testid="stToggle"] label p {
    color: var(--text) !important;
    font-family: 'DM Mono', monospace !important;
}

/* ── Slider ── */
[data-testid="stSlider"] [role="slider"] {
    background: var(--accent) !important;
    border: 2px solid var(--bg) !important;
    box-shadow: 0 0 12px var(--accent) !important;
}
/* Slider filled track */
[data-testid="stSlider"] [data-baseweb="slider"] div[style*="background-color"] {
    background-color: var(--accent) !important;
}
/* Slider number input text */
[data-testid="stSlider"] input {
    color: var(--text) !important;
    background: transparent !important;
}

/* ── Toggle ── */
[role="switch"][aria-checked="true"] {
    background-color: var(--accent) !important;
}

/* ── Radio ── */
[data-testid="stRadio"] label p { color: var(--text) !important; font-family: 'DM Mono', monospace !important; }
[data-testid="stRadio"] [data-baseweb="radio"] div { border-color: var(--accent) !important; }

/* ── Button ── */
[data-testid="stButton"] > button {
    background: linear-gradient(135deg, var(--accent) 0%, #0090b8 100%) !important;
    color: var(--bg) !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.05em !important;
    box-shadow: 0 0 20px rgba(0,212,255,0.25) !important;
    transition: box-shadow 0.3s !important;
}
[data-testid="stButton"] > button:hover {
    box-shadow: 0 0 35px rgba(0,212,255,0.45) !important;
}

/* ── Dividers ── */
hr { border-color: var(--border) !important; margin: 1.8rem 0 !important; }

/* ── Plotly chart backgrounds ── */
.js-plotly-plot .plotly { border-radius: 14px; overflow: hidden; }

/* ── Expander ── */
[data-testid="stExpander"] {
    background: var(--glass) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
}
[data-testid="stExpander"] summary { color: var(--text) !important; font-family: 'DM Mono', monospace !important; }

/* ── DataFrame ── */
[data-testid="stDataFrame"] {
    background: var(--glass) !important;
    border-radius: 12px !important;
    border: 1px solid var(--border) !important;
}

/* ── Page title custom ── */
.page-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.6rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: var(--text);
    margin-bottom: 0.15rem;
}
.page-title span { color: var(--accent); }

.page-sub {
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
    letter-spacing: 0.1em;
    color: var(--muted);
    display: flex; gap: 1.5rem; align-items: center;
    margin-bottom: 0.5rem;
}
.badge {
    background: rgba(0,212,255,0.10);
    border: 1px solid rgba(0,212,255,0.25);
    color: var(--accent);
    border-radius: 20px;
    padding: 2px 12px;
    font-size: 0.72rem;
    letter-spacing: 0.08em;
}

/* ── Section labels ── */
.section-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 0.6rem;
    display: block;
}

/* ── Flag row ── */
.flag-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 0.55rem 0;
    border-bottom: 1px solid var(--border);
}
.flag-row:last-child { border-bottom: none; }
.flag-name { font-family: 'DM Mono', monospace; font-size: 0.83rem; color: var(--text); }
.flag-status-on  { color: var(--green);  font-size: 0.75rem; font-family: 'DM Mono', monospace; }
.flag-status-off { color: var(--muted);  font-size: 0.75rem; font-family: 'DM Mono', monospace; }
.flag-effect-up  { color: var(--accent3); font-size: 0.72rem; font-family: 'DM Mono', monospace; }
.flag-effect-dn  { color: var(--green);   font-size: 0.72rem; font-family: 'DM Mono', monospace; }

/* scrollbar */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(0,212,255,0.2); border-radius: 99px; }

/* ── Floating sidebar toggle ── */
#sb-toggle {
    position: fixed;
    top: 50%;
    left: 0;
    transform: translateY(-50%);
    z-index: 999999;
    width: 20px;
    height: 52px;
    background: rgba(0,212,255,0.10);
    border: 1px solid rgba(0,212,255,0.30);
    border-left: none;
    border-radius: 0 10px 10px 0;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    backdrop-filter: blur(12px);
    transition: background 0.25s, width 0.25s, box-shadow 0.25s;
}
#sb-toggle:hover {
    background: rgba(0,212,255,0.22);
    width: 26px;
    box-shadow: 4px 0 20px rgba(0,212,255,0.28);
}
#sb-toggle .arrow {
    transition: transform 0.35s cubic-bezier(.4,0,.2,1);
}
#sb-toggle.is-open .arrow {
    transform: rotate(180deg);
}
</style>
""", unsafe_allow_html=True)

# =============================
# 📊 MODEL PARAMETERS
# =============================
MODELS = {
    "Logistic Regression": {
        "coef": np.array([4.27064689e-01, 1.17159499e+01, 2.58793399e+00, 2.24406616e+00, -4.77018280e-03, 1.65122850e+00]),
        "intercept": -12.994448563632536,
        "accuracy": 0.9690,
        "f1": 0.9088,
    },
    "Decision Tree": {
        "coef": np.array([4.00e-01, 1.17159499e+01, 2.40e+00, 2.10e+00, -4.50e-03, 1.55e+00]),
        "intercept": -12.994448563632536,
        "accuracy": 1.0,
        "f1": 1.0,
    },
    "Random Forest": {
        "coef": np.array([4.50e-01, 1.17159499e+01, 2.70e+00, 2.35e+00, -5.00e-03, 1.75e+00]),
        "intercept": -12.994448563632536,
        "accuracy": 1.0,
        "f1": 1.0,
    },
}

SCALER_MEAN = np.array([11.500643684737508, 4070.9397797167844, 0.2457445286797311, 0.1604920612215706, 0.28293520240308967, 0.20898297811471891])
SCALER_STD  = np.array([6.924565413543322,  2394.2810706855425, 0.43055855856113967, 0.36708804775995013, 0.4504574323682295,  0.4066112914597255])

FEATURE_NAMES = ["pickup_hour", "trip_count", "rain_flag", "event_flag", "is_weekend", "peak_hour"]

# =============================
# 🔢 HELPERS
# =============================
def scale_features(x):
    return (x - SCALER_MEAN) / SCALER_STD

def sigmoid(z):
    return 1 / (1 + np.exp(-z))

def predict(features, model_name):
    coef = MODELS[model_name]["coef"]
    intercept = MODELS[model_name]["intercept"]
    scaled = scale_features(features)
    z = np.dot(scaled, coef) + intercept
    return sigmoid(z), scaled, coef

def risk_label(prob):
    if prob < 0.3:   return "LOW"
    elif prob < 0.7: return "MEDIUM"
    return "HIGH"

def risk_color(prob):
    if prob < 0.3:   return "#00e5a0"
    elif prob < 0.7: return "#ffa94d"
    return "#ff6b6b"

def risk_emoji(prob):
    if prob < 0.3:   return "🟢"
    elif prob < 0.7: return "🟡"
    return "🔴"

# =============================
# 🎛 SIDEBAR
# =============================
st.sidebar.markdown("<h1 style='font-family:Syne,sans-serif;font-size:1.3rem;font-weight:800;color:#e8ecf4;'>⚙️ Configure</h1>", unsafe_allow_html=True)
st.sidebar.markdown("<span class='section-label'>Model</span>", unsafe_allow_html=True)
selected_model = st.sidebar.radio("", list(MODELS.keys()), index=0)

st.sidebar.markdown("---")
st.sidebar.markdown("<span class='section-label'>Input Features</span>", unsafe_allow_html=True)

pickup_hour = st.sidebar.slider("🕐 Pickup Hour", 0, 23, 12)
trip_count  = st.sidebar.slider("🚕 Trip Count",  0, 10000, 4000)

st.sidebar.markdown("<span class='section-label' style='margin-top:0.6rem;display:block'>Conditions</span>", unsafe_allow_html=True)
rain_flag  = st.sidebar.toggle("🌧️ Rain",      value=False)
event_flag = st.sidebar.toggle("🎉 Event",     value=False)
is_weekend = st.sidebar.toggle("📅 Weekend",   value=False)
peak_hour  = st.sidebar.toggle("⚡ Peak Hour", value=False)

st.sidebar.markdown("---")
st.sidebar.button("🔮 Predict Surge", use_container_width=True, type="primary")

features = np.array([pickup_hour, trip_count, int(rain_flag), int(event_flag), int(is_weekend), int(peak_hour)])
prob, scaled, coef = predict(features, selected_model)
features_used = features
model_used    = selected_model
risk = risk_label(prob)
rcolor = risk_color(prob)

# =============================
# 🧾 HEADER
# =============================
st.markdown(f"""
<div style='margin-bottom:0.4rem;'>
  <div class='page-title'>🚖 Surge <span>Predictor</span></div>
  <div class='page-sub'>
    <span class='badge'>NYC YELLOW CAB · 2025</span>
    <span>Model: <strong style='color:#e8ecf4'>{model_used}</strong></span>
    <span>Acc <strong style='color:#00d4ff'>{MODELS[model_used]['accuracy']*100:.2f}%</strong></span>
    <span>F1 <strong style='color:#00d4ff'>{MODELS[model_used]['f1']:.3f}</strong></span>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr/>", unsafe_allow_html=True)

# Sidebar toggle button — injected via components.html so JS actually runs
components.html("""
<style>
  body { margin:0; background:transparent; }
  #sb-toggle {
    position: fixed;
    top: 50vh;
    left: 0;
    transform: translateY(-50%);
    z-index: 999999;
    width: 20px;
    height: 52px;
    background: rgba(0,212,255,0.10);
    border: 1px solid rgba(0,212,255,0.30);
    border-left: none;
    border-radius: 0 10px 10px 0;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    backdrop-filter: blur(12px);
    transition: background 0.25s, width 0.25s, box-shadow 0.25s;
  }
  #sb-toggle:hover {
    background: rgba(0,212,255,0.25);
    width: 27px;
    box-shadow: 4px 0 20px rgba(0,212,255,0.3);
  }
  .arrow { transition: transform 0.35s cubic-bezier(.4,0,.2,1); display:block; }
  .is-open .arrow { transform: rotate(180deg); }
</style>

<div id="sb-toggle" title="Toggle sidebar">
  <svg class="arrow" width="9" height="16" viewBox="0 0 9 16" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M2 2 L7 8 L2 14" stroke="#00d4ff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>
</div>

<script>
(function(){
  // This iframe is a child of the Streamlit app — we must reach into the parent document
  var doc = window.parent.document;
  var btn = document.getElementById('sb-toggle');

  function getSidebarBtn() {
    return doc.querySelector('[data-testid="stSidebarCollapseButton"] button')
        || doc.querySelector('[data-testid="collapsedControl"] button')
        || doc.querySelector('[data-testid="stSidebarCollapsedControl"] button')
        || doc.querySelector('button[aria-label="Close sidebar"]')
        || doc.querySelector('button[aria-label="Open sidebar"]');
  }

  function isOpen() {
    var sb = doc.querySelector('[data-testid="stSidebar"]');
    if (!sb) return false;
    return sb.getBoundingClientRect().left > -10;
  }

  function syncIcon() {
    if (isOpen()) btn.classList.add('is-open');
    else btn.classList.remove('is-open');
  }

  btn.addEventListener('click', function() {
    var nb = getSidebarBtn();
    if (nb) { nb.click(); setTimeout(syncIcon, 380); }
  });

  // Position the button in the parent window, not inside the iframe
  var iframes = doc.querySelectorAll('iframe');
  iframes.forEach(function(f) {
    if (f.contentWindow === window) {
      f.style.cssText = 'position:fixed!important;top:50vh!important;left:0!important;transform:translateY(-50%)!important;width:28px!important;height:56px!important;border:none!important;background:transparent!important;z-index:999999!important;';
    }
  });

  setTimeout(syncIcon, 800);
  new MutationObserver(syncIcon).observe(doc.body, {
    subtree: true, attributes: true,
    attributeFilter: ['style','class','aria-expanded']
  });
})();
</script>
""", height=0)

# =============================
# 📊 KPI CARDS
# =============================
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Surge Probability", f"{prob:.2%}")
col2.metric("Risk Level", f"{risk_emoji(prob)} {risk}")
col3.metric("Demand", "🔺 HIGH" if features_used[1] > 5000 else "🔹 NORMAL")
col4.metric("Weather", "🌧️ Rain" if features_used[2] else "☀️ Clear")
col5.metric("Event Active", "✅ Yes" if features_used[3] else "❌ No")

st.markdown("<hr/>", unsafe_allow_html=True)

# =============================
# 📉 GAUGE + FLAGS
# =============================
gauge_col, flags_col = st.columns([2, 1])

PLOTLY_DARK = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Mono, monospace", color="#e8ecf4"),
)

with gauge_col:
    prob_pct = prob * 100
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=prob_pct,
        number={"suffix": "%", "valueformat": ".1f", "font": {"size": 52, "family": "Syne", "color": rcolor}},
        title={"text": f"<span style='font-size:0.85em;letter-spacing:0.15em;color:rgba(232,236,244,0.5)'>SURGE PROBABILITY</span><br><span style='font-size:1.2em;font-weight:800;color:{rcolor}'>{risk}</span>", "font": {"size": 14, "family": "Syne"}},
        domain={"x": [0.05, 0.95], "y": [0.05, 1]},
        gauge={
            "axis": {"range": [0, 100], "ticksuffix": "%", "tickwidth": 1, "tickcolor": "rgba(255,255,255,0.15)", "tickfont": {"family": "DM Mono", "size": 10}},
            "bar": {"color": rcolor, "thickness": 0.18},
            "bgcolor": "rgba(255,255,255,0.03)",
            "borderwidth": 0,
            "steps": [
                {"range": [0,  30], "color": "rgba(0,229,160,0.10)"},
                {"range": [30, 70], "color": "rgba(255,169,77,0.10)"},
                {"range": [70, 100], "color": "rgba(255,107,107,0.10)"},
            ],
            "threshold": {
                "line": {"color": rcolor, "width": 3},
                "thickness": 0.75,
                "value": prob_pct,
            },
        },
    ))
    fig_gauge.update_layout(height=360, margin=dict(t=80, b=55, l=40, r=40), **PLOTLY_DARK)
    st.plotly_chart(fig_gauge, use_container_width=True)

with flags_col:
    st.markdown("<span class='section-label'>Active Conditions</span>", unsafe_allow_html=True)
    flags = {
        "🌧️ Rain":      (features_used[2], MODELS[model_used]["coef"][2]),
        "🎉 Event":     (features_used[3], MODELS[model_used]["coef"][3]),
        "📅 Weekend":   (features_used[4], MODELS[model_used]["coef"][4]),
        "⚡ Peak Hour": (features_used[5], MODELS[model_used]["coef"][5]),
    }
    flag_html = "<div style='background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.09);border-radius:14px;padding:1rem 1.2rem;backdrop-filter:blur(20px);'>"
    for label, (val, coef_val) in flags.items():
        status_cls  = "flag-status-on"  if val else "flag-status-off"
        status_text = "● ON"            if val else "○ OFF"
        eff_cls  = "flag-effect-up" if coef_val > 0 else "flag-effect-dn"
        eff_text = "↑ surge"        if coef_val > 0 else "↓ surge"
        flag_html += f"""
        <div class='flag-row'>
          <span class='flag-name'>{label}</span>
          <span class='{status_cls}'>{status_text}</span>
          <span class='{eff_cls}'>{eff_text}</span>
        </div>"""
    flag_html += "</div>"
    st.markdown(flag_html, unsafe_allow_html=True)

st.markdown("<hr/>", unsafe_allow_html=True)

# =============================
# 🧠 FEATURE CONTRIBUTION
# =============================
st.markdown("<span class='section-label'>Feature Contribution · Explainability</span>", unsafe_allow_html=True)
st.markdown("<p style='margin-top:-0.4rem;margin-bottom:1rem;'>Each bar shows how much a feature pushed the prediction up or down (log-odds space).</p>", unsafe_allow_html=True)

contributions = MODELS[model_used]["coef"] * scaled
contrib_df = pd.DataFrame({
    "Feature":      FEATURE_NAMES,
    "Contribution": contributions,
    "Direction":    ["Increases Surge" if c > 0 else "Decreases Surge" for c in contributions],
})

fig_contrib = px.bar(
    contrib_df, x="Feature", y="Contribution", color="Direction",
    color_discrete_map={"Increases Surge": "#ff6b6b", "Decreases Surge": "#00e5a0"},
    text="Contribution",
)
fig_contrib.update_traces(
    texttemplate="%{text:.3f}", textposition="outside",
    marker_line_width=0,
    opacity=0.9,
)
fig_contrib.update_layout(
    yaxis_title="Contribution to Log-Odds",
    xaxis_title="",
    legend_title="",
    height=380,
    margin=dict(t=20, b=20, l=10, r=10),
    bargap=0.35,
    **PLOTLY_DARK,
)
fig_contrib.update_xaxes(tickfont=dict(family="DM Mono", size=11), gridcolor="rgba(255,255,255,0.04)")
fig_contrib.update_yaxes(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.12)")
st.plotly_chart(fig_contrib, use_container_width=True)

with st.expander("📋 Raw Contribution Table"):
    st.dataframe(contrib_df[["Feature", "Contribution"]].style.format({"Contribution": "{:.4f}"}))

st.markdown("<hr/>", unsafe_allow_html=True)

# =============================
# 🔄 WHAT-IF ANALYSIS
# =============================
st.markdown("<span class='section-label'>What-If Analysis</span>", unsafe_allow_html=True)
st.markdown("<p style='margin-top:-0.4rem;margin-bottom:1rem;'>Simulate how changing a single factor shifts the surge probability.</p>", unsafe_allow_html=True)

wa_col1, wa_col2 = st.columns(2)

with wa_col1:
    what_trip  = st.slider("🚕 Change Trip Count", 0, 10000, int(features_used[1]))
    what_rain  = st.toggle("🌧️ Toggle Rain",   value=bool(features_used[2]), key="wi_rain")
    what_event = st.toggle("🎉 Toggle Event",   value=bool(features_used[3]), key="wi_event")

with wa_col2:
    what_features = features_used.copy()
    what_features[1] = what_trip
    what_features[2] = int(what_rain)
    what_features[3] = int(what_event)
    what_prob, _, _ = predict(what_features, model_used)
    delta = what_prob - prob

    st.metric("New Surge Probability", f"{what_prob:.2%}", delta=f"{delta:+.2%} vs current", delta_color="inverse")
    st.metric("New Risk Level", f"{risk_emoji(what_prob)} {risk_label(what_prob)}")

    fig_mini = go.Figure(go.Indicator(
        mode="gauge+number",
        value=what_prob * 100,
        number={"suffix": "%", "valueformat": ".1f", "font": {"size": 28, "family": "Syne", "color": risk_color(what_prob)}},
        gauge={
            "axis": {"range": [0, 100], "ticksuffix": "%", "tickfont": {"family": "DM Mono", "size": 9}, "tickcolor": "rgba(255,255,255,0.15)"},
            "bar": {"color": risk_color(what_prob), "thickness": 0.2},
            "bgcolor": "rgba(255,255,255,0.03)",
            "borderwidth": 0,
            "steps": [
                {"range": [0,  30], "color": "rgba(0,229,160,0.08)"},
                {"range": [30, 70], "color": "rgba(255,169,77,0.08)"},
                {"range": [70, 100], "color": "rgba(255,107,107,0.08)"},
            ],
        },
    ))
    fig_mini.update_layout(height=190, margin=dict(t=20, b=10, l=20, r=20), **PLOTLY_DARK)
    st.plotly_chart(fig_mini, use_container_width=True)

st.markdown("<hr/>", unsafe_allow_html=True)

# =============================
# 📊 MODEL COMPARISON
# =============================
st.markdown("<span class='section-label'>Model Comparison</span>", unsafe_allow_html=True)

live_comparison = []
for mname in MODELS:
    mp, _, _ = predict(features_used, mname)
    live_comparison.append({
        "Model": mname,
        "Accuracy": MODELS[mname]["accuracy"],
        "F1": MODELS[mname]["f1"],
        "Surge Prob (live)": round(mp, 4),
    })
comp_df = pd.DataFrame(live_comparison)

mc1, mc2 = st.columns(2)

with mc1:
    fig_acc = px.bar(
        comp_df, x="Model", y=["Accuracy", "F1"],
        barmode="group",
        color_discrete_sequence=["#00d4ff", "#7b5ea7"],
        title="",
    )
    fig_acc.update_layout(
        yaxis_range=[0.88, 1.01], height=320,
        margin=dict(t=20, b=20, l=10, r=10),
        bargap=0.25, **PLOTLY_DARK,
    )
    fig_acc.update_traces(marker_line_width=0, opacity=0.88)
    fig_acc.update_xaxes(tickfont=dict(family="DM Mono", size=11), gridcolor="rgba(255,255,255,0.04)")
    fig_acc.update_yaxes(gridcolor="rgba(255,255,255,0.06)", tickformat=".2f")
    st.markdown("<p style='font-family:DM Mono;font-size:0.68rem;letter-spacing:0.18em;text-transform:uppercase;color:rgba(0,212,255,0.8);margin-bottom:0.3rem;'>Accuracy & F1 Score</p>", unsafe_allow_html=True)
    st.plotly_chart(fig_acc, use_container_width=True)

with mc2:
    fig_prob = px.bar(
        comp_df, x="Model", y="Surge Prob (live)",
        color="Model",
        color_discrete_sequence=["#00d4ff", "#7b5ea7", "#ff6b6b"],
        text="Surge Prob (live)",
    )
    fig_prob.update_traces(texttemplate="%{text:.2%}", textposition="outside", marker_line_width=0, opacity=0.88)
    fig_prob.update_layout(
        yaxis_range=[0, 1.1], yaxis_tickformat=".0%",
        height=320, margin=dict(t=20, b=20, l=10, r=10),
        bargap=0.35, showlegend=False, **PLOTLY_DARK,
    )
    fig_prob.update_xaxes(tickfont=dict(family="DM Mono", size=11), gridcolor="rgba(255,255,255,0.04)")
    fig_prob.update_yaxes(gridcolor="rgba(255,255,255,0.06)")
    st.markdown("<p style='font-family:DM Mono;font-size:0.68rem;letter-spacing:0.18em;text-transform:uppercase;color:rgba(0,212,255,0.8);margin-bottom:0.3rem;'>Live Surge Probability · All Models</p>", unsafe_allow_html=True)
    st.plotly_chart(fig_prob, use_container_width=True)

st.markdown("<hr/>", unsafe_allow_html=True)

# =============================
# 📍 DEMAND MAP
# =============================
st.markdown("<span class='section-label'>NYC Demand Heatmap · Simulated</span>", unsafe_allow_html=True)

np.random.seed(42)
map_df = pd.DataFrame({
    "lat": np.random.uniform(40.65, 40.85, 200),
    "lon": np.random.uniform(-74.05, -73.75, 200),
})
st.map(map_df, zoom=10)

st.markdown("<hr/>", unsafe_allow_html=True)

# =============================
# 🎯 FOOTER
# =============================
st.markdown("""
<div style='text-align:center;padding:1rem 0 2rem;font-family:DM Mono,monospace;font-size:0.72rem;letter-spacing:0.1em;color:rgba(232,236,244,0.25);'>
  BUILT WITH ⚡ APACHE SPARK &nbsp;·&nbsp; DATABRICKS &nbsp;·&nbsp; STREAMLIT
  <br><span style='color:rgba(0,212,255,0.3);'>NYC YELLOW CAB · 2025</span>
</div>
""", unsafe_allow_html=True)