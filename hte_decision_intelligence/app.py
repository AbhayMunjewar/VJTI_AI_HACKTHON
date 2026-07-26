import os
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="HTE Decision Intelligence | State AI Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

from data.loader import load_hte_data, get_filtered_data
from utils.css_theme import inject_custom_css
from pages_modules.overview import render_overview_page
from pages_modules.trends import render_trends_page
from pages_modules.predictive import render_predictive_page
from pages_modules.ai_assistant import render_ai_assistant_page

def main():
    # Inject Custom Production-Grade CSS
    inject_custom_css()

    # Load Dataset
    df_raw = load_hte_data()

    # Sidebar Header & Brand
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 10px 0;">
        <h2 style="color: #00D2C4; font-size: 1.6rem; margin:0;">🎓 HTE Intelligence</h2>
        <p style="color: #94A3B8; font-size: 0.82rem; margin-top:2px;">State Decision Analytics Platform</p>
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("---")

    # Role Selector (Simulated Access Control)
    st.sidebar.markdown("##### 👤 Active Persona Role")
    user_role = st.sidebar.selectbox(
        "Select User Persona",
        ["State Official", "Institute Admin"],
        help="State Official views all districts; Institute Admin scopes to a single target institution."
    )

    if user_role == "Institute Admin":
        st.sidebar.markdown("""
        <div class="role-indicator">
            🏛️ Persona: Institute Administrator
        </div>
        """, unsafe_allow_html=True)
    else:
        st.sidebar.markdown("""
        <div class="role-indicator">
            👑 Persona: State HTE Official
        </div>
        """, unsafe_allow_html=True)

    st.sidebar.markdown("<br>", unsafe_allow_html=True)

    # Sidebar Navigation Menu
    st.sidebar.markdown("##### 🧭 Navigation")
    selected_page = st.sidebar.radio(
        "Select Module",
        [
            "📊 State Overview",
            "📉 Trend & Comparative Analytics",
            "🔮 Predictive Enrollment Modeling",
            "💬 AI Assistant (NL Query)"
        ],
        label_visibility="collapsed"
    )

    st.sidebar.markdown("---")

    # Global Data Filters
    st.sidebar.markdown("##### 🎛️ Filter Controls")

    available_districts = ["All"] + sorted(df_raw['district'].unique().tolist())
    available_institutes = ["All"] + sorted(df_raw['institute_name'].unique().tolist())
    available_depts = ["All"] + sorted(df_raw['department'].unique().tolist())

    if user_role == "State Official":
        sel_district = st.sidebar.selectbox("District Region", available_districts)
        # Filter institute dropdown options based on selected district
        if sel_district != "All":
            inst_options = ["All"] + sorted(df_raw[df_raw['district'] == sel_district]['institute_name'].unique().tolist())
        else:
            inst_options = available_institutes
        sel_institute = st.sidebar.selectbox("Institute Name", inst_options)
    else:
        # Institute Admin is pre-filtered to a specific institute
        sel_district = "All"
        inst_options = [i for i in available_institutes if i != "All"]
        sel_institute = st.sidebar.selectbox("Your Institute", inst_options)

    sel_dept = st.sidebar.selectbox("Academic Department", available_depts)

    min_yr, max_yr = int(df_raw['year'].min()), int(df_raw['year'].max())
    sel_years = st.sidebar.slider("Historical Period", min_value=min_yr, max_value=max_yr, value=(min_yr, max_yr))

    # Apply Filter Logic
    df_filtered = get_filtered_data(
        df_raw,
        role=user_role,
        selected_district=sel_district,
        selected_institute=sel_institute,
        selected_dept=sel_dept,
        year_range=sel_years
    )

    st.sidebar.markdown("---")

    # LLM Engine Status Indicator
    groq_key = os.environ.get("GROQ_API_KEY", "").strip()
    if groq_key:
        st.sidebar.success("⚡ Groq LLM (llama-3.3-70b): Connected")
    else:
        st.sidebar.info("💡 LLM Status: Smart Local Heuristics (GROQ_API_KEY optional)")

    st.sidebar.caption("HTE Decision Intelligence v1.0 • Hackathon Build")

    # Top Header Banner
    st.markdown("""
    <div class="dashboard-header">
        <h1 class="dashboard-title">HTE Decision Intelligence Platform</h1>
        <p class="dashboard-tagline">Transforming Higher & Technical Education data into actionable state governance intelligence.</p>
    </div>
    """, unsafe_allow_html=True)

    # Route to Selected Page
    if "📊 State Overview" in selected_page:
        render_overview_page(df_filtered)
    elif "📉 Trend & Comparative Analytics" in selected_page:
        render_trends_page(df_filtered)
    elif "🔮 Predictive Enrollment Modeling" in selected_page:
        render_predictive_page(df_filtered)
    elif "💬 AI Assistant" in selected_page:
        render_ai_assistant_page(df_filtered)

if __name__ == "__main__":
    main()
