import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from models.forecaster import forecast_enrollment
from llm.insights_generator import generate_forecast_explanation
from utils.export_utils import generate_pdf_report, generate_excel_report

def render_predictive_page(df):
    st.markdown("### 🔮 Predictive Enrollment Modeling & Capacity Planning")
    st.markdown("Scikit-learn Polynomial Trend Forecasting with dynamic confidence intervals (2025–2027).")

    if df.empty:
        st.warning("No data available for forecasting.")
        return

    # Selectors for forecasting scope
    c1, c2, c3 = st.columns(3)

    with c1:
        institutes = ["All Institutes"] + sorted(df['institute_name'].unique().tolist())
        selected_inst = st.selectbox("Select Target Institute", institutes)

    with c2:
        departments = ["All Departments"] + sorted(df['department'].unique().tolist())
        selected_dept = st.selectbox("Select Target Department", departments)

    with c3:
        horizon = st.slider("Forecast Horizon (Years)", min_value=1, max_value=4, value=3)

    # Filter dataframe slice for model
    df_slice = df.copy()
    if selected_inst != "All Institutes":
        df_slice = df_slice[df_slice['institute_name'] == selected_inst]
    if selected_dept != "All Departments":
        df_slice = df_slice[df_slice['department'] == selected_dept]

    entity_name = f"{selected_inst} - {selected_dept}" if selected_inst != "All Institutes" or selected_dept != "All Departments" else "State Total"

    # Fit Model & Predict
    forecast_df, metrics = forecast_enrollment(df_slice, horizon_years=horizon)

    if forecast_df.empty:
        st.error("Insufficient data points to build regression forecast.")
        return

    # Render Metric Cards
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Overall Trajectory", metrics.get("trend_direction", "N/A"))
    with m2:
        st.metric("3-Yr Projected Growth", f"{metrics.get('forecast_growth_pct', 0.0):+.1f}%")
    with m3:
        st.metric("Model R² Confidence", f"{metrics.get('r2_score', 0.0):.3f}")
    with m4:
        st.metric("2027 Projected Cohort", f"{metrics.get('forecast_2027', 0):,.0f}")

    st.markdown("<br>", unsafe_allow_html=True)

    # Render Forecast Chart with Shaded Confidence Band
    fig = go.Figure()

    hist_data = forecast_df[forecast_df['type'] == 'Historical Actual']
    fc_data = forecast_df[forecast_df['type'] == 'AI Forecast']

    # Historical Line
    fig.add_trace(go.Scatter(
        x=hist_data['year'], y=hist_data['enrollment'],
        mode='lines+markers', name='Historical Actual',
        line=dict(color='#00D2C4', width=3),
        marker=dict(size=8)
    ))

    # Forecast Line
    # Bridge transition from last actual point to first forecast
    bridge_x = [hist_data['year'].iloc[-1]] + list(fc_data['year'])
    bridge_y = [hist_data['enrollment'].iloc[-1]] + list(fc_data['enrollment'])
    bridge_lower = [hist_data['enrollment'].iloc[-1]] + list(fc_data['lower_bound'])
    bridge_upper = [hist_data['enrollment'].iloc[-1]] + list(fc_data['upper_bound'])

    fig.add_trace(go.Scatter(
        x=bridge_x, y=bridge_y,
        mode='lines+markers', name='AI Forecast (2025-2027)',
        line=dict(color='#FFC72C', width=3, dash='dash'),
        marker=dict(size=9, symbol='diamond')
    ))

    # Upper Confidence Band
    fig.add_trace(go.Scatter(
        x=bridge_x, y=bridge_upper,
        mode='lines', name='Upper Confidence Band (95%)',
        line=dict(width=0), showlegend=False
    ))

    # Lower Confidence Band with Fill
    fig.add_trace(go.Scatter(
        x=bridge_x, y=bridge_lower,
        mode='lines', name='95% Confidence Interval',
        fill='tonexty', fillcolor='rgba(255, 199, 44, 0.15)',
        line=dict(width=0)
    ))

    fig.update_layout(
        title=f"Enrollment Forecast & Projection Bounds: {entity_name}",
        xaxis_title="Academic Year",
        yaxis_title="Total Enrollment",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig, use_container_width=True)

    # AI Forecast Drivers Explanation
    st.markdown("""
    <div class="ai-insights-box">
        <div class="ai-insights-title">🧠 AI Strategic Forecast Driver Analysis</div>
    """, unsafe_allow_html=True)

    with st.spinner("Generating AI forecast rationale..."):
        explanation = generate_forecast_explanation(entity_name, forecast_df, metrics)

    st.markdown(explanation)
    st.markdown("</div>", unsafe_allow_html=True)

    # Forecast Data Table & Export
    st.markdown("#### 📋 Forecasted Data Table")
    st.dataframe(forecast_df, use_container_width=True)
