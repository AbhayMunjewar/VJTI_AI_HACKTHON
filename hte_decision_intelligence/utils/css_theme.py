import streamlit as st

def inject_custom_css():
    """
    Injects custom production-grade CSS styles for a stunning dark-mode dashboard aesthetic.
    Features glassmorphism cards, glowing accent borders, gold/teal badges, and responsive typography.
    """
    css = """
    <style>
    /* Global Container Styles */
    .stApp {
        background: linear-gradient(135deg, #0E1117 0%, #161B26 50%, #0E1117 100%);
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }

    /* Top Banner / Header Card */
    .dashboard-header {
        background: linear-gradient(90deg, rgba(26,31,44,0.9) 0%, rgba(14,17,23,0.95) 100%);
        border: 1px solid rgba(0, 210, 196, 0.25);
        border-radius: 12px;
        padding: 20px 28px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(8px);
    }
    
    .dashboard-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #F0F2F5 0%, #00D2C4 50%, #FFC72C 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        letter-spacing: -0.5px;
    }

    .dashboard-tagline {
        color: #94A3B8;
        font-size: 1.0rem;
        margin-top: 4px;
        font-weight: 400;
    }

    /* Glassmorphism Metric Cards */
    .kpi-card {
        background: rgba(26, 31, 44, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 18px 20px;
        text-align: left;
        box-shadow: 0 4px 20px rgba(0,0,0,0.25);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        border-color: rgba(0, 210, 196, 0.4);
    }
    .kpi-label {
        font-size: 0.82rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        font-weight: 600;
    }
    .kpi-value {
        font-size: 1.85rem;
        font-weight: 700;
        color: #F0F2F5;
        margin: 6px 0 2px 0;
    }
    .kpi-badge {
        display: inline-block;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 12px;
    }
    .kpi-badge-teal { background: rgba(0, 210, 196, 0.15); color: #00D2C4; border: 1px solid rgba(0, 210, 196, 0.3); }
    .kpi-badge-gold { background: rgba(255, 199, 44, 0.15); color: #FFC72C; border: 1px solid rgba(255, 199, 44, 0.3); }
    .kpi-badge-coral { background: rgba(255, 107, 107, 0.15); color: #FF6B6B; border: 1px solid rgba(255, 107, 107, 0.3); }

    /* AI Insights Container */
    .ai-insights-box {
        background: linear-gradient(135deg, rgba(0, 210, 196, 0.06) 0%, rgba(26, 31, 44, 0.85) 100%);
        border: 1px solid rgba(0, 210, 196, 0.3);
        border-radius: 12px;
        padding: 20px;
        margin: 16px 0 24px 0;
    }
    .ai-insights-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #00D2C4;
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 12px;
    }
    .ai-insight-item {
        color: #E2E8F0;
        font-size: 0.95rem;
        line-height: 1.5;
        margin-bottom: 8px;
    }

    /* Role Badge Indicator */
    .role-indicator {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255, 199, 44, 0.1);
        color: #FFC72C;
        border: 1px solid rgba(255, 199, 44, 0.3);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }

    /* Sidebar Clean Styling */
    section[data-testid="stSidebar"] {
        background-color: #131722 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Streamlit Buttons Custom Accent */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        border-color: #00D2C4;
        color: #00D2C4;
        box-shadow: 0 0 12px rgba(0, 210, 196, 0.3);
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
