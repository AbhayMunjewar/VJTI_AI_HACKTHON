# 🎓 HTE Decision Intelligence Dashboard

> **Transforming Institutional Data into Actionable Governance Intelligence.**

An AI-powered analytics and decision intelligence dashboard built for state Higher & Technical Education (HTE) departments. Features unified telemetry, predictive enrollment modeling with confidence intervals, role-based scoping, dynamic executive reporting, and a Groq-powered Natural Language Query assistant.

---

## 🌟 Key Features

1. **📊 Unified State Analytics & Executive Telemetry**:
   - High-level KPI cards for total enrollment, avg placement %, dropout rates, student-faculty ratios, and state funding.
   - Interactive macro charts powered by Plotly with regional and department breakdowns.

2. **🔮 Predictive Enrollment Modeling & Capacity Planning**:
   - Explainable scikit-learn polynomial trend forecaster predicting 3-year future enrollment trajectories (2025–2027).
   - Dynamic 95% confidence interval shaded bands.
   - AI-generated plain language explanations of key forecast drivers.

3. **💬 Natural Language Query AI Assistant**:
   - Plain-English chat interface powered by Groq LLM (`llama-3.3-70b-versatile`) translating queries into data operations.
   - Clickable suggestion prompt chips for live hackathon demos.
   - Renders natural-language answers alongside dynamic Plotly figures and data tables.

4. **🤖 AI Executive Insights Panel**:
   - Auto-generates 3-4 strategic policy findings whenever filters or datasets change.

5. **👤 Role-Based View Toggle**:
   - Lightweight persona switcher between **State Official** (state-wide governance view) and **Institute Admin** (institute-scoped view).

6. **📥 Executive Report Exporting**:
   - One-click export to PDF and Excel formats containing KPI summaries, insights, and filtered data.

---

## 🏗️ Architecture & Project Structure

```
hte_decision_intelligence/
├── .streamlit/
│   └── config.toml             # Dark navy dashboard theme configuration
├── data/
│   ├── generate_data.py        # Synthetic AISHE-compatible HTE dataset generator
│   ├── hte_data.csv            # Generated dataset (18 institutes, 5 departments, 2019-2024)
│   └── loader.py               # Cached data loading, filtering, and role-scoping layer
├── models/
│   └── forecaster.py           # Polynomial Ridge regression enrollment forecaster
├── llm/
│   ├── groq_client.py          # Groq API SDK wrapper with robust heuristic fallback
│   ├── nl_query.py             # Natural language text-to-pandas & visual generator
│   └── insights_generator.py   # AI executive insights & forecast driver narrative generator
├── utils/
│   ├── css_theme.py            # Custom CSS theme with glassmorphism & accent badges
│   └── export_utils.py         # PDF & Excel report exporter
├── pages_modules/
│   ├── overview.py             # Executive overview dashboard module
│   ├── trends.py               # Comparative & correlation analytics module
│   ├── predictive.py           # Predictive modeling & confidence bound module
│   └── ai_assistant.py         # Natural Language Query AI Assistant module
├── app.py                      # Main Streamlit application entry point
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation & design rationale
└── PITCH.md                    # Hackathon pitch outline, demo script & judge talking points
```

---

## 💡 Real-Data Compatibility Design Choice

> **Note on Data Architecture**: While synthetic data (`data/hte_data.csv`) is generated for demo reproducibility, `data/generate_data.py` and `data/loader.py` are strictly structured to match the standard schema of official AISHE (All India Survey on Higher Education) and state technical education datasets. Real state HTE CSV or database tables can be swapped directly into `data/loader.py` with zero code modifications.

---

## 🚀 Quickstart & Local Installation

### Prerequisites
- Python 3.9+
- (Optional) Groq API Key for LLM-powered natural language queries.

### 1. Clone & Navigate
```bash
cd hte_decision_intelligence
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set API Key (Optional)
Set your `GROQ_API_KEY` environment variable for live Groq LLM query processing. If not provided, the system automatically degrades gracefully to built-in smart local heuristics.

**Windows PowerShell**:
```powershell
$env:GROQ_API_KEY="your_groq_api_key_here"
```

**Linux / macOS**:
```bash
export GROQ_API_KEY="your_groq_api_key_here"
```

### 4. Launch Application
```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`.

---

## 🛣️ Future Roadmap

1. **GIS Spatial Mapping**: Incorporate Leaflet/Mapbox geospatial heatmaps for district-level physical infrastructure tracking.
2. **Automated Dropout Early Warning**: Implement classification model predicting individual student risk based on attendance and mid-term grades.
3. **Database Integration**: Connect directly to PostgreSQL / Snowflake for live streaming state data integration.
