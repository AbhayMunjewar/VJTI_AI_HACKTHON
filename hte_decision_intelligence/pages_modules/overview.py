import streamlit as st
import plotly.express as px
import pandas as pd
from data.loader import get_kpi_metrics
from llm.insights_generator import generate_ai_insights
from utils.export_utils import generate_excel_report, generate_pdf_report

def render_overview_page(df_filtered):
    st.markdown("### 📊 State Overview & Executive Telemetry")

    kpis = get_kpi_metrics(df_filtered)

    # Render KPI Cards in Columns
    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Total Enrollment</div>
            <div class="kpi-value">{kpis['total_enrollment']:,}</div>
            <span class="kpi-badge kpi-badge-teal">Active Students</span>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Avg Placement Rate</div>
            <div class="kpi-value">{kpis['avg_placement']:.1f}%</div>
            <span class="kpi-badge kpi-badge-gold">Industry Ready</span>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Avg Dropout Rate</div>
            <div class="kpi-value">{kpis['avg_dropout']:.1f}%</div>
            <span class="kpi-badge kpi-badge-coral">Retention Risk</span>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Student-Faculty Ratio</div>
            <div class="kpi-value">{kpis['avg_ratio']:.1f}</div>
            <span class="kpi-badge kpi-badge-teal">Faculty Norms</span>
        </div>
        """, unsafe_allow_html=True)

    with c5:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Total State Funding</div>
            <div class="kpi-value">₹{kpis['total_funding']:,.0f}L</div>
            <span class="kpi-badge kpi-badge-gold">Annual Budget</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # AI Insights Panel
    st.markdown("""
    <div class="ai-insights-box">
        <div class="ai-insights-title">🤖 AI Executive Decision Insights</div>
    """, unsafe_allow_html=True)
    
    with st.spinner("Analyzing current filter slice with Groq AI..."):
        insights = generate_ai_insights(df_filtered)

    for item in insights:
        st.markdown(f'<div class="ai-insight-item">{item}</div>', unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

    # Macro Charts
    col_left, col_right = st.columns(2)

    palette = ["#00D2C4", "#FFC72C", "#FF6B6B", "#4A90E2", "#9B51E0"]

    with col_left:
        st.markdown("#### 📈 Enrollment Trend by Department (2019-2024)")
        if not df_filtered.empty:
            yearly_dept = df_filtered.groupby(['year', 'department'])['enrollment'].sum().reset_index()
            fig1 = px.line(
                yearly_dept, x="year", y="enrollment", color="department",
                markers=True, template="plotly_dark", color_discrete_sequence=palette
            )
            fig1.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig1, use_container_width=True)

    with col_right:
        st.markdown("#### 🎯 Placement % vs Student-Faculty Ratio")
        if not df_filtered.empty:
            latest_year = df_filtered['year'].max()
            latest_df = df_filtered[df_filtered['year'] == latest_year]
            fig2 = px.scatter(
                latest_df, x="student_faculty_ratio", y="placement_pct",
                color="department", size="enrollment", hover_data=["institute_name", "district"],
                template="plotly_dark", color_discrete_sequence=palette
            )
            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # Export Report Section
    st.markdown("#### 📥 Export Decision Report")
    exp_c1, exp_c2, _ = st.columns([1, 1, 2])

    excel_bytes = generate_excel_report("Executive Summary", kpis, insights, df_filtered)
    pdf_bytes = generate_pdf_report("Executive Summary", kpis, insights, df_filtered)

    with exp_c1:
        st.download_button(
            label="📊 Download Excel Report",
            data=excel_bytes,
            file_name="HTE_Executive_Report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    with exp_c2:
        st.download_button(
            label="📄 Download PDF Summary",
            data=pdf_bytes,
            file_name="HTE_Executive_Report.pdf",
            mime="application/pdf",
            use_container_width=True
        )
