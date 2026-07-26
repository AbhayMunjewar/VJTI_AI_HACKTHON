import os
import pandas as pd
import streamlit as st

DATA_FILE_PATH = os.path.join(os.path.dirname(__file__), "hte_data.csv")

@st.cache_data(ttl=3600)
def load_hte_data():
    """
    Loads and caches the state HTE dataset.
    If hte_data.csv does not exist, triggers automatic generation.
    Designed to be schema-compatible with official AISHE dataset imports.
    """
    if not os.path.exists(DATA_FILE_PATH):
        from data.generate_data import generate_hte_dataset
        generate_hte_dataset(DATA_FILE_PATH)

    df = pd.read_csv(DATA_FILE_PATH)
    # Ensure standard types
    df['year'] = df['year'].astype(int)
    df['enrollment'] = df['enrollment'].astype(int)
    df['seats_available'] = df['seats_available'].astype(int)
    df['faculty_count'] = df['faculty_count'].astype(int)
    df['placement_pct'] = df['placement_pct'].astype(float)
    df['dropout_pct'] = df['dropout_pct'].astype(float)
    df['student_faculty_ratio'] = df['student_faculty_ratio'].astype(float)
    df['avg_package_lpa'] = df['avg_package_lpa'].astype(float)
    df['infrastructure_score'] = df['infrastructure_score'].astype(float)
    df['funding_lakhs'] = df['funding_lakhs'].astype(float)
    return df

def get_filtered_data(df, role="State Official", selected_district="All", selected_institute="All", selected_dept="All", year_range=(2019, 2024)):
    """
    Applies role-based scoping and user filter selection.
    - State Official: Full view access across districts & institutes
    - Institute Admin: Scope locked to the selected target institute
    """
    filtered = df.copy()

    # Apply year filter
    filtered = filtered[(filtered['year'] >= year_range[0]) & (filtered['year'] <= year_range[1])]

    # Apply role scoping or institute filter
    if role == "Institute Admin":
        if selected_institute != "All":
            filtered = filtered[filtered['institute_name'] == selected_institute]
        else:
            # Default to first institute for admin role if not specifically picked
            default_inst = filtered['institute_name'].iloc[0] if not filtered.empty else ""
            filtered = filtered[filtered['institute_name'] == default_inst]
    else:
        # State Official Role
        if selected_district != "All":
            filtered = filtered[filtered['district'] == selected_district]
        if selected_institute != "All":
            filtered = filtered[filtered['institute_name'] == selected_institute]

    # Department filter
    if selected_dept != "All":
        filtered = filtered[filtered['department'] == selected_dept]

    return filtered

def get_kpi_metrics(filtered_df):
    """
    Computes key summary performance metrics for KPI cards.
    """
    if filtered_df.empty:
        return {
            "total_enrollment": 0,
            "avg_placement": 0.0,
            "avg_dropout": 0.0,
            "total_institutes": 0,
            "total_funding": 0.0,
            "avg_ratio": 0.0
        }

    latest_year = filtered_df['year'].max()
    latest_df = filtered_df[filtered_df['year'] == latest_year]

    return {
        "total_enrollment": int(latest_df['enrollment'].sum()),
        "avg_placement": round(float(latest_df['placement_pct'].mean()), 1),
        "avg_dropout": round(float(latest_df['dropout_pct'].mean()), 1),
        "total_institutes": int(filtered_df['institute_id'].nunique()),
        "total_funding": round(float(latest_df['funding_lakhs'].sum()), 1),
        "avg_ratio": round(float(latest_df['student_faculty_ratio'].mean()), 1)
    }
