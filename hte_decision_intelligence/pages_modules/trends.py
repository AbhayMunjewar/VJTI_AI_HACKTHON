import time
import streamlit as st
import plotly.express as px
import pandas as pd

def render_trends_page(df_filtered):
    st.markdown("### 📉 Comparative & Correlation Analytics")

    # Real-time simulation toggle
    top_c1, top_c2 = st.columns([3, 1])
    with top_c2:
        auto_refresh = st.toggle("🔄 Live Telemetry Stream", value=False)
        if auto_refresh:
            st.caption("⚡ Live updates active (2s interval)")

    if auto_refresh:
        time.sleep(0.5)

    palette = ["#00D2C4", "#FFC72C", "#FF6B6B", "#4A90E2", "#9B51E0", "#2ECC71"]

    # Row 1: Institutional Comparison & District Ranking
    r1_col1, r1_col2 = st.columns(2)

    with r1_col1:
        st.markdown("#### 🏛️ Top 10 Institutes by Placement Rate (%)")
        if not df_filtered.empty:
            inst_rank = df_filtered.groupby('institute_name')['placement_pct'].mean().reset_index()
            inst_rank = inst_rank.sort_values('placement_pct', ascending=True).tail(10)
            
            fig_bar = px.bar(
                inst_rank, y="institute_name", x="placement_pct", orientation="h",
                color="placement_pct", template="plotly_dark",
                color_continuous_scale="Viridis"
            )
            fig_bar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                xaxis_title="Avg Placement %", yaxis_title=""
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    with r1_col2:
        st.markdown("#### 📍 District-wise Funding Allocation & Enrollment")
        if not df_filtered.empty:
            dist_summary = df_filtered.groupby('district').agg({
                'funding_lakhs': 'sum',
                'enrollment': 'sum',
                'dropout_pct': 'mean'
            }).reset_index()

            fig_bubble = px.scatter(
                dist_summary, x="funding_lakhs", y="enrollment",
                size="enrollment", color="dropout_pct", text="district",
                template="plotly_dark", color_continuous_scale="Reds",
                title="District Funding vs Enrollment (Color = Dropout %)"
            )
            fig_bubble.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig_bubble, use_container_width=True)

    st.markdown("---")

    # Row 2: Deep Correlations
    st.markdown("#### 🔬 Institutional Health & Infrastructure Correlations")
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("##### Infrastructure Score vs Placement Rate")
        if not df_filtered.empty:
            fig_corr1 = px.scatter(
                df_filtered, x="infrastructure_score", y="placement_pct",
                color="department", trendline="ols",
                template="plotly_dark", color_discrete_sequence=palette
            )
            fig_corr1.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig_corr1, use_container_width=True)

    with c2:
        st.markdown("##### Student-Faculty Ratio vs Dropout Rate")
        if not df_filtered.empty:
            fig_corr2 = px.scatter(
                df_filtered, x="student_faculty_ratio", y="dropout_pct",
                color="district", trendline="ols",
                template="plotly_dark", color_discrete_sequence=palette
            )
            fig_corr2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig_corr2, use_container_width=True)
