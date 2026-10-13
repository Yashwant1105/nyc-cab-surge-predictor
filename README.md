# 🚖 NYC Cab Surge Price Predictor

A machine learning dashboard that predicts surge pricing probability for NYC yellow cabs in real time — built with PySpark on Databricks and served via a Streamlit web app.

---

## 🖥️ Dashboard Preview

> Dark glassmorphism UI with live gauge, feature explainability, what-if analysis and model comparison.

---

## 🧠 How It Works

Input conditions like pickup hour, trip count, weather, and events are passed through trained ML models. The app returns a surge probability score (0–100%) along with a risk level and feature-level explainability.

---

## ⚙️ Tech Stack

| Layer | Tools |
|---|---|
| Data Processing | Apache Spark, PySpark |
| Model Training | Databricks Community Edition |
| ML Models | Logistic Regression, Decision Tree, Random Forest |
| Frontend | Streamlit, Plotly |
| Dataset | NYC Yellow Taxi 2025 |

---

## 🤖 Models

| Model | Accuracy | F1 Score |
|---|---|---|
| Logistic Regression | 96.90% | 0.909 |
| Decision Tree | 100% | 1.000 |
| Random Forest | 100% | 1.000 |

---

## 📊 Features

- **Live Surge Gauge** — probability meter with LOW / MEDIUM / HIGH risk levels
- **Feature Contribution** — bar chart showing how each input shifts the prediction
- **What-If Analysis** — simulate changes to trip count, rain, events in real time
- **Model Comparison** — compare all three models side by side on the same inputs
- **NYC Demand Map** — simulated heatmap of pickup demand across the city

---

## 🚀 Run Locally

```bash
# Clone the repo
git clone https://github.com/Yashwant1105/nyc-cab-surge-predictor.git
cd nyc-cab-surge-predictor

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

---

## 📁 Project Structure

```
nyc-cab-surge-predictor/
├── app.py                      # Streamlit dashboard
├── cab_surge_pred_final.ipynb  # PySpark model training (Databricks)
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 📓 Notebook

`cab_surge_pred_final.ipynb` contains the full ML pipeline run on Databricks Community Edition:
- Data cleaning & feature engineering
- StandardScaler preprocessing
- Training Logistic Regression, Decision Tree, Random Forest
- Model evaluation (accuracy, F1, confusion matrix)

---
